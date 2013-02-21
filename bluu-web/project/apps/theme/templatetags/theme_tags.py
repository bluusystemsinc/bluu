import datetime
import re

from django import template
from django.template import Library

from grontextual.models import UserObjectGroup
from grontextual.shortcuts import get_objects_for_user

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
    menu_dict = {'main_menu':{}}

    if user.is_authenticated():
        # user is assigned to only one company
        companies = get_objects_for_user(user, 'companies.view_company')
        ccount = companies.count()
        menu_dict['main_menu']['company_count'] = ccount
        if not user.has_perm('companies.add_company') and ccount == 1:
            menu_dict['main_menu']['company'] = companies[0]

        # user is assigned to only one site 
        sites = get_objects_for_user(user, 'bluusites.view_bluusite')
        scount = sites.count()
        menu_dict['main_menu']['bluusite_count'] = scount
        if not user.has_perm('bluusites.add_bluusite') and scount == 1:
            menu_dict['main_menu']['bluusite'] = sites[0]

    context.update(menu_dict)
    return context


@register.inclusion_tag('_company_breadcrumb.html', takes_context=True)
def companies_breadcrumb(context):
    request = context['request']
    user = request.user
    
    bread_dict = {}
    single = False
    # if user is assigned to only one company
    if user.get_companies().count() == 1:
        single = True
    bread_dict['single'] = single

    return bread_dict


@register.inclusion_tag('_bluusite_breadcrumb.html', takes_context=True)
def bluusites_breadcrumb(context):
    request = context['request']
    user = request.user
    
    bread_dict = {}
    single = False
    # if user is assigned to only one site
    if user.get_sites().count() == 1:
        single = True
    bread_dict['single'] = single

    return bread_dict



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
