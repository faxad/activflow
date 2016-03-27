# activflow

[![Build Status](https://travis-ci.org/faxad/ActivFlow.svg?branch=master)](https://travis-ci.org/faxad/ActivFlow)
[![Coverage Status](https://coveralls.io/repos/github/faxad/ActivFlow/badge.svg?branch=master)](https://coveralls.io/github/faxad/ActivFlow?branch=master)
[![Code Health](https://landscape.io/github/faxad/ActivFlow/master/landscape.svg?style=flat)](https://landscape.io/github/faxad/ActivFlow/master)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/f1cb2c6766cb4539ac1c3d4057996047)](https://www.codacy.com/app/fawadhq/ActivFlow)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/767844efa40e45e9b6e7689e37464272/badge.svg)](https://www.quantifiedcode.com/app/project/767844efa40e45e9b6e7689e37464272)

### Introduction
**ActivFlow** is a generic, light-weight and extensible workflow engine for agile development and automation of complex Business Process operations.

Developers can emphasize towards mapping the Business Process model as ActivFlow workflow without having to worry about implementing the core workflow processing logic. The generic implementation of the workflow engine manages the automation of the Business Processes from start to finish as per the defined configuration.

What defines an ActivFlow workflow?
- Business Process flow mapped as ActivFlow configuration
- Definition of data that needs to be captured for each activity (state)
- Business Roles mapped to workflow activities
- Rules for transitioning between activities

![alt tag](https://cloud.githubusercontent.com/assets/6130967/14062046/b055de98-f3a2-11e5-9d13-e74e4a9252f7.png)

### Technology Stack
- Python 2.7x, 3.4x, 3.5x
- Django 1.9x
- Bootstrap 3.x

### Usage & Configuration

#### Step 1: Workflow App Registration
- A Business Process must be represented in terms of a Django app
- All apps must be registered to **WORKFLOW_APPS** under **core/constants**
```python
WORKFLOW_APPS = ['leave_request']
```

#### Step 2: Activity Configuration
- Activities (States/Nodes) are represented as Django models
- **AbstractInitialActivity** should be the base for the initial activity
- **AbstractActivity** should be the base for all other activities
- Custom validation logic must be defined under **clean()** on the activity model
- Custom field specific validation should be defined under **app/validator** and applied to the field as **validators** attribute
```python
from activflow.core.models import AbstractActivity, AbstractInitialActivity
from activflow.leave_request.validators import validate_initial_cap

class RequestInitiation(AbstractInitialActivity):
    """Leave request details"""
    employee_name = CharField("Employee", max_length=200, validators=[validate_initial_cap])
    from = DateField("From Date")
    to = DateField("To Date")
    reason = TextField("Purpose of Leave", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass

class ManagementApproval(AbstractActivity):
    """Management approval"""
    approval_status = CharField(verbose_name="Status", max_length=3, choices=(
        ('APP', 'Approved'), ('REJ', 'Rejected')))
    remarks = TextField("Remarks")

    def clean(self):
        """Custom validation logic should go here"""
        pass

```
#### Step 3: Flow Definition
- A flow is represented by collection of Activities (States/Nodes) connected using Transitions (Edges)
- Rules are applied on transitions to allow switching from one activity to another provided the condition satisfies
- Business Process flow must be defined as **FLOW** under **app/flow**
- As a default behavior, the Role maps OTO with django Group (this can be customized by developers as per the requirements)
```python
from activflow.leave_request.models import RequestInitiation, ManagementApproval
from activflow.leave_request.rules import validate_request

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
#### Step 4: Business Rules
- Transition rules and conditions must be defined under **app/rules**
```python
def validate_request(self):
    return self.reason == 'Emergency'
```

#### Step 5: Configure Field Visibility (Optional)
- Include **config.py** in the workflow app and define **ACTIVITY_CONFIG** as Nested Ordered Dictionary if you want to have more control over what gets displayed.
- Define for each activity model the visibility of fields for display on templates and forms 
    - **create:** field will appear on activity create form
    - **update:** field will be available for activity update operation
    - **display:** available for display in activity detail view
```python
from collections import OrderedDict as odict

ACTIVITY_CONFIG = odict([
    ('RequestInitiation', odict([
        ('subject', ['create', 'update', 'display']),
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

#### Step 6: Access/Permission Configuration (Optional)
The logic for restricting the access is defined as **AccessDeniedMixin** under **core/mixins**
This can be customized by the developer based on the requirements

#### Demo Instructions
Execute the below command to configure ActivFlow for demo purpose
```
python demo.py
```
