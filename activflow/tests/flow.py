# flow

from activflow.tests.models import Foo, Corge
from activflow.tests.rules import foo_to_corge


FLOW = {
    'foo_activity': {
        'name': 'Foo Activity',
        'model': Foo,
        'role': 'Submitter',
        'transitions': {
            'corge_activity': foo_to_corge,
        }
    },
    'corge_activity': {
        'name': 'Corge Activity',
        'model': Corge,
        'role': 'Reviewer',
        'transitions': None
    }
}

INITIAL = 'foo_activity'
