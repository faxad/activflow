"""Helpers"""

import inspect
from importlib import import_module

from django.apps import apps
from django.forms.models import modelform_factory

from djangoflow.core.constants import WORKFLOW_APPS


def get_errors(form_errors):
    """Returns compiled form errors"""
    error_list = []
    errors = form_errors.as_data().copy()
    errors = [error_list.append(
        e + ': ' + str(
            list(errors[e][0])[0])) for e in errors]

    return list(set(error_list))


def discover():
    """Returns activity configuration for all registered
    workflow apps
    """
    discovered = {}
    for app in WORKFLOW_APPS:
        name = apps.get_app_config(app).name
        discovered[app] = import_module(
            '{}.config'.format(name)
        ).ACTIVITY_CONFIG

    return discovered


def flow_config(module):
    """Returns flow configuration"""
    return import_module(
        '{}.flow'.format(apps.get_app_config(module).name))


def get_request_params(what, request=None, **kwargs):
    """Returns provided argument value"""
    args = {'app_name': 1, 'model_name': 2, 'pk': 4}

    try:
        return kwargs.get(
            what, request.path.split('/')[
                args[what]] if request else None)
    except IndexError:
        pass


def get_model(**kwargs):
    """Returns model"""
    return apps.get_model(
        get_request_params('app_name', **kwargs),
        get_request_params('model_name', **kwargs))


def get_model_instance(request, **kwargs):
    """Returns model instance"""
    return get_model(**kwargs).objects.get(id=kwargs.get("pk"))


def get_form_instance(**kwargs):
    """Returns form instance"""
    fields = []
    field_config = discover()[get_request_params(
        'app_name', **kwargs)][get_request_params('model_name', **kwargs)]
    callee = type(inspect.currentframe().f_back.f_locals['self']).__name__
    operation = 'create' if 'Create' in callee else 'update'

    for field in field_config:
        if operation in field_config[field]:
            fields.append(field)

    return modelform_factory(get_model(**kwargs), fields=fields)
