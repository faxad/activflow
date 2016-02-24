"""Test model definition for CRUD operations"""

from django.db.models import (
    CharField,
    TextField)

from djangoflow.core.mixins import BaseEntityMixin
from djangoflow.core.models import AbstractEntity
from djangoflow.tests.validators import validate_initial_cap


class Foo(AbstractEntity, BaseEntityMixin):
    """Sample representation of Foo"""
    bar = CharField("Bar", max_length=200, validators=[validate_initial_cap])
    baz = CharField(verbose_name="Baz", max_length=30, choices=(
        ('CR', 'Corge'), ('WL', 'Waldo')))
    qux = TextField("Qux", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass
