from django.contrib.contenttypes.models import ContentType
from bluusites.models import BluuSite, BluuSiteAccess
from grontextual.models import UserObjectGroup
from companies.models import Company, CompanyAccess

# import the logging library
import logging

# Get an instance of a logger
logger = logging.getLogger('bluu')


def cleanup_companyaccess():
    ctype = ContentType.objects.get_for_model(Company)
    trash = []
    for uog in UserObjectGroup.objects.filter(content_type=ctype):
        if not CompanyAccess.objects.filter(user=uog.user,
                                            company__pk=uog.object_pk,
                                            group=uog.group).exists():
            trash.append(uog.pk)
    UserObjectGroup.objects.filter(pk__in=trash).delete()
    logger.info('Cleaned up company uogs: {}'.format(trash))
    return trash
