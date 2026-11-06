"""Exercise the running API through curl and the supplied headless clients."""
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent.gateway import execute
import quizctl

OUT = ROOT / "deliverables" / "lab08" / "evidence"
PRIVATE = ROOT / ".private"
BASE = os.environ.get("QUIZ_URL", "http://127.0.0.1:8008")
TOKENS = json.loads((PRIVATE / "quiz_tokens.json").read_text())
records = []


def call(label, method, path, body=None, expected=200, role="human"):
    config = PRIVATE / "curl-lab08.cfg"
    config.write_text(
        'header = "Accept: application/json"\n'
        'header = "Content-Type: application/json"\n'
        + (f'header = "Authorization: Token {TOKENS[role]}"\n' if role else ""),
        encoding="utf-8",
    )
    command = ["curl.exe", "--silent", "--show-error", "--config", str(config),
               "--request", method, BASE + path, "--write-out", "\n%{http_code}"]
    if body is not None:
        payload = PRIVATE / "curl-lab08-body.json"
        payload.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
        command += ["--data-binary", "@" + str(payload)]
    result = subprocess.run(command, capture_output=True, check=True)
    raw, status = result.stdout.decode("utf-8").rsplit("\n", 1)
    data = json.loads(raw) if raw else None
    row = {"label": label, "method": method, "path": path, "role": role,
           "body": body, "expected": expected, "status": int(status), "response": data}
    records.append(row)
    if int(status) != expected:
        raise AssertionError(f"{label}: {status} expected {expected}: {data}")
    return data


