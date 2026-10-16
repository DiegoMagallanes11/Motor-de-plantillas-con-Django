import json

from django.core.management.base import BaseCommand

from blog.agent.intents import execute_intent
from blog.agent.registry import dispatch


class Command(BaseCommand):
    help = "Execute one explicitly allowed local action; never interpret code."

    def add_arguments(self, parser):
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument("--intent")
        group.add_argument("--action")
        parser.add_argument("--article-id", type=int)
        parser.add_argument("--approve")

    def handle(self, *args, **options):
        if options["intent"]:
            if options["article_id"] is not None:
                result = {"status": "denied", "reason": "unexpected_arguments"}
            else:
                result = execute_intent(options["intent"], options["approve"])
        else:
            arguments = {} if options["article_id"] is None else {
                "article_id": options["article_id"]
            }
            result = dispatch(options["action"], arguments, options["approve"])
        self.stdout.write(json.dumps(result, ensure_ascii=False, indent=2))
