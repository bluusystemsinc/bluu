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


def can_add_sites(user):
    """
    If there is a company or companies a user has permission to
    add bluusites to them then return true.
    """
    if get_objects_for_user(user, 'bluusites.add_bluusite').count() > 0:
        return True
    return False


@register.inclusion_tag('_main_menu.html', takes_context=True)
def main_menu(context):
    request = context['request']
    user = request.user
    menu_dict = {'main_menu':{}}

    if user.is_authenticated():
        companies = get_objects_for_user(user, 'companies.view_company')
        ccount = companies.count()

        if (user.has_perm('companies.browse_companies') and \
            user.has_perm('companies.add_company')) or \
           (ccount > 1):
            """
            If user is Bluu then show companies.
            If user is Dealer or Technician then show companies if more than 1 
            assigned.
            """
            menu_dict['main_menu']['companies'] = True
            menu_dict['main_menu']['company'] = None
        elif (ccount == 1) and \
                user.has_perm('companies.change_company', companies[0]):
            """
            If user isn't Bluu and has only one company assigned then
            show only this one company.
            """
            menu_dict['main_menu']['companies'] = False
            menu_dict['main_menu']['company'] = companies[0]
        else:
            """
            If user isn't Bluu and has no companies assigned then don't 
            show any companies.
            """
            menu_dict['main_menu']['companies'] = False
            menu_dict['main_menu']['company'] = None

        sites = get_objects_for_user(user, 'bluusites.view_bluusite')
        scount = sites.count()
        if (user.has_perm('bluusites.browse_bluusites') and \
            user.has_perm('bluusites.add_bluusite')) or \
            (user.has_perm('bluusites.browse_bluusites') and \
            can_add_sites(user)) or \
           (scount > 1): 
            """
            If user is Bluu then show sites
            If user is Dealer or Technician then show sites
            If user is assigned to more than one site then show sites
            """
            menu_dict['main_menu']['bluusites'] = True
            menu_dict['main_menu']['bluusite'] = None
        elif (scount == 1) and \
                user.has_perm('bluusites.change_bluusite', sites[0]):
            """
            If user isn't Bluu or Dealer or Technician and is assigned
            to only one site then show this one site
            """
            menu_dict['main_menu']['bluusites'] = False
            menu_dict['main_menu']['bluusite'] = sites[0]
        else:
            menu_dict['main_menu']['bluusites'] = False
            menu_dict['main_menu']['bluusite'] = None

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
