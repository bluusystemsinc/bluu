from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db import models
from .countries import CountryField
from south.modelsinspector import add_introspection_rules
add_introspection_rules([], ["^utils\.countries\.CountryField"])


class Entity(models.Model):
    street = models.CharField(_('street'), max_length=50, blank=True)
    city = models.CharField(_('city'), max_length=50, blank=True)
    state = models.CharField(_('state'), max_length=50, blank=True)
    zip_code = models.CharField(_('zip code'), max_length=7, blank=True)
    country = CountryField(_('country'), default='US', blank=True)
    phone = models.CharField(_('phone'), max_length=10, blank=True)
    email = models.EmailField(_('email address'), blank=True)

    class Meta:
        abstract = True

