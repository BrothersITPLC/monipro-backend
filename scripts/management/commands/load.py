import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Load multiple fixture files into the database from scripts/data"

    def handle(self, *args, **options):
        data_dir = os.path.join(settings.BASE_DIR, "scripts", "data")
        if not os.path.exists(data_dir):
            self.stdout.write(
                self.style.ERROR(f"❌ Data directory does not exist: {data_dir}")
            )
            return
        json_files = [f for f in os.listdir(data_dir) if f.endswith(".json")]

        if not json_files:
            self.stdout.write(
                self.style.WARNING("⚠ No JSON files found in data directory.")
            )
            return

        loaded = 0

        for filename in json_files:
            filepath = os.path.join(data_dir, filename)
            try:
                call_command("loaddata", filepath)
                self.stdout.write(
                    self.style.SUCCESS(f"✅ Successfully loaded {filename}")
                )
                loaded += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Failed to load {filename}: {e}")
                )
        self.stdout.write(
            self.style.SUCCESS(f"✅ Loaded {loaded} out of {len(json_files)} files.")
        )
