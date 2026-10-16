from django.shortcuts import render
from django.views.decorators.http import require_GET

from .agent.intents import INTENT_EXAMPLES, execute_intent
from .duel.verifier import measure_front_page, run_duel
from .models import Article, Author, Category, Comment, Profile, Tag


@require_GET
def dashboard(request):
    verified = run_duel("team")
    candidates = run_duel("ai")
    comparisons = [
        {"reference": reference, "candidate": candidate}
        for reference, candidate in zip(verified, candidates)
    ]
    measurement = measure_front_page()
    intents = [
        {"text": intent, "status": execute_intent(intent)["status"]}
        for intent in INTENT_EXAMPLES
    ]
    comments = execute_intent(INTENT_EXAMPLES[1]).get("data", [])
    return render(request, "blog/dashboard.html", {
        "comparisons": comparisons,
        "measurement": measurement,
        "intents": intents,
        "injected_comment": comments[3] if len(comments) >= 4 else None,
        "counts": {
            "Autores": Author.objects.count(), "Perfiles": Profile.objects.count(),
            "Artículos": Article.objects.count(), "Categorías": Category.objects.count(),
            "Etiquetas": Tag.objects.count(), "Comentarios": Comment.objects.count(),
        },
        "accepted_count": sum(row["status"] == "accepted" for row in verified),
    })
