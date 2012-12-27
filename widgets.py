#coding=utf-8

from django import forms
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.contrib.admin.widgets import AdminDateWidget, AdminTimeWidget

__author__ = 'Johnny'

class CustomAdminSplitDateTime(forms.SplitDateTimeWidget):
    """
    A SplitDateTime Widget that has some admin-specific styling.
    """
    def __init__(self, attrs=None):
        widgets = [AdminDateWidget, AdminTimeWidget]
        # Note that we're calling MultiWidget, not SplitDateTimeWidget, because
        # we want to define widgets.
        forms.MultiWidget.__init__(self, widgets, attrs)

    def format_output(self, rendered_widgets):
        return mark_safe(u'<span>%s</span> %s <span style="margin-left:20px">%s</span> %s' %\
                         (_('Date:'), rendered_widgets[0], _('Time:'), rendered_widgets[1]))