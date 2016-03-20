"""Activity Configuration"""

from collections import OrderedDict as odict


ACTIVITY_CONFIG = odict([
    ('Foo', odict([
        ('bar', ['create', 'update', 'display']),
        ('baz', ['create', 'update', 'display']),
        ('qux', ['create', 'update', 'display']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
    ('Corge', odict([
        ('grault', ['create', 'update', 'display']),
        ('thud', ['create', 'update', 'display']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
])
