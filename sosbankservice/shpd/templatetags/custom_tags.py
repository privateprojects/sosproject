#coding=utf8


from django import template

from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

from shpd.displayers import DisplayerFactory
from shpd import config


display_factory = DisplayerFactory.get_instance()

register = template.Library()


@register.filter
def localize(formatted_str):
    """ formatted_str is as 'displayer_name.field_name' """
    if (not formatted_str):
        return ""

    displayer_name, field_name = formatted_str.split(".", 2)
    displayer_map = display_factory.get_displayer(str(displayer_name), config.LANGUAGE)

    localized_str = (displayer_map and displayer_map.get(str(field_name))) or ""
    return mark_safe(localized_str)