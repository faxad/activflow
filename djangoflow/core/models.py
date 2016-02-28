"""Model definition for CRUD operations"""

from django.db.models import (
    Model,
    CharField,
    DateTimeField,
    ForeignKey)

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

    def submit(self):
        pass


class Task(AbstractEntity):
    request = ForeignKey(Request, related_name='tasks')
    status = CharField(verbose_name="Status", max_length=30, choices=(
        ('Not Started', 'Not Started'),
        ('In Progress', 'In Progress'),
        ('Ended', 'Ended'))
    )
