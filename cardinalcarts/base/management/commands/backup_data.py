from django.core.management import call_command
from django.core.management.base import BaseCommand
import os

class Command(BaseCommand):
    help = "Backup CardinalCarts data"

    def handle(self, *args, **kwargs):
        os.makedirs('backup', exist_ok=True)
        with open('backup/backup.json', 'w', encoding='utf-8') as f:
            call_command('dumpdata', 'base', format='json', indent=2, stdout=f)
        self.stdout.write(self.style.SUCCESS("Backup successful"))
