#coding = utf-8

from django.contrib.admin.views.main import (   PAGE_VAR )
from django.utils.html import escape
from django.utils.safestring import mark_safe
from django.template import Library

__author__ = 'Jonatas'

register = Library()

DOT = '.'

@register.simple_tag
def my_paginator_number(cl,i):
    """
    Generates an individual page index link in a paginated list.
    """
    if i == DOT:
        return mark_safe(u'<span class="this-page">%s</span> ' % '...')
    elif i == cl.page_num:
        return mark_safe(u'<span class="this-page">%d</span> ' % (i+1))
    else:
        return mark_safe(u'<a href="%s"%s>%d</a> ' % (escape(cl.get_query_string({PAGE_VAR: i})), (i == cl.paginator.num_pages-1 and ' class="end"' or ''), i+1))
