from django import template
from django.utils.timesince import timesince

register = template.Library()

@register.filter
def custom_timesince(value):
    result = timesince(value)
    return result.split(",")[0]
