#utf-8

from django.template.defaultfilters import capfirst

__author__ = 'Johnny'

from custom_admin import  custom_site

def all_app_list(request):
    """
    return a lists of all of the installed
    apps that have been registered in this site.
    """
    app_dict = {}
    user = request.user
    for model, model_admin in custom_site._registry.items():
        app_label = model._meta.app_label
        has_module_perms = user.has_module_perms(app_label)



        if has_module_perms:
            perms = model_admin.get_model_perms(request)

            # Check whether user has any perm for this module.
            # If so, add the module to the model_list.
            if True in perms.values():
                info = (app_label, model._meta.module_name)
                model_dict = {
                    'name': capfirst(model._meta.verbose_name_plural),
                    'perms': perms,
                    'model_name' :  model._meta.verbose_name,
                    }
                if perms.get('change', False):
                    try:
                        model_dict['admin_url'] = reverse('admin:%s_%s_changelist' % info, current_app=self.name)
                    except NoReverseMatch:
                        pass
                if perms.get('add', False):
                    try:
                        model_dict['add_url'] = reverse('admin:%s_%s_add' % info, current_app=self.name)
                    except NoReverseMatch:
                        pass
                if app_label in app_dict:
                    app_dict[app_label]['models'].append(model_dict)
                else:
                    app_dict[app_label] = {
                        'name': app_label.title(),
                        'app_url': reverse('admin:app_list', kwargs={'app_label': app_label}, current_app=self.name),
                        'has_module_perms': has_module_perms,
                        'models': [model_dict],
                        }

    # Sort the apps alphabetically.
    app_list = app_dict.values()
    app_list.sort(key=lambda x: x['name'])

    # Sort the models alphabetically within each app.
    for app in app_list:
        app['models'].sort(key=lambda x: x['name'])

    return app_list;

