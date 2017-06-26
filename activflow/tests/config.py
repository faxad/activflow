"""Activity Configuration"""

from collections import OrderedDict as odict


ACTIVITY_CONFIG = odict([
    ('Foo', odict([
        ('Fields', odict([
            ('subject', ['create', 'update', 'display']),
            ('bar', ['create', 'update', 'display']),
            ('baz', ['create', 'update', 'display']),
            ('qux', ['create', 'update', 'display']),
            ('creation_date', ['display']),
            ('last_updated', ['display'])
        ])),
        ('Relations', odict([
            ('FooLineItem', odict([
                ('plugh', ['create', 'update', 'display']),
                ('thud', ['create', 'update', 'display'])
            ])),
            ('FooMoreLineItem', odict([
                ('plughmore', ['create', 'update', 'display']),
                ('thudmore', ['create', 'update', 'display'])
            ]))
        ]))
    ])),
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
