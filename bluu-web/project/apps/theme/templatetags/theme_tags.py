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
    """
    Renders main menu including different access levels for current user:

    1. If user has access to many companies - render "Companies" link that leads
       to company list page
    2. If user has access to one company - render "Company" link that leads
       to company management page
    3. If user has access to many sites - render "Sites" link that leads to
       site list page
    4. If there's a bluusite in page context or user has access to only one
       bluusite then:
       a) render "Alerts" link (every user can set alerts for site if only he has
          access to this site) that leads to alerts configuration page
       b) if user has perm to browse or manage devices then render "Devices"
          link that leads to devices configuration page
       c) if user has perm to change bluusite then render "Manage site" link
          that leads to site management (edit) page
    """
    request = context['request']
    bluusite = context.get('bluusite', None)
    user = request.user
    menu_dict = {'main_menu': {}}

    if user.is_authenticated():
        sites = user.get_sites()
        count = sites.count()
        # if user has access to many sites then mark it
        if (user.has_perm('bluusites.browse_bluusites') and user.can_add_sites()) \
                or (count > 1):
            menu_dict['main_menu']['bluusites'] = True
        # if there's no current bluusite, but user has access to one and only one
        # bluusite then use it
        elif (bluusite is None) and (count == 1):
           bluusite = sites[0]

        # get companies data
        menu_dict['main_menu']['companies'] = \
                        user.can_see_companies(perm='companies.change_company')

        if bluusite and (user.has_perm('bluusites.view_bluusite') or \
                            user.has_perm('bluusites.view_bluusite', bluusite)):
            menu_dict['main_menu']['bluusite'] = {}
            menu_dict['main_menu']['bluusite']['bluusite'] = bluusite
            menu_dict['main_menu']['bluusite']['show_devices'] = \
                user.has_perm('bluusites.browse_devices', bluusite) or \
                user.has_perm('bluusites.browse_devices')
            #menu_dict['main_menu']['bluusite']['show_rooms'] = \
            #    user.has_perm('bluusites.browse_rooms', bluusite)
            menu_dict['main_menu']['bluusite']['show_management'] = \
                user.has_perm('bluusites.change_bluusite', bluusite) or \
                user.has_perm('bluusites.change_bluusite')

    context.update(menu_dict)
    return context


@register.inclusion_tag('_company_breadcrumb.html', takes_context=True)
def companies_breadcrumb(context):
    request = context['request']
    user = request.user
    
    if user.get_companies(perm='companies.change_company').count() == 1:
        return {'single': True}
    return {'single': False}


@register.inclusion_tag('_bluusite_breadcrumb.html', takes_context=True)
def bluusites_breadcrumb(context):
    request = context['request']
    user = request.user
 
    if user.get_sites(perm='bluusites.view_bluusite').count() == 1:
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
