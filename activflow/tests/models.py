"""Model definition for test workflow"""

from django.db.models import (
    CharField,
    ForeignKey,
    IntegerField,
    TextField,
    CASCADE)

from activflow.core.models import (
    AbstractEntity,
    AbstractActivity,
    AbstractInitialActivity)

from activflow.tests.validators import validate_initial_cap


class Foo(AbstractInitialActivity):
    """Sample representation of Foo activity"""
    bar = CharField("Bar", max_length=200, validators=[validate_initial_cap])
    baz = CharField(verbose_name="Baz", max_length=30, choices=(
        ('CR', 'Corge'), ('WL', 'Waldo')))
    qux = TextField("Qux", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass


class FooLineItem(AbstractEntity):
    """Sample representation of Foo Line Item"""
    foo = ForeignKey(Foo, related_name="lines", on_delete=CASCADE)
    plugh = CharField(
        "Plugh", max_length=200, validators=[validate_initial_cap])
    thud = CharField(verbose_name="Thud", max_length=30, choices=(
        ('GR', 'Grault'), ('GA', 'Garply')))

    @property
    def title(self):
        """Returns entity title"""
        return self.__class__.__name__

    def clean(self):
        """Custom validation logic should go here"""
        pass


class FooMoreLineItem(AbstractEntity):
    """Sample representation of FooMore Line Item"""
    foo = ForeignKey(Foo, related_name="morelines", on_delete=CASCADE)
    plughmore = CharField(
        "Plughmore", max_length=200, validators=[validate_initial_cap])
    thudmore = CharField(verbose_name="Thudmore", max_length=30, choices=(
        ('GR', 'Grault'), ('GA', 'Garply')))

    @property
    def title(self):
        """Returns entity title"""
        return self.__class__.__name__

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
