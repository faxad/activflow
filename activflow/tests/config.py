"""Activity Configuration"""

from collections import OrderedDict as odict


ACTIVITY_CONFIG = odict([
    ('Foo', odict([
        ('subject', ['create', 'update', 'display']),
        ('bar', ['create', 'update', 'display']),
        ('baz', ['create', 'update', 'display']),
        ('qux', ['create', 'update', 'display']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
    # ('Corge', odict([
    #     ('grault', ['create', 'update', 'display']),
    #     ('thud', ['create', 'update', 'display']),
    #     ('creation_date', ['display']),
    #     ('last_updated', ['display'])
    # ])),
])

#  config for Corge commented out to demonstrate that config is optional

# field configuration for WYSIWYG editor

WYSIWYG_CONFIG = {
    'Foo': ['qux']
}

# custom form registration

FORM_CONFIG = {
    'Foo': 'CustomForm'
}
