"""Model definition for workflow operations"""

from django.contrib.auth.models import User, Group
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    OneToOneField,
    ForeignKey)

from djangoflow.core.helpers import flow_config
from djangoflow.core.mixins import BaseEntityMixin


class AbstractEntity(Model, BaseEntityMixin):
    """Common properties for all models"""
    creation_date = DateTimeField('Creation Date', auto_now_add=True)
    last_updated = DateTimeField('Last Updated', auto_now=True)

    @property
    def class_meta(self):
        """Returns class meta"""
        return self._meta

    @property
    def module_label(self):
        """Returns module label"""
        return self.class_meta.app_label

    def __unicode__(self):
        """Returns ID"""
        return str(self.id)

    class Meta(object):
        abstract = True


class Request(AbstractEntity):
    requester = ForeignKey(User, related_name='requests')
    status = CharField(verbose_name="Status", max_length=30, choices=(
        ('Initiated', 'Initiated'),
        ('Draft', 'Draft'),
        ('Submitted', 'Submitted'),
        ('Withdrawn', 'Withdrawn'),
        ('Completed', 'Completed'))
    )

    @property
    def workflow_module(self):
        return (self.tasks.first().class_meta.
                get_all_related_objects()[0].related_model())

    def submit(self, next):
        pass


class Task(AbstractEntity):
    request = ForeignKey(Request, related_name='tasks')
    assignee = ForeignKey(Group)
    updated_by = ForeignKey(User)
    flow_ref_key = CharField(max_length=100)
    status = CharField(verbose_name="Status", max_length=30, choices=(
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Ended', 'Ended'))
    )

    @property
    def activity(self):
        module = self.request.workflow_module.module_label
        flow = flow_config(module).FLOW
        return getattr(
            self, flow[self.flow_ref_key]['model']().title.lower(), None)

    def initiate(self):
        self.status = 'In Progress'
        self.save()

    def submit(self, module, next=None):
        transitions = flow_config(
            module).FLOW[self.flow_ref_key]['transitions']

        self.status = 'Ended'
        self.save()

        if transitions is not None:
            Task.objects.create(
                request=self.request,
                flow_ref_key=next,
                status='Not Started')
        else:
            self.request.status = 'Completed'
            self.request.save()


class AbstractActivity(AbstractEntity):
    """Common properties for all models"""
    task = OneToOneField(Task)

    @property
    def is_initial(self):
        """Checks if the activity is initial activity"""
        config = flow_config(self.module_label)
        return True if self.title == config.FLOW[
            config.INITIAL]['model']().title else False

    def next(self):
        """Compute the next possible activities"""
        transitions = flow_config(self.module_label).FLOW[
            self.task.flow_ref_key]['transitions']
        if transitions:
            return [transition for transition in
                    transitions if transitions[transition](self)]
        else:
            return None

    def initiate_request(self):
        """Initiates new workflow requests"""
        request = Request.objects.create(
            status='Initiated')

        task = Task.objects.create(
            request=request,
            flow_ref_key='first_activity',
            status='In Progress')

        self.task = task
        self.save()

    class Meta(object):
        abstract = True
