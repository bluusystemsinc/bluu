from django.core.management.base import BaseCommand

from bluusites.misc import cleanup_siteaccess


class Command(BaseCommand):
    help = 'Removes orphaned UserObjectGroups permissions for Sites'

    def handle(self, *args, **options):
        cleanup_siteaccess()
