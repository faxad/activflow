"""Helpers"""

import inspect
from importlib import import_module

from django.apps import apps
from django.forms.models import modelform_factory
from django.db.models import Q

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


def get_flow(module):
    """Returns the flow"""
    return import_module(
        '{}.flow'.format(apps.get_app_config(module).name)
    ).FLOW


def extract_from_url(request, position):
    """Returns app/model from url"""
    return request.path.split('/')[position] if request else None


def get_task_id(request=None, **kwargs):
    """Returns task identifier"""
    try:
        return kwargs.get(
            'pk', extract_from_url(request, 4))
    except IndexError:
        pass


def get_app_name(request=None, **kwargs):
    """Returns the name of app"""
    return kwargs.get(
        'app_name', extract_from_url(request, 1))


def get_model_name(request=None, **kwargs):
    """Returns the name of model"""
    try:
        return kwargs.get(
            'model_name', extract_from_url(request, 2))
    except IndexError:
        pass


def get_model(**kwargs):
    """Returns model"""
    return apps.get_model(
        get_app_name(**kwargs),
        get_model_name(**kwargs))


def get_model_instance(request, **kwargs):
    """Returns model instance"""
    instance = get_model(**kwargs).objects.filter(id=kwargs.get("pk"))

    if not request.user.is_superuser:
        return instance.filter(task__assignee__in=list(
            request.user.groups.all())).latest('id')
    else:
        return instance.latest('id')


def get_form_instance(**kwargs):
    """Returns form instance"""
    fields = []
    field_config = discover()[get_app_name(
        **kwargs)][get_model_name(**kwargs)]
    callee = type(inspect.currentframe().f_back.f_locals['self']).__name__
    operation = 'create' if 'Create' in callee else 'update'

    for field in field_config:
        if operation in field_config[field]:
            fields.append(field)

    return modelform_factory(get_model(**kwargs), fields=fields)
