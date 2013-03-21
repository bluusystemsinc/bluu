from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from grontextual.models import UserObjectGroup
from companies.models import Company, CompanyAccess


class Command(BaseCommand):
    help = 'Removes orphaned UserObjectGroups permissions for Companies'

    def handle(self, *args, **options):
        ctype = ContentType.objects.get_for_model(Company)
        trash = []
        for uog in UserObjectGroup.objects.filter(content_type=ctype):
            if not CompanyAccess.objects.filter(user=uog.user,
                                                company__pk=uog.object_pk,
                                                group=uog.group).exists():
                trash.append(uog.pk)
        UserObjectGroup.objects.filter(pk__in=trash).delete()
        self.stdout.write('Successfully cleaned up "{}" company uogs'.\
                                                             format(str(trash)))
