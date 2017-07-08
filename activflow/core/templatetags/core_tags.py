"""Template Tags"""

import itertools
from importlib import import_module
from collections import OrderedDict

from django.apps import apps
from django import template

from activflow.core.constants import REQUEST_IDENTIFIER
from activflow.core.helpers import (
    activity_config,
    wysiwyg_config
)

from activflow.core.models import Task

register = template.Library()


@register.filter(is_safe=True)
def label_with_class(value, arg):
    """Style adjustments"""
    return value.label_tag(attrs={'class': arg})


@register.assignment_tag(takes_context=True)
def activity_data(context, instance, option, _type):
    """Returns activity data as in field/value pair"""
    app = context['app_title']
    model = type(instance)

    def compute(configuration):
        """Compute fields for display"""
        for field_name in configuration:
            if option in configuration[field_name]:
                yield field_name

    def get_field_value_pairs(model, instance, config):
        """Returns field/value pairs"""
        return OrderedDict([(model().class_meta.get_field(
            field_name).verbose_name, getattr(
                instance, field_name)) for field_name in itertools.islice(
                    compute(config), len(config))])

    if _type == 'model':
        try:
            field_config = activity_config(app, model.__name__)['Fields']
            return get_field_value_pairs(model, instance, field_config)
        except KeyError:
            fields = [field for field in (
                (field.name, field.verbose_name) for field in instance.class_meta.
                get_fields()) if field[0] not in ['id', 'task', 'task_id']]
            return {field[1]: getattr(
                instance, field[0]) for field in fields}
    else:
        try:
            related_model_fields = {} 
            relation_config = activity_config(app, model.__name__)['Relations']
            for relation in relation_config:
                related_model = apps.get_model(app, relation)
                for field in related_model._meta.fields:
                    if field.get_internal_type() == 'ForeignKey' and field.related_model == model:
                        instances = related_model.objects.filter(
                            **{ field.name: instance })
                        related_model_fields[relation] = [get_field_value_pairs(
                            related_model, instance, relation_config[relation]) for instance in instances]
                        break
            return related_model_fields
        except KeyError:
            pass # TODO: handle case where no explicit configuration is specified


@register.assignment_tag(takes_context=True)
def wysiwyg_form_fields(context):
    """Returns activity data as in field/value pair"""
    app = context['app_title']
    model = context['entity_title']

    try:
        return wysiwyg_config(app, model)
    except (KeyError, AttributeError):
        return None


@register.simple_tag
def activity_title(ref, app):
    """Returns activity name"""
    return import_module(
        '{}.flow'.format(apps.get_app_config(app).name)
    ).FLOW[ref]['model']().title


@register.simple_tag
def activity_friendly_name(ref, app):
    """Returns activity friendly name"""
    return import_module(
        '{}.flow'.format(apps.get_app_config(app).name)
    ).FLOW[ref]['name']


@register.simple_tag
def request_instance(task_identifier):
    """Returns request instance"""
    return Task.objects.get(
        id=task_identifier
    ).request if task_identifier != REQUEST_IDENTIFIER else None
