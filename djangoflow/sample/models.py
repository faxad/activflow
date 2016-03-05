"""Test model definition for CRUD operations"""

from django.db.models import (
    CharField,
    ForeignKey,
    OneToOneField,
    TextField)

from djangoflow.core.mixins import BaseEntityMixin
from djangoflow.core.models import AbstractEntity, AbstractActivity, Request, Task
from djangoflow.tests.validators import validate_initial_cap



class FirstActivity(AbstractEntity, AbstractActivity):
    """Sample first activity"""
    task = OneToOneField(Task)
    bar = CharField("Bar", max_length=200, validators=[validate_initial_cap])
    baz = CharField(verbose_name="Baz", max_length=30, choices=(
        ('CR', 'Corge'), ('WL', 'Waldo')))

    def clean(self):
        """Custom validation logic should go here"""
        pass


class SecondActivity(AbstractEntity, AbstractActivity):
    """Sample second activity"""
    task = OneToOneField(Task)
    qux = TextField("Qux", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass
