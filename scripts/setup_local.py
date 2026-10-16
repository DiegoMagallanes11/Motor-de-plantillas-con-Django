"""Write local-only settings and create a random administrator password."""
import os
import secrets
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root))
environment_file = root / ".env"
if not environment_file.exists():
    environment_file.write_text(
        f"DJANGO_SECRET_KEY={secrets.token_urlsafe(64)}\n"
        "DJANGO_DEBUG=1\nDJANGO_ALLOWED_HOSTS=127.0.0.1,localhost\n",
        encoding="utf-8",
    )
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
import django

django.setup()
from django.contrib.auth import get_user_model
from django.core.management import call_command

call_command("migrate", interactive=False)
call_command("seed_news")
user_model = get_user_model()
if not user_model.objects.filter(username="diego").exists():
    password = secrets.token_urlsafe(18)
    user_model.objects.create_superuser("diego", password=password)
    private_directory = root / ".private"
    private_directory.mkdir(exist_ok=True)
    (private_directory / "admin-access.txt").write_text(
        "Portal local: http://127.0.0.1:8000/admin/\n"
        f"Usuario: diego\nContraseña: {password}\n"
        "Archivo privado excluido de Git.\n", encoding="utf-8",
    )
    print("Administrator created. Read .private/admin-access.txt locally.")
else:
    print("Existing administrator preserved.")
