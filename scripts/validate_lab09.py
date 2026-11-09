"""Validate the hand-in against immutable teacher sources and saved evidence."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parent.parent
STARTER = ROOT / ".private/lab09-starter"
FRONTEND = ROOT / "frontend"
EVIDENCE = ROOT / "deliverables/lab09/evidence"
checks = {}

for relative in ["src/data/movies.js", "src/data/movies.test.js", "src/duel/support.js"]:
    assert (STARTER / relative).read_bytes() == (FRONTEND / relative).read_bytes()
for folder in ["src/duel/tests", "src/duel/ai"]:
    for source in (STARTER / folder).glob("*.jsx"):
        assert source.read_bytes() == (FRONTEND / folder / source.name).read_bytes()
checks["teacher_data_tests_and_ai_unchanged"] = True

browser = json.loads((EVIDENCE / "browser-results.json").read_text(encoding="utf-8"))
assert len(browser["checks"]) == 22
assert all(row["passed"] for row in browser["checks"])
assert browser["consoleErrors"] == []
assert browser["restoredSource"]
assert browser["unsafeExperiment"] == {"flag": 1, "injectedImages": 2}
checks["browser_checks"] = len(browser["checks"])

components = ["Header", "Footer", "Hero", "MovieCard", "MovieList", "Showtimes", "Synopsis", "AgentMessage"]
for component in components:
    base = FRONTEND / "src/components" / component
    assert (base / f"{component}.jsx").is_file()
    assert (base / f"{component}.css").is_file()
    assert "useState" not in (base / f"{component}.jsx").read_text(encoding="utf-8")
assert "dangerouslySetInnerHTML" not in (FRONTEND / "src/components/Synopsis/Synopsis.jsx").read_text(encoding="utf-8")
checks["eight_component_folders_and_safe_synopsis"] = True

for name, count in [("04-team-green.txt", 43), ("05-fixed-green.txt", 43), ("09-final-restored-tests.txt", 47)]:
    text = (EVIDENCE / name).read_text(encoding="utf-8")
    assert f"{count} passed" in text
checks["recorded_team_fixed_and_full_tests"] = [43, 43, 47]

source_guide = ROOT / "deliverables/lab09/guia-referencia.txt"
word = ROOT / "deliverables/lab09/Lab09_Diego_Magallanes_Linares.docx"
with ZipFile(word) as package:
    text_parts = b"".join(package.read(name) for name in package.namelist() if name.endswith(".xml"))
    assert b"Conclusiones" in text_parts
    assert b"Django REST Framework" not in text_parts
checks["word_and_reference_sha256"] = {
    "word": hashlib.sha256(word.read_bytes()).hexdigest(),
    "reference": hashlib.sha256(source_guide.read_bytes()).hexdigest(),
}
private_tokens = ROOT / ".private/quiz_tokens.json"
if private_tokens.exists():
    tokens = json.loads(private_tokens.read_text())
    public_files = list((ROOT / "deliverables/lab09").rglob("*"))
    public_files.extend([ROOT / "LAB09.md", ROOT / "README.md"])
    public_files.extend(path for path in (FRONTEND / "src").rglob("*") if path.is_file())
    for path in public_files:
        if path.is_file():
            data = text_parts if path == word else path.read_bytes()
            assert all(token.encode() not in data for token in tokens.values())
checks["local_tokens_absent"] = True
(EVIDENCE / "delivery-checks.json").write_text(json.dumps(checks, indent=2), encoding="utf-8")
print(json.dumps({"validated": True, "checks": list(checks)}, indent=2))
