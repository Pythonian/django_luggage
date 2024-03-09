from django.core.management.base import BaseCommand

from ...models import State, ParkLocation


class Command(BaseCommand):
    help = "Populate the database with State and Park Locations."

    def handle(self, *args, **kwargs):
        pass
