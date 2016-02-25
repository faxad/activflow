"""Core CRUD configuration/constants"""

CRUD_OPERATIONS = {
    'create': 'add',
    'update': 'change',
    'delete': 'delete',
    'list': 'view',
    'detail': 'view'
    }

# register apps for CRUD operations
# enable 'tests' app only for manual testing purpose

WORKFLOW_APPS = [
    'sample'
]
