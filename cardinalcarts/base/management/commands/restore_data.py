from django.core.management import call_command
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Restore CardinalCarts data"

    def handle(self, *args, **kwargs):
        call_command('loaddata', 'backup/backup.json')
        self.stdout.write(self.style.SUCCESS("Restore successful"))
