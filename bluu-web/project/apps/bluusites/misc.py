from django.contrib.contenttypes.models import ContentType
from bluusites.models import BluuSite, BluuSiteAccess
from grontextual.models import UserObjectGroup
from companies.models import CompanyAccess

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger('bluu')


def cleanup_siteaccess():
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
    UserObjectGroup.objects.filter(pk__in=trash).delete()
    logger.info('Cleaned up site uogs: {}'.format(trash))
    return trash

