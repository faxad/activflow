"""Core workflow configuration/constants"""

REQUEST_IDENTIFIER = 'Initial'

REQUEST_STATUS = (
    ('Initiated', 'Initiated'),
    ('Withdrawn', 'Withdrawn'),
    ('Completed', 'Completed')
)

TASK_STATUS = (
    ('Not Started', 'Not Started'),
    ('In Progress', 'In Progress'),
    ('Rolled Back', 'Rolled Back'),
    ('Completed', 'Completed')
)
# register workflow apps here
# enable 'tests' app only for manual testing purpose

WORKFLOW_APPS = [
    'tests'
]
