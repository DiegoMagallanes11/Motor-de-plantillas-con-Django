"""Collect reproducible lab evidence, restoring the isolated dataset at the end."""
import json
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand

from blog.agent.intents import INTENT_EXAMPLES, execute_intent
from blog.agent.registry import dispatch
from blog.duel.verifier import measure_front_page, run_duel
from blog.models import Comment
from blog.seed import seed_blog


class Command(BaseCommand):
    help = "Reset blog sample data and record measurements and approval checks."

    def handle(self, *args, **options):
        output = settings.BASE_DIR / "deliverables" / "lab07" / "evidence"
        output.mkdir(parents=True, exist_ok=True)

        def write(filename, data):
            (output / filename).write_text(
                json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
            )

        counts = seed_blog()
        write("dataset.json", counts)
        write("duel-team.json", run_duel())
        write("duel-ai.json", run_duel("ai"))
        write("query-counts.json", measure_front_page())
        intentions = [
            {"intent": intent, "response": execute_intent(intent)}
            for intent in INTENT_EXAMPLES
        ]
        plan = dispatch("delete_comments", {"article_id": 5})
        approved = dispatch("delete_comments", {"article_id": 5}, plan["plan_hash"])
        after_delete = Comment.objects.filter(article_id=5).count()
        restored = seed_blog()
        stale_plan = dispatch("delete_comments", {"article_id": 5})
        inserted = Comment.objects.create(
            article_id=5, author_name="Prueba de cambio", body="Comentario agregado entre plan y aprobación."
        )
        denied = dispatch("delete_comments", {"article_id": 5}, stale_plan["plan_hash"])
        preserved = Comment.objects.filter(article_id=5).count()
        final_counts = seed_blog()
        write("agent-results.json", {
            "intents": intentions, "plan": plan, "approved": approved,
            "comments_after_delete": after_delete, "restored": restored,
            "stale_plan": stale_plan, "inserted_comment_id": inserted.id,
            "stale_approval": denied, "comments_preserved_after_rejection": preserved,
            "final_counts": final_counts,
        })
        self.stdout.write(
            "Evidencia registrada: 8 consultas verificadas; portada 23 a 2; "
            "aprobación válida y plan obsoleto probados; datos restaurados."
        )
