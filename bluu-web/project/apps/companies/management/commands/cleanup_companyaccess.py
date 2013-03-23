from django.core.management.base import BaseCommand

from companies.misc import cleanup_companyaccess


class Command(BaseCommand):
    help = 'Removes orphaned UserObjectGroups permissions for Companies'

    def handle(self, *args, **options):
        cleanup_companyaccess()
