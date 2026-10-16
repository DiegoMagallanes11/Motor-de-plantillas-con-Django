import json

from django.core.management.base import BaseCommand

from blog.seed import seed_blog


class Command(BaseCommand):
    help = "Reset only the adapted blog practice data; preserve news and auth."

    def handle(self, *args, **options):
        self.stdout.write(json.dumps(seed_blog(), ensure_ascii=False, indent=2))
