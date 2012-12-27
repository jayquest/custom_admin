__author__ = 'Johnny'

from django import template
from django.contrib.admin.models import LogEntry
from django.contrib.admin.templatetags.log import AdminLogNode

register = template.Library()

class MyAdminLogNode(AdminLogNode):
    def __init__(self, limit, varname, user=None,model=None):
        self.limit, self.varname, self.user, self.model = limit, varname, user, model

    def __repr__(self):
        return "<GetAdminLog Node>"

    def render(self, context):
        if self.user is None and self.model is None:
            context[self.varname] = LogEntry.objects.all().select_related('content_type', 'user')[:self.limit]
        else:
            if self.model is None:
                user_id = self.user
                if not user_id.isdigit():
                    user_id = context[self.user].id
                context[self.varname] = LogEntry.objects.filter(user__id__exact=user_id).select_related('content_type', 'user')[:self.limit]
            else:
                model = context[self.model]['model_name']
                if isinstance(model,str):
                    context[self.varname] = LogEntry.objects.filter(content_type__model__exact=model).select_related('content_type', 'model')[:self.limit]
        return ''

@register.tag
def my_get_admin_log(parser, token):
    """
    Populates a template variable with the admin log for the given criteria.

    Usage::

        {% get_admin_log [limit] as [varname] for_user [context_var_containing_user_obj] %}

        {% get_admin_log [limit] as [varname] for_model [context_var_containing_model_obj] %}

    Examples::

        {% get_admin_log 10 as admin_log for_user 23 %}
        {% get_admin_log 10 as admin_log for_user user %}
        {% get_admin_log 10 as admin_log %}

    Note that ``context_var_containing_user_obj`` can be a hard-coded integer
    (user ID) or the name of a template context variable containing the user
    object whose ID you want.
    """
    tokens = token.contents.split()
    if len(tokens) < 4:
        raise template.TemplateSyntaxError(
            "'get_admin_log' statements require two arguments")
    if not tokens[1].isdigit():
        raise template.TemplateSyntaxError(
            "First argument to 'get_admin_log' must be an integer")
    if tokens[2] != 'as':
        raise template.TemplateSyntaxError(
            "Second argument to 'get_admin_log' must be 'as'")
    if len(tokens) > 4:
        if tokens[4] != 'for_user' and tokens[4] != 'for_model':
            raise template.TemplateSyntaxError(
                "Fourth argument to 'get_admin_log' must be 'for_user' or 'for_model'")
    if(tokens[4] == 'for_user'):
        return MyAdminLogNode(limit=tokens[1], varname=tokens[3], user=(len(tokens) > 4 and tokens[5] or None))
    else:
        return MyAdminLogNode(limit=tokens[1], varname=tokens[3], model=(len(tokens) > 4 and tokens[5] or None))

