"""Model definition for workflow operations"""

from django.contrib.auth.models import User, Group
from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    OneToOneField,
    ForeignKey,
    CASCADE)

from activflow.core.constants import (
    REQUEST_STATUS,
    TASK_STATUS)

from activflow.core.helpers import (
    flow_config,
    transition_config)


class AbstractEntity(Model):
    """Common attributes for all models"""
    creation_date = DateTimeField('Creation Date', auto_now_add=True)
    last_updated = DateTimeField('Last Updated', auto_now=True)

    class Meta(object):
        abstract = True

    @property
    def class_meta(self):
        """Returns class meta"""
        return self._meta

    @property
    def title(self):
        """Returns entity title"""
        return self.__class__.__name__

    @property
    def module_label(self):
        """Returns module label"""
        return self.class_meta.app_label

    @property
    def code(self):
        """Returns a unique code"""
        return "{0}-{1}-{2}".format(
            self.class_meta.app_label,
            self.title,
            self.id)

    def __unicode__(self):
        """Returns ID"""
        return str(self.id)


class Request(AbstractEntity):
    """Defines the workflow request"""
    requester = ForeignKey(User, related_name='requests', on_delete=CASCADE)
    module_ref = CharField(max_length=100)
    status = CharField(
        verbose_name="Status", max_length=30, choices=REQUEST_STATUS)


class Task(AbstractEntity):
    """Defines the workflow task"""
    request = ForeignKey(Request, related_name='tasks', on_delete=CASCADE)
    assignee = ForeignKey(Group, on_delete=CASCADE)
    updated_by = ForeignKey(User, on_delete=CASCADE)
    activity_ref = CharField(max_length=100)
    status = CharField(
        verbose_name="Status", max_length=30, choices=TASK_STATUS)

    @property
    def activity(self):
        """Returns the activity associated with the task"""
        flow = flow_config(self.request.module_ref).FLOW
        return getattr(
            self, flow[self.activity_ref]['model']().title.lower(), None)

    @property
    def is_active(self):
        """Checks if the current task is active / most recent"""
        return self == self.request.tasks.latest('id')

    @property
    def is_final(self):
        """Checks if the current task is final / end task"""
        transitions = transition_config(
            self.request.module_ref, self.activity_ref)

        return not transitions

    @property
    def previous(self):
        """Returns previous task"""
        return Task.objects.filter(
            request=self.request, id__lt=self.id).latest('id')

    @property
    def can_view_activity(self):
        """Checks if activity can be viewed"""
        return self.activity

    @property
    def can_initiate_activity(self):
        """Checks if new activity can be initiated"""
        return not self.activity

    @property
    def can_revise_activity(self):
        """Checks if activity can be revised"""
        return all([self.activity, self.is_active])

    @property
    def can_rollback(self):
        """Checks if activity can be rolled back"""
        return not any([
            self.activity.is_initial,
            self.status == 'Completed'])

    def initiate(self):
        """Initializes the task"""
        self.status = 'In Progress'
        self.save()

    def submit(self, module, user, next_activity=None):
        """Submits the task"""
        config = flow_config(module)
        transitions = transition_config(module, self.activity_ref)
        role = Group.objects.get(
            name=config.FLOW[next_activity]['role'])

        self.status = 'Completed'
        self.save()

        if transitions is not None:
            Task.objects.create(
                request=self.request,
                assignee=role,
                updated_by=user,
                activity_ref=next_activity,
                status='Not Started')
        else:
            self.request.status = 'Completed'
            self.request.save()

    def rollback(self):
        """Rollback to previous task"""
        previous = self.previous
        previous.status = 'Rolled Back'
        previous.save()
        self.status = 'Rolled Back'
        self.save()

        # Clone Task
        task = self.previous
        task.id = None
        task.status = 'Not Started'
        task.save()

        # Clone Activity
        activity = self.previous.activity
        activity.id = None
        activity.task = task
        activity.save()


class AbstractActivity(AbstractEntity):
    """Common attributes for all activities"""
    task = OneToOneField(Task, null=True, on_delete=CASCADE)

    class Meta(object):
        abstract = True

    @property
    def is_initial(self):
        """Checks if the activity is initial activity"""
        config = flow_config(self.module_label)
        return True if self.title == config.FLOW[
            config.INITIAL]['model']().title else False

    def next_activity(self):
        """Compute the next possible activities"""
        transitions = transition_config(
            self.module_label, self.task.activity_ref)

        return [transition for transition in
                transitions if transitions[transition](
                    self)] if transitions else None

    def validate_rule(self, identifier):
        """Validates the rule for the current
        transition"""
        transitions = transition_config(
            self.module_label, self.task.activity_ref)

        return transitions[identifier](self)

    def assign_task(self, identifier):
        """Link activity with task"""
        self.task = Task.objects.get(id=identifier)
        self.save()

    def update(self):
        """On activity save"""
        self.task.status = 'In Progress'
        self.task.save()

    def finish(self):
        """On activity finish"""
        self.task.status = 'Completed'
        self.task.save()
        self.task.request.status = 'Completed'
        self.task.request.save()


class AbstractInitialActivity(AbstractActivity):
    """Common attributes for initial activity"""
    subject = CharField(verbose_name="Subject", max_length=70)

    class Meta(object):
        abstract = True

    def initiate_request(self, user, module):
        """Initiates new workflow requests"""
        config = flow_config(self.module_label)
        role = Group.objects.get(
            name=config.FLOW[config.INITIAL]['role'])

        request = Request.objects.create(
            requester=user,
            module_ref=module,
            status='Initiated')

        task = Task.objects.create(
            request=request,
            assignee=role,
            updated_by=user,
            activity_ref=config.INITIAL,
            status='In Progress')

        self.task = task
        self.save()


def get_workflows_requests(module):
    """Returns all requests for specified workflow"""
    return Request.objects.filter(module_ref=module)


def get_task(identifier):
    """Returns task instance"""
    return Task.objects.get(id=identifier)
