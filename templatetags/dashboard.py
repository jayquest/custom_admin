#utf-8

__author__ = 'Johnny'

from django import template
from custom_admin import   dash

register = template.Library()

class IndexDashboardNode(template.Node):
    def __init__(self, varname, user=None):
        self.varname, self.user =  varname, user

    def __repr__(self):
        return "<GetIndexDashboard Node>"

    def render(self, context):
        if self.user is None:
            context[self.varname] = dash.app_dashboards
        else:
            context[self.varname] = dash.app_dashboards
        return ''


@register.tag
def get_dashboards(parser,token):
    """
    Populates a template variable with the apps dashboards.

    Usage::

        {% get_dashboards as [varname] for_user [context_var_containing_user_obj] %}

    Examples::

        {% get_dashboards as dashboards for_user 23 %}
        {% get_dashboards as dashboards for_user user %}
        {% get_dashboards as dashboards %}

    Note that ``context_var_containing_user_obj`` can be a hard-coded integer
    (user ID) or the name of a template context variable containing the user
    object whose ID you want.
    """
    tokens = token.contents.split()
    if len(tokens) < 3:
        raise template.TemplateSyntaxError(
            "'get_admin_log' statements require one arguments")
    if tokens[1] != 'as':
        raise template.TemplateSyntaxError(
            "First argument to 'get_admin_log' must be 'as'")
    if len(tokens) > 3:
        if tokens[3] != 'for_user':
            raise template.TemplateSyntaxError(
                "Fourth argument to 'get_admin_log' must be 'for_user'")
        else:
            return IndexDashboardNode(varname=tokens[2], user=(len(tokens) > 3 and tokens[4] or None))

    return IndexDashboardNode(varname=tokens[2])