def main():
    initial = call("initial questions", "GET", "/api/questions/")
    exam = call("create exam", "POST", "/api/exams/", {"title": "HTTP Lab08"}, 201)
    eid = exam["id"]
    call("list exams", "GET", "/api/exams/")
    call("retrieve exam", "GET", f"/api/exams/{eid}/")
    call("patch exam", "PATCH", f"/api/exams/{eid}/", {"title": "HTTP Lab08 actualizado"})
    body = {"exam": eid, "text": "¿Qué es REST?", "choices": [
        {"text": "Un estilo", "is_correct": True},
        {"text": "Un lenguaje", "is_correct": False},
    ]}
    question = call("create question", "POST", "/api/questions/", body, 201)
    qid = question["id"]
    call("list questions", "GET", "/api/questions/")
    call("retrieve question", "GET", f"/api/questions/{qid}/")
    call("patch question", "PATCH", f"/api/questions/{qid}/", {"text": "REST sobre HTTP"})
    choice = call("create choice", "POST", "/api/choices/", {
        "question": qid, "text": "Un sistema operativo", "is_correct": False,
    }, 201)
    cid = choice["id"]
    call("list choices", "GET", "/api/choices/")
    call("retrieve choice", "GET", f"/api/choices/{cid}/")
    call("patch choice", "PATCH", f"/api/choices/{cid}/", {"text": "Un compilador"})
    call("invalid correct choice", "POST", "/api/choices/", {
        "question": qid, "text": "Otra correcta", "is_correct": True,
    }, 400)
    for label, invalid in [
        ("missing required field", {k: v for k, v in body.items() if k != "text"}),
        ("wrong type", {**body, "exam": "no-es-un-numero"}),
        ("two correct choices", {**body, "choices": [
            {"text": "a", "is_correct": True}, {"text": "b", "is_correct": True}]}),
    ]:
        call(label, "POST", "/api/questions/", invalid, 400)
    call("no authentication", "GET", "/api/exams/", expected=401, role=None)
    call("agent forbidden delete", "DELETE", f"/api/questions/{qid}/", expected=403, role="agent")
    call("delete choice", "DELETE", f"/api/choices/{cid}/", expected=204)
    call("deleted choice", "GET", f"/api/choices/{cid}/", expected=404)
    call("delete question", "DELETE", f"/api/questions/{qid}/", expected=204)
    call("deleted question", "GET", f"/api/questions/{qid}/", expected=404)
    call("delete exam", "DELETE", f"/api/exams/{eid}/", expected=204)
    call("deleted exam", "GET", f"/api/exams/{eid}/", expected=404)
    page1 = call("pagination first page", "GET", "/api/questions/?page=1")
    page2 = call("pagination second page", "GET", "/api/questions/?page=2")
    assert (page1["count"], len(page1["results"]), len(page2["results"])) == (8, 5, 3)
    seed_exam = page1["results"][0]["exam"]
    filtered = call("filter by exam", "GET", f"/api/questions/?exam={seed_exam}")
    searched = call("search text", "GET", "/api/questions/?search=prefetch_related")
    assert filtered["count"] == 4 and searched["count"] == 1
    call("invalid filter", "GET", "/api/questions/?exam=no", expected=400)
    final = call("final questions", "GET", "/api/questions/")
    assert initial == final
    (OUT / "http-results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    audit = OUT / "agent-audit.jsonl"
    if audit.exists():
        audit.unlink()
    intents = [
        {"op": "exams_list"}, {"op": "questions_list", "query": {"search": "prefetch"}},
        {"op": "exams_destroy", "path": {"id": seed_exam}},
        "Exam.objects.all().delete()", {"op": "run_sql"},
    ]
    actions = []
    for intent in intents:
        result = execute(intent, base_url=BASE, agent_token=TOKENS["agent"], audit_path=audit)
        actions.append({"intent": intent, "result": result})
    assert [r["result"]["status"] for r in actions] == ["ok", "ok", "approval_required", "denied", "denied"]
    temp = call("gateway temporary target", "POST", "/api/questions/", {
        **body, "exam": seed_exam, "text": "Objetivo temporal del plan",
    }, 201)
    intent = {"op": "questions_destroy", "path": {"id": temp["id"]}}
    def gateway(**kwargs):
        return execute(intent, base_url=BASE, agent_token=TOKENS["agent"], audit_path=audit, **kwargs)
    plan = gateway()
    call("change gateway target", "PATCH", f"/api/questions/{temp['id']}/", {"text": "Objetivo cambiado"})
    stale = gateway(approval=plan["plan"]["plan_hash"], human_token=TOKENS["human"])
    no_human = gateway(approval=stale["plan"]["plan_hash"])
    wrong_identity = gateway(approval=stale["plan"]["plan_hash"], human_token=TOKENS["agent"])
    applied = gateway(approval=stale["plan"]["plan_hash"], human_token=TOKENS["human"])
    assert (stale["status"], no_human["status"], wrong_identity["http"], applied["http"]) == ("approval_required", "denied", 403, 204)
    (OUT / "agent-results.json").write_text(json.dumps({"intents": actions, "plan": plan,
        "stale": stale, "no_human": no_human, "agent_cannot_approve": wrong_identity,
        "applied": applied}, ensure_ascii=False, indent=2), encoding="utf-8")
    import io
    cli_results = []
    for argv in [["--json", "exams", "list"], ["--json", "questions", "list", "--search", "prefetch_related"],
                 ["--dry-run", "questions", "delete", "99999"], ["ops"], ["questions", "get", "99999"]]:
        output = io.StringIO()
        status = quizctl.main(argv, env={"QUIZ_URL": BASE, "QUIZ_TOKEN": TOKENS["human"]}, out=output)
        cli_results.append({"argv": argv, "exit": status, "output": output.getvalue()})
    (OUT / "cli-results.json").write_text(json.dumps(cli_results, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT / "http-results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    assert call("restored question count", "GET", "/api/questions/")["count"] == 8
    (OUT / "http-results.json").write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    config = PRIVATE / "curl-lab08.cfg"
    config.unlink()
    print(f"Verified {len(records)} curl requests; five operations per resource, errors, filters, client and gateway.")


if __name__ == "__main__":
    main()
