from django import template

register = template.Library()

@register.filter(name='split')
def split(value, key):
    """
    Splits the value by the given key and returns the last element of the list.
    """
    return value.split(key)[-1]