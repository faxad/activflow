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
    """Common attributes for all models"""
    creation_date = DateTimeField('Creation Date', auto_now_add=True)
    last_updated = DateTimeField('Last Updated', auto_now=True)

    class Meta:
        abstract = True

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


class Request(AbstractEntity):
    """Defines the workflow request"""
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


class Task(AbstractEntity):
    """Defines the workflow task"""
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
        """Returns the activity associated with the task"""
        module = self.request.workflow_module.module_label
        flow = flow_config(module).FLOW
        return getattr(
            self, flow[self.flow_ref_key]['model']().title.lower(), None)

    @property
    def is_active(self):
        """Checks if the current task is active / most recent"""
        return self == self.request.tasks.latest('id')

    def initiate(self):
        """Initializes the task"""
        self.status = 'In Progress'
        self.save()

    def submit(self, module, user, next=None):
        """Submits the task"""
        config = flow_config(module)
        transitions = config.FLOW[self.flow_ref_key]['transitions']
        role = Group.objects.get(
            name=config.FLOW[next]['role'])

        self.status = 'Ended'
        self.save()

        if transitions is not None:
            Task.objects.create(
                request=self.request,
                assignee=role,
                updated_by=user,
                flow_ref_key=next,
                status='Not Started')
        else:
            self.request.status = 'Completed'
            self.request.save()


class AbstractActivity(AbstractEntity):
    """Common attributes for all activities"""
    task = OneToOneField(Task)

    class Meta:
        abstract = True

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

    def assign_task(self, identifier):
        """Link activity with task"""
        self.task = Task.objects.get(id=identifier)
        self.save()


class AbstractInitialActivity(AbstractActivity):
    """Common attributes for initial activity"""

    class Meta:
        abstract = True

    def initiate_request(self, user):
        """Initiates new workflow requests"""
        config = flow_config(self.module_label)
        role = Group.objects.get(
            name=config.FLOW[config.INITIAL]['role'])

        request = Request.objects.create(
            requester=user,
            status='Initiated')

        task = Task.objects.create(
            request=request,
            assignee=role,
            updated_by=user,
            flow_ref_key=config.INITIAL,
            status='In Progress')

        self.task = task
        self.save()
