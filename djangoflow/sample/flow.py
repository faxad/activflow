# flow

from djangoflow.sample.models import (
    FirstActivity,
    SecondActivity
)

from djangoflow.sample.rules import first_to_second


FLOW = {
    'first_activity': {
        'name': 'First Activity',
        'model': FirstActivity,
        'role': None,
        'transitions': {
            'second_activity': first_to_second,
        }
    },
    'second_activity': {
        'name': 'Second Activity',
        'model': SecondActivity,
        'role': None,
        'transitions': None
    }
}
