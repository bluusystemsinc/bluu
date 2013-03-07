import datetime
import re

from django import template
from django.template import Library

from ..models import Device

register = Library()

@register.inclusion_tag('devices/_devices_of_type.html', takes_context=True)
def devices_of_type(context, bluusite, device_type):
    request = context['request']
    user = request.user

    devices = Device.objects.filter(bluusite=bluusite, device_type=device_type)

    context.update({'device_type': device_type,
                    'devices': devices})
    return context


@register.inclusion_tag('_company_breadcrumb.html', takes_context=True)
def companies_breadcrumb(context):
    request = context['request']
    user = request.user
    
    if user.can_see_companies(perm='companies.change_company').\
            get('company', None) is not None:
        return {'single': True}
    return {'single': False}


@register.inclusion_tag('_bluusite_breadcrumb.html', takes_context=True)
def bluusites_breadcrumb(context):
    request = context['request']
    user = request.user
 
    if user.can_see_sites(perm='bluusites.change_bluusite').\
            get('bluusite', None) is not None:
        return {'single': True}
    return {'single': False}


"""
jQuery templates use constructs like:

    {{if condition}} print something{{/if}}

This, of course, completely screws up Django templates,
because Django thinks {{ and }} mean something.

Wrap {% verbatim %} and {% endverbatim %} around those
blocks of jQuery templates and this will try its best
to output the contents with no changes.
"""


class VerbatimNode(template.Node):

    def __init__(self, text):
        self.text = text
    
    def render(self, context):
        return self.text


@register.tag
def verbatim(parser, token):
    text = []
    while 1:
        token = parser.tokens.pop(0)
        if token.contents == 'endverbatim':
            break
        if token.token_type == template.TOKEN_VAR:
            text.append('{{')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('{%')
        text.append(token.contents)
        if token.token_type == template.TOKEN_VAR:
            text.append('}}')
        elif token.token_type == template.TOKEN_BLOCK:
            text.append('%}')
    return VerbatimNode(''.join(text))
