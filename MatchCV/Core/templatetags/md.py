"""Render the markdown the model returns as readable HTML."""

import markdown as markdown_lib
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name="markdown")
def markdown_filter(value):
    return mark_safe(markdown_lib.markdown(value or "", extensions=["extra", "sane_lists"]))

