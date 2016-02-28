"""Configure models for CRUD operations"""

from collections import OrderedDict as odict


CRUD_MODELS_CONFIG = odict([
    ('FirstActivity', odict([
        ('bar', ['create', 'update', 'display', 'preview']),
        ('baz', ['create', 'update', 'display', 'preview']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
    ('SecondActivity', odict([
        ('qux', ['create', 'update', 'display', 'preview']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
])
