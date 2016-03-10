"""Core CRUD configuration/constants"""

CRUD_OPERATIONS = {
    'create': 'add',
    'update': 'change',
    'delete': 'delete',
    'list': 'view',
    'detail': 'view'
    }

INITIAL_REQUEST_IDENTIFIER = 'Initial'

# register apps for CRUD operations
# enable 'tests' app only for manual testing purpose

WORKFLOW_APPS = [
    'sample'
]
