"""Model definition for test workflow"""

from django.db.models import (
    CharField,
    IntegerField,
    TextField)

from djangoflow.core.models import AbstractActivity, AbstractInitialActivity
from djangoflow.tests.validators import validate_initial_cap


class Foo(AbstractInitialActivity):
    """Sample representation of Foo activity"""
    bar = CharField("Bar", max_length=200, validators=[validate_initial_cap])
    baz = CharField(verbose_name="Baz", max_length=30, choices=(
        ('CR', 'Corge'), ('WL', 'Waldo')))
    qux = TextField("Qux", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass


class Corge(AbstractActivity):
    """Sample representation of Corge activity"""
    grault = CharField("Grault", max_length=50)
    thud = IntegerField("Thud")

    def clean(self):
        """Custom validation logic should go here"""
        pass
