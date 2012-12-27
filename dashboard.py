#coding=utf-8

from django.contrib.admin.models import LogEntry
from django.contrib.admin.sites import NotRegistered
from django.contrib.admin.util import quote
from django.core.exceptions import ObjectDoesNotExist
from django.db.models.query import QuerySet

from django.contrib.admin.templatetags.admin_list import *
from django.template.loader import render_to_string

__author__ = 'Johnny'
import re



class DashboardInfo(object):
    name = None
    query_set = None
    operation = None


    def __init__(self,name,query_set,operation='count'):
        self.name = name
        self.operation = operation
        if isinstance(query_set,QuerySet):
            self.query_set = query_set
        else:
            raise AttributeError("invalid type of query_set")

    def value(self):
        if self.operation == 'count':
            return self.query_set.count()
        elif self.operation == 'list':
            return self.query_set.all()
        elif self.operation == 'first':
            if(self.query_set.count() > 0):
                return self.query_set[:1].get()
            return ''
        elif self.operation == 'last':
            if(self.query_set.count() > 0):
                return self.query_set.latest().get()
            return ''
        elif self.operation.isdigit():
            number = int(self.operation)
            return self.query_set[:number]
        raise AttributeError('Invalid operation param value')


class DashReportBase(object):
    model = None
    query_set = None
    title = None
    pk_attname = None
    meta = None

    def __init__(self,title,query_set):
        self.title = title
        if not isinstance(query_set,QuerySet):
            raise TypeError('the query_set parameter most be a QuerySet')

        self.query_set = query_set
        self.model = self.query_set.model
        self.meta = self.model._meta
        self.pk_attname = self.model._meta.pk.attname

    def url_for_result(self, result):
        return "%s/" % quote(getattr(result, self.pk_attname))

class ListReport(DashReportBase):

    display_fields = []
    list_size = 5

    def __init__(self,title,query_set,display_fields = None,list_size = 5):
        super(ListReport,self).__init__(title=title,query_set=query_set)

        if display_fields == None:
            fields = []
            for f in self.model._meta.fields:
                if f.name != self.pk_attname:
                    fields.append(f.name)

            self.display_fields = fields
        else:
            self.display_fields = display_fields

        self.list_size = list_size

    def lookup_field(self,name, obj):
        opts = obj._meta
        try:
            f = opts.get_field(name)
        except models.FieldDoesNotExist:
            # For non-field values, the value is either a method, property or
            # returned via a callable.
            if callable(name):
                attr = name
                value = attr(obj)
            else:
                attr = getattr(obj, name)
                if callable(attr):
                    value = attr()
                else:
                    value = attr
            f = None
        else:
            attr = None
            value = getattr(obj, name)
        return f, attr, value

    def html_output(self):

        headers = self.headers()

        results = self.results()

        return render_to_string('dashboard/list_report.html',{'title':self.title,
                                                              'result_headers': headers,
                                                              'results': results})

    def results(self):
        results = []

        for r in self.query_set.all()[:self.list_size]:
            itens = []
            first = True
            for f in self.display_fields:
                f, attr, value = lookup_field(f,r)

                url = ''
                if first:
                    url = self.url_for_result(r)

                itens.append({'url':url,'value':value,'is_date':isinstance(value,datetime.datetime)})
                first = False

            results.append({'itens':itens})

        return results

    def headers(self):
        headers = []
        for f in self.display_fields:
            for field in self.meta.fields:
                if field.name == f:
                    headers.append({'class':'','text':field.verbose_name})

        return headers


class BaseDashboard(object):
    title = None
    infos = []
    reports = []

    def __init__(self, title, ):
        self.title = title

    def add_info(self, info):
        if isinstance(info,DashboardInfo):
            self.infos.append(info)

    def remove_info(self,info):
        if info not in self.infos:
            raise NotRegistered('The info %s is not registered' % name)
        self.infos.remove(info)

    def add_report(self, report):
        if isinstance(report,DashReportBase):
            self.reports.append(report)

    def remove_report(self,report):
        if report not in self.reports:
            raise NotRegistered('The info %s is not registered' % name)
        self.reports.remove(report)

    def __unicode__(self):
        return self.title

class ModelDashboard(BaseDashboard):
    model = None

    def __init__(self,model,infos = []):

        if isinstance(model,models.Model):
            self.model = model
        else:
            raise TypeError('the model param most be a model.Model instance')

        for i in infos:
            self.add_info(info)

    def get_opts(self):
        return self.model._meta

    def has_add_permission(self, request):
        if self.get_opts.auto_created:
            # We're checking the rights to an auto-created intermediate model,
            # which doesn't have its own individual permissions. The user needs
            # to have the change permission for the related model in order to
            # be able to do anything with the intermediate model.
            return self.has_change_permission(request)
        return request.user.has_perm(
            self.opts.app_label + '.' + self.opts.get_add_permission())

    def has_change_permission(self, request, obj=None):
        opts = self.get_opts
        if opts.auto_created:
            # The model was auto-created as intermediary for a
            # ManyToMany-relationship, find the target model
            for field in opts.fields:
                if field.rel and field.rel.to != self.parent_model:
                    opts = field.rel.to._meta
                    break
        return request.user.has_perm(
            opts.app_label + '.' + opts.get_change_permission())

    def has_delete_permission(self, request, obj=None):
        if self.get_opts.auto_created:
            # We're checking the rights to an auto-created intermediate model,
            # which doesn't have its own individual permissions. The user needs
            # to have the change permission for the related model in order to
            # be able to do anything with the intermediate model.
            return self.has_change_permission(request, obj)
        return request.user.has_perm(
            self.opts.app_label + '.' + self.opts.get_delete_permission())

    def get_log(self):
        return LogEntry.objects.filter(content_type__model__exact=self.model).select_related('content_type', 'model')[:10]

class AppDashboard(BaseDashboard):

    app_label = None
    models_dashboards = []

    def has_read_permission(self,request):
        if(app_label):
            return request.user.has_module_perms(self.app_label)
        return False

    def add_model_dashboard(self, dash):
        if isinstance(dash,ModelDashboard):
            self.models_dashboards.append(dash)

    def remove_model_dashboard(self,dash):
        if dash not in self.models_dashboards:
            raise NotRegistered('The info %s is not registered' % dash.title)
        self.models_dashboards.remove(dash)

class DashboardManager(object):

    app_dashboards = []

    def register(self, dash):
        if isinstance(dash,BaseDashboard):
            self.app_dashboards.append(dash)
        else:
            raise TypeError('the object that you trying to registers is not an BaseDashboard')

    def unregister(self, app_dash):
        if isinstance(app_dash, BaseDashboard):
            if app_dash not in self.app_dashboards:
                raise NotRegistered('The dashboard %s is not registered' % app_dash.title)
            self.app_dashboards.remove(app_dash)

dash = DashboardManager()