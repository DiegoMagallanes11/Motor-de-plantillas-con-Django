import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from blog.duel.verifier import run_duel


class Command(BaseCommand):
    help = "Verify the eight adapted ORM exercises, including query budgets."

    def add_arguments(self, parser):
        parser.add_argument("--source", choices=("team", "ai"), default="team")
        parser.add_argument("--output")
        parser.add_argument("--strict", action="store_true")

    def handle(self, *args, **options):
        results = run_duel(options["source"])
        for item in results:
            self.stdout.write(
                f"Q{item['number']}: {item['status']} | "
                f"{item['queries']}/{item['budget']} consultas"
            )
            if item["status"] != "accepted":
                self.stdout.write(f"  Esperado: {item['expected']}")
                self.stdout.write(f"  Obtenido: {item['actual']}")
                self.stdout.write(f"  Diagnóstico: {item['classification']}")
                if item["error"]:
                    self.stdout.write(f"  {item['error']}")
        accepted = sum(item["status"] == "accepted" for item in results)
        self.stdout.write(f"Aceptadas: {accepted}/8")
        if options["output"]:
            Path(options["output"]).write_text(
                json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        if options["strict"] and accepted != 8:
            raise CommandError("The adapted duel has unresolved candidates.")
