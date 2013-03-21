from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from grontextual.models import UserObjectGroup
from companies.models import Company, CompanyAccess
from bluusites.models import BluuSite, BluuSiteAccess


class Command(BaseCommand):
    help = 'Removes orphaned UserObjectGroups permissions for Sites'

    def handle(self, *args, **options):
        trash = []
        sctype = ContentType.objects.get_for_model(BluuSite)

        for uog in UserObjectGroup.objects.filter(content_type=sctype):
            trash_me = False
            if (not BluuSiteAccess.objects.filter(user=uog.user,
                                                site__pk=uog.object_pk,
                                                group=uog.group).exists()):
                try:
                    site = BluuSite.objects.get(pk=uog.object_pk)
                    if not CompanyAccess.objects.filter(user=uog.user,
                                            company__pk=site.company.pk,
                                            group=uog.group).exists():
                        trash_me = True
                except BluuSite.DoesNotExist:
                    trash_me = True
            if trash_me:
                trash.append(uog.pk)
        #UserObjectGroup.objects.filter(pk__in=trash).delete()

        self.stdout.write('Successfully cleaned up "{}" site uogs'.\
                                                             format(str(trash)))
