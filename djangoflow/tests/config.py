"""Configure models for CRUD operations"""

from collections import OrderedDict as odict


ACTIVITY_CONFIG = odict([
    ('Foo', odict([
        ('bar', ['create', 'update', 'display', 'preview']),
        ('baz', ['create', 'update', 'display', 'preview']),
        ('qux', ['create', 'update', 'display', 'preview']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
    ('Corge', odict([
        ('grault', ['create', 'update', 'display', 'preview']),
        ('thud', ['create', 'update', 'display', 'preview']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
])
