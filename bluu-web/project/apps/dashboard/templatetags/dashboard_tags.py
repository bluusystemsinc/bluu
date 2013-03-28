import json
import calendar

from django.template import Library

register = Library()


@register.inclusion_tag('dashboard/_sleep_graph.html', takes_context=True)
def sleep_graph(context, bluusite):
    pass


def get_hours(seconds):
    return seconds / 3600


@register.inclusion_tag('dashboard/_sleep_graph_media.html', takes_context=True)
def sleep_graph_media(context, bluusite):
    beds = bluusite.get_sleeps()
    sleeps = []
    for k, bed in beds.iteritems():
        for sleep in bed:
            timestamp = sleep.get('timestamp')
            length = sleep.get('length')
            if timestamp and length:
                dat = calendar.timegm(timestamp.timetuple()) * 1000
                sleeps.append((dat, get_hours(length)))
    ret = {'sleeps': json.dumps(sleeps)} 
    return ret

