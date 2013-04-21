import datetime
import re

from django import template
from django.template import Library

register = Library()

@register.simple_tag
def copyright_date(start_year):
    curr_year = datetime.datetime.now().strftime('%Y')
    if str(start_year) == curr_year:
        return curr_year
    return '%s-%s' % (start_year, curr_year)

@register.simple_tag
def active(request, pattern):
    if re.search(pattern, request.path):
        return 'active'
    return ''


@register.inclusion_tag('_main_menu.html', takes_context=True)
def main_menu(context):
    request = context['request']
    user = request.user
    menu_dict = {'main_menu':{
        'companies': {},
        'bluusites': {
            'manage': {},
            'view': {}
        }
    }}

    if user.is_authenticated():
        menu_dict['main_menu']['companies'].update(
                        user.can_see_companies(perm='companies.change_company'))
        menu_dict['main_menu']['bluusites']['manage'].update(
                        user.can_see_sites(perm='bluusites.change_bluusite'))
        menu_dict['main_menu']['bluusites']['view'].update(
                        user.can_see_sites(perm='bluusites.view_bluusite'))
    context.update(menu_dict)
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
