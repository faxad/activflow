# djangoflow

[![Build Status](https://travis-ci.org/faxad/djangoflow.svg?branch=master)](https://travis-ci.org/faxad/djangoflow)
[![Coverage Status](https://coveralls.io/repos/github/faxad/djangoflow/badge.svg?branch=master)](https://coveralls.io/github/faxad/djangoflow?branch=master)
[![Code Health](https://landscape.io/github/faxad/djangoflow/master/landscape.svg?style=flat)](https://landscape.io/github/faxad/djangoflow/master)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/82d97392eecb4ffab85403390f6b25af)](https://www.codacy.com/app/fawadhq/djangoflow)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/2807a5b5bcdb46258ef0bcf7bb4e4d0f/badge.svg)](https://www.quantifiedcode.com/app/project/2807a5b5bcdb46258ef0bcf7bb4e4d0f)

### About
Description goes here...

### Technology Stack
- Python 2.7x, 3.4x, 3.5x
- Django 1.9x
- Bootstrap 3.x

### Usage & Configuration

#### Step 1: Workflow App Registration
- Add your workflow app to **WORKFLOW_APPS** under **core/constants**
```python
WORKFLOW_APPS = ['leave_request']
```

#### Step 2: Activity Configuration
- Activities must be configured as models
- Model representing initial Activity must take **AbstractInitialActivity** as base
- Models representing all other Activities must have **AbstractActivity** as base
- Custom validation logic must be defined under **clean()** on the activity model
- Custom field specific validation should be defined under **app/validator** and applied to the field as **validators** attribute
```python
from djangoflow.core.models import AbstractActivity, AbstractInitialActivity
from djangoflow.leave_request.validators import validate_initial_cap

class RequestInitiation(AbstractInitialActivity):
    """Leave request details"""
    employee_name = CharField("Employee", max_length=200, validators=[validate_initial_cap])
    from = DateField("From Date")
    to = DateField("To Date")
    reason = TextField("Leave Reason", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass

class ManagementApproval(AbstractActivity):
    """Management approval"""
    approval_status = CharField(verbose_name="Status", max_length=3, choices=(
        ('APP', 'Approved'), ('REJ', 'Rejected')))
    remarks = TextField("Thud")

    def clean(self):
        """Custom validation logic should go here"""
        pass

```
#### Step 3: Flow Definition
- Workflow configuration for Business Process should be defined as **FLOW** under **app/flow**
```python
from djangoflow.leave_request.models import RequestInitiation, ManagementApproval
from djangoflow.leave_request.rules import validate_request

FLOW = {
    'initiate_request': {
        'name': 'Leave Request Initiation',
        'model': RequestInitiation,
        'role': 'Submitter',
        'transitions': {
            'management_approval': validate_request,
        }
    },
    'management_approval': {
        'name': 'Management Approval',
        'model': ManagementApproval,
        'role': 'Approver',
        'transitions': None
    }
}

INITIAL = 'initiate_request'
```
#### Step 4: Rules
- All transition rules should be defined under **app/rules**
```python
def validate_request(self):
    return self.reason == 'Emergency'
```

#### Step 5: Configure Field Visibility
- Add **config.py** under your app and define **ACTIVITY_CONFIG** as Nested Ordered Dictionary
- Define the configuration for all activty models
- Define for each activity model the visbility of fields for display on templates and forms 
    - **create:** available on create form
    - **update:** available on update form
    - **display:** available for display in detail view
```python
from collections import OrderedDict as odict

ACTIVITY_CONFIG = odict([
    ('RequestInitiation', odict([
        ('employee_name', ['create', 'update', 'display']),
        ('from', ['create', 'update', 'display']),
        ('to', ['create', 'update', 'display']),
        ('reason', ['create', 'update', 'display']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
    ('ManagementApproval', odict([
        ('approval_status', ['create', 'update', 'display']),
        ('remarks', ['create', 'update', 'display']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
])

```

#### Step 6: Access/Permission Configuration
**AccessDeniedMixin** under **core/mixins** contains

