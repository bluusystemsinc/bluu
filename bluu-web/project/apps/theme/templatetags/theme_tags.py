import datetime
import re
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
