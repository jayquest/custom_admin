import os
from django.conf import settings
from django.contrib import admin
from django.contrib.admin.sites import NotRegistered
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from custom_admin import custom_site
from dashboard import dash

from custom_model_admin import CustomModelAdmin, CustomGroupAdmin, CustomUserAdmin

def autodiscover():
    """
    Auto-discover INSTALLED_APPS admin.py modules and fail silently when
    not present. This forces an import on them to register any admin bits they
    may want.
    """

    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule


    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(custom_site._registry)
            import_module('%s.admin' % app)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            custom_site._registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'admin'):
                raise


        ##########DASHBOARD############

        # Attempt to import the app's dashboard module.
        try:
            before_import_dashs = copy.copy(dash.app_dashboards)
            import_module('%s.dashboard' % app)
        except:
            # Reset the dashboard registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            dash.app_dashboards = before_import_dashs

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'dashboard'):
                raise

    for model,admin_class in admin.site._registry.items():
        try:
            custom_site.unregister(model)
        except NotRegistered:
            if isinstance(admin_class,UserAdmin):
                custom_site.register(model,CustomUserAdmin)
            else:
                if isinstance(admin_class,GroupAdmin):
                    custom_site.register(model,CustomGroupAdmin)
                else:
                    custom_site.register(model,CustomModelAdmin)


settings.TEMPLATE_DIRS += (os.path.join(os.path.abspath(os.path.dirname(__file__)),'templates'),)
settings.STATICFILES_DIRS += (os.path.join(os.path.abspath(os.path.dirname(__file__)),'static'),)
