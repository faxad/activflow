"""Configure models for CRUD operations"""

from collections import OrderedDict as odict


CRUD_MODELS_CONFIG = odict([
    ('Foo', odict([
        ('bar', ['create', 'update', 'display', 'preview']),
        ('baz', ['create', 'update', 'display']),
        ('qux', ['create', 'update', 'display', 'preview']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
])
