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

    def filter(configuration):
        """Filter fields to display based on configuration"""
        for field_name in configuration:
            if option in configuration[field_name]:
                yield field_name

    def get_fields_from_config(model, instance, config):
        """Returns field/value pairs from configuration"""
        return OrderedDict([
            (
                model().class_meta.get_field(field_name).verbose_name,
                getattr(instance, field_name)
            )
            for field_name in itertools.islice(filter(config), len(config))
        ])

    def get_all_fields(instance, exclude=None):
        """Returns all field/value pairs on the model"""
        exclude = exclude or []
        fields = [field for field in (
            (
                field.name,
                field.verbose_name
            ) for field in instance.class_meta.get_fields()
        ) if field[0] not in ['id', 'task', 'task_id'] + exclude]
        return {field[1]: getattr(
            instance, field[0]) for field in fields}

    if _type == 'model':
        try:
            field_config = activity_config(
                app, model.__name__)['Fields']
            return get_fields_from_config(model, instance, field_config)
        except KeyError:
            return get_all_fields(instance)
    else:
        related_model_fields = {}
        for relation in model.class_meta.related_objects:
            related_model = relation.related_model
            for field in related_model.class_meta.fields:
                if all([
                    field.get_internal_type() == 'ForeignKey',
                    field.related_model == model]
                ):
                    instances = related_model.objects.filter(
                        **{field.name: instance})
                    try:
                        field_config = activity_config(
                            app,
                            model.__name__
                        )['Relations'][related_model.__name__]
                        relatd_items_detail = [get_fields_from_config(
                            related_model,
                            inst,
                            field_config
                        ) for inst in instances]
                    except KeyError:
                        relatd_items_detail = []
                        for inst in instances:
                            relatd_items_detail.append(
                                get_all_fields(inst, exclude=[field.name]))
            related_model_fields[related_model.__name__] = relatd_items_detail
        return related_model_fields


@register.assignment_tag(takes_context=True)
def wysiwyg_form_fields(context):
    """Returns activity data as in field/value pair"""
    app = context['app_title']
    model = context['entity_title']

    try:
        return wysiwyg_config(app, model)
    except (KeyError, AttributeError):
        return


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
