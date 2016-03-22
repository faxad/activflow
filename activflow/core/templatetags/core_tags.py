"""Template Tags"""

import itertools
from importlib import import_module
from collections import OrderedDict

from django.apps import apps
from django import template

from activflow.core.constants import REQUEST_IDENTIFIER
from activflow.core.helpers import activity_config
from activflow.core.models import Task

register = template.Library()


@register.filter(is_safe=True)
def label_with_class(value, arg):
    """Style adjustments"""
    return value.label_tag(attrs={'class': arg})


@register.assignment_tag(takes_context=True)
def activity_data(context, instance, option):
    """Returns activity data as in field/value pair"""
    app = context['app_title']
    model = type(instance)
    config = activity_config(app, model.__name__)

    def compute(activity_config):
        """Compute fields for display"""
        for field_name in activity_config:
            if option in activity_config[field_name]:
                yield field_name

    return OrderedDict([(model().class_meta.get_field(
        field_name).verbose_name, getattr(
            instance, field_name)) for field_name in itertools.islice(
                compute(config), len(config))])


@register.simple_tag
def activity_title(ref, app):
    """Returns activity name"""
    return import_module(
        '{}.flow'.format(apps.get_app_config(app).name)
    ).FLOW[ref]['model']().title


@register.simple_tag
def request_instance(task_identifier):
    """Returns request instance"""
    return Task.objects.get(
        id=task_identifier
    ).request if task_identifier != REQUEST_IDENTIFIER else None
