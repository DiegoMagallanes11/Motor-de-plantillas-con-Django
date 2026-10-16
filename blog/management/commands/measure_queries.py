import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from blog.duel.verifier import measure_front_page


class Command(BaseCommand):
    help = "Measure the same rendering workload before and after optimization."

    def add_arguments(self, parser):
        parser.add_argument("--output")

    def handle(self, *args, **options):
        result = measure_front_page()
        self.stdout.write(
            f"Antes: {result['before']['queries']} consultas; "
            f"después: {result['after']['queries']} consultas; "
            f"artículos: {result['after']['rows']}; "
            f"mismo contenido: {result['same_payload']}"
        )
        if options["output"]:
            Path(options["output"]).write_text(
                json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        if not result["same_payload"]:
            raise CommandError("The optimization changed the rendered content.")
