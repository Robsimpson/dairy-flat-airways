from django import template
from datetime import datetime
from zoneinfo import ZoneInfo

from dairy_flat_airways.models import Airport

register = template.Library()

timezone = ZoneInfo('Pacific/Auckland')


@register.filter
def get_length(obj):
    return len(obj)


@register.filter
def get_datetime(timestamp):
    return datetime.fromtimestamp(timestamp).astimezone(timezone)


@register.filter
def price_leg(flightleg):
    flightleg.price = max(round(flightleg.distance * 0.25) - 1, 79)
    flightleg.save()
    return flightleg.price


@register.filter
def get_airport_code(airport_name):
    return Airport.objects.get(name=airport_name).id


@register.filter
def to_list(num):
    return range(1, num)
