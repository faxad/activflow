"""Helpers"""

import inspect
from importlib import import_module

from django.apps import apps
from django.forms.models import modelform_factory


# Configuration Loaders

def workflow_config(module):
    """Returns workflow configuration"""
    return import_module(
        '{}.config'.format(
            apps.get_app_config(module).name))


def activity_config(module, model):
    """Returns activity configuration"""
    return workflow_config(
        module).ACTIVITY_CONFIG[model]


def flow_config(module):
    """Returns flow configuration"""
    return import_module(
        '{}.flow'.format(apps.get_app_config(module).name))


def transition_config(module, activity):
    """Returns all possible transitions
    for a given workflow module and activity
    """
    return flow_config(
        module).FLOW[activity]['transitions']


def wysiwyg_config(module, activity):
    """Returns configuration for WYSIWYG editor"""
    return workflow_config(
        module).WYSIWYG_CONFIG[activity]


def form_config(module, activity):
    """Returns custom form configuration"""
    return workflow_config(
        module).FORM_CONFIG[activity]

# Request Helpers


def get_request_params(what, request=None, **kwargs):
    """Returns requested argument value"""
    args = {'app_name': 1, 'model_name': 2, 'pk': 4}

    try:
        return kwargs.get(
            what, request.path.split('/')[
                args[what]] if request else None)
    except IndexError:
        pass


# Model and Form Helpers


def get_model(**kwargs):
    """Returns model"""
    args = [get_request_params(
        key, **kwargs) for key in ('app_name', 'model_name')]

    return apps.get_model(*args)


def get_model_instance(**kwargs):
    """Returns model instance"""
    return get_model(**kwargs).objects.get(id=kwargs.get("pk"))


def get_custom_form(**kwargs):
    """Returns custom form instance"""
    try:
        args = [get_request_params(
            key, **kwargs) for key in ('app_name', 'model_name')]
        config = form_config(*args)
        return getattr(import_module(
            '{}.forms'.format(apps.get_app_config(args[0]).name)), config)
    except (AttributeError, KeyError):
        return None


def get_form_instance(**kwargs):
    """Returns form instance"""
    callee = type(inspect.currentframe().f_back.f_locals['self']).__name__
    operation = 'create' if 'Create' in callee else 'update'
    try:
        field_config = activity_config(*[get_request_params(
            key, **kwargs) for key in ('app_name', 'model_name')])
        fields = [field for field in field_config
                  if operation in field_config[field]]
    except KeyError:
        fields = [field for field in (
            field.name for field in get_model(**kwargs)().class_meta.
            get_fields()) if field not in [
                'id', 'task', 'task_id', 'last_updated', 'creation_date']]
    arguments = {'fields': fields}
    custom_form = get_custom_form(**kwargs)

    if custom_form:
        arguments['form'] = custom_form

    return modelform_factory(get_model(**kwargs), **arguments)


def get_errors(form_errors):
    """Returns compiled form errors"""
    error_list = []
    errors = form_errors.as_data().copy()
    errors = [error_list.append(
        e + ': ' + str(
            list(errors[e][0])[0])) for e in errors]

    return list(set(error_list))
