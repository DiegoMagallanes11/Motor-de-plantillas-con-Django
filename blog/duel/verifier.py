"""Compare evaluated QuerySets against fixed answer keys and measured budgets."""
from django.db import connection
from django.db.models import QuerySet
from django.test.utils import CaptureQueriesContext

from blog.queries import front_page, front_page_naive, render_front_page

from . import ai, team
from .questions import QUESTIONS

CLASSIFICATIONS = {
    1: "borde temporal excluido", 2: "campo inventado",
    3: "significado de la pregunta", 4: "duplicados por relación inversa",
    5: "conteos multiplicados", 6: "significado de ninguno",
    7: "conteo de borradores", 8: "correcta pero cara",
}


def serialize(number, queryset):
    if not isinstance(queryset, QuerySet):
        raise TypeError("Each solution must return a QuerySet")
    if number == 5:
        return [[item.id, item.n_comments, item.n_tags] for item in queryset]
    if number == 7:
        return [[item.id, item.n_articles] for item in queryset]
    if number == 8:
        return [row["id"] for row in render_front_page(queryset)]
    return [item.id for item in queryset]


def run_duel(source="team"):
    module = {"team": team, "ai": ai}[source]
    results = []
    for question in QUESTIONS:
        number = question["number"]
        actual = None
        error = None
        sql = None
        with CaptureQueriesContext(connection) as captured:
            try:
                queryset = getattr(module, f"question_{number}")()
                sql = str(queryset.query)
                actual = serialize(number, queryset)
            except Exception as exception:
                # Report candidate failures without executing generated strings.
                error = f"{type(exception).__name__}: {exception}"
        if error:
            status = "error"
        elif actual != question["expected"]:
            status = "wrong_result"
        elif len(captured) > question["budget"]:
            status = "expensive"
        else:
            status = "accepted"
        results.append({
            "number": number, "question": question["text"],
            "status": status, "actual": actual, "expected": question["expected"],
            "queries": len(captured), "budget": question["budget"],
            "classification": CLASSIFICATIONS[number] if status != "accepted" else "correcta",
            "error": error, "sql": sql,
            "captured_sql": [item["sql"] for item in captured.captured_queries],
        })
    return results


def measure_front_page():
    measurements = {}
    for label, query in (("before", front_page_naive), ("after", front_page)):
        with CaptureQueriesContext(connection) as captured:
            payload = render_front_page(query())
        measurements[label] = {
            "queries": len(captured), "rows": len(payload), "payload": payload,
            "sql": [item["sql"] for item in captured.captured_queries],
        }
    measurements["same_payload"] = (
        measurements["before"]["payload"] == measurements["after"]["payload"]
    )
    return measurements
