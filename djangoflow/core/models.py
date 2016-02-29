"""Model definition for CRUD operations"""

from django.apps import apps
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    ForeignKey)

from djangoflow.core.mixins import BaseEntityMixin
from djangoflow.core.constants import WORKFLOW_APPS
from django.forms.models import modelform_factory


class AbstractEntity(Model, BaseEntityMixin):
    """Common properties for all models"""
    creation_date = DateTimeField('Creation Date', auto_now_add=True)
    last_updated = DateTimeField('Last Updated', auto_now=True)

    @property
    def class_meta(self):
        """Returns class meta"""
        return self._meta

    @property
    def is_initial_activity(self):
        """Returns true if is initial activity"""
        return True if self.title.startswith('First') else False

    def __unicode__(self):
        """Returns ID"""
        return str(self.id)

    class Meta(object):
        abstract = True


class Request(AbstractEntity):
    status = CharField(verbose_name="Status", max_length=30, choices=(
        ('Initiated', 'Initiated'),
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Withdrawn', 'Withdrawn'),
        ('Completed', 'Completed'))
    )

    @property
    def workflow_module_name(self):
        return self.activity.class_meta.app_label

    def submit(self):
        pass


class Task(AbstractEntity):
    request = ForeignKey(Request, related_name='tasks')
    flow_ref_key = CharField(max_length=100)
    status = CharField(verbose_name="Status", max_length=30, choices=(
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Ended', 'Ended'))
    )

    # @property
    # def discovered_activity(self):
    #     name = apps.get_app_config(
    #         self.request.workflow_module_name).name
    #     discovered = import_module(
    #         '{}.flow'.format(name)
    #     ).FLOW
