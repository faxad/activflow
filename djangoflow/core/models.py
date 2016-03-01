"""Model definition for CRUD operations"""

from importlib import import_module

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

    def submit(self, next):
        Task.objects.create(
            request=self,
            flow_ref_key=next,
            status='Not Started')


class Task(AbstractEntity):
    request = ForeignKey(Request, related_name='tasks')
    flow_ref_key = CharField(max_length=100)
    status = CharField(verbose_name="Status", max_length=30, choices=(
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Ended', 'Ended'))
    )

    @property
    def get_activity_title(self):
        try:
            return self.activity.title
        except AttributeError:
            name = apps.get_app_config(
                self.request.workflow_module_name).name
            flow = import_module(
                '{}.flow'.format(name)
            ).FLOW

            return flow[self.flow_ref_key]['model']().title

    def initiate(self):
        pass

    def submit(self, next=None):
        name = apps.get_app_config(
            self.request.workflow_module_name).name
        transitions = import_module(
            '{}.flow'.format(name)
        ).FLOW[self.flow_ref_key]['transitions']

        if transitions is not None:
            Task.objects.create(
                request=self.request,
                flow_ref_key=next,
                status='Not Started')
        else:
            pass
