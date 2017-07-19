# activflow
[![Build Status](https://travis-ci.org/faxad/ActivFlow.svg?branch=master)](https://travis-ci.org/faxad/ActivFlow)
[![Coverage Status](https://coveralls.io/repos/github/faxad/ActivFlow/badge.svg?branch=master)](https://coveralls.io/github/faxad/ActivFlow?branch=master)
[![Code Health](https://landscape.io/github/faxad/ActivFlow/master/landscape.svg?style=flat)](https://landscape.io/github/faxad/ActivFlow/master)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/f1cb2c6766cb4539ac1c3d4057996047)](https://www.codacy.com/app/fawadhq/ActivFlow)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/767844efa40e45e9b6e7689e37464272/badge.svg)](https://www.quantifiedcode.com/app/project/767844efa40e45e9b6e7689e37464272)

### Introduction
**ActivFlow** is a generic, light-weight and extensible workflow engine for agile development and automation of complex Business Process operations.

Developers can emphasize towards mapping the Business Process model as ActivFlow workflow without having to worry about implementing the core workflow processing logic. The generic implementation of the workflow engine manages the automation of the Business Processes from start to finish in accordance with the defined flow.

What is an ActivFlow workflow?
- Business Process flow mapped as ActivFlow configuration
- Definition of data to be captured for each activity (state)
- Business Roles mapped to workflow activities
- Rules applied on transitions between activities

![alt tag](https://user-images.githubusercontent.com/6130967/28086399-5625a4e8-6698-11e7-8a00-ccf3180d70be.png)

### Technology Stack
- Python 2.7x, 3.4x, 3.5x, 3.6x
- Django 1.9x, 1.10x, 1.11x
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
- Activity must inherit from **AbstractInitialActivity**/**AbstractActivity** respectively
- Custom validation logic must be defined under **clean()** on the activity model
- Custom field specific validation should go under **app/validator** and applied to the field as **validators** attribute
```python
from activflow.core.models import AbstractActivity, AbstractInitialActivity, AbstractEntity
from activflow.leave_request.validators import validate_initial_cap

class SampleRequest(AbstractInitialActivity):
    """Sample leave request details"""
    employee_name = CharField("Employee", max_length=200, validators=[validate_initial_cap])
    from = DateField("From Date")
    to = DateField("To Date")
    reason = TextField("Purpose of Leave", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass

class Itinerary(AbstractEntity):
    """Itinerary details"""
    request = ForeignKey(RequestInitiation, related_name="itineraries")
    destination = CharField("Destination", max_length=200)
    date = DateField("Visit Date")

    def clean(self):
        """Custom validation logic should go here"""
        pass

class ManagementReview(AbstractActivity):
    """Management review/approval"""
    approval_status = CharField(verbose_name="Status", max_length=3, choices=(
        ('APP', 'Approved'), ('REJ', 'Rejected')))
    remarks = TextField("Remarks")

    def clean(self):
        """Custom validation logic should go here"""
        pass

```
#### Step 3: Flow Definition
- A flow is represented by collection of Activities (States/Nodes) connected using Transitions (Edges)
- Rules are applied on transitions to allow routing between activities, provided, the condition satisfies
- Business Process flow must be defined as **FLOW** under **app/flow**
- As a default behavior, the Role maps OTO with django Group (developers, feel free to customize)
```python
from activflow.leave_request.models import SampleRequest, ManagementReview
from activflow.leave_request.rules import validate_request

FLOW = {
    'sample_leave_request': {
        'name': 'Sample Request',
        'model': SampleRequest,
        'role': 'Submitter',
        'transitions': {
            'management_review': validate_request,
        }
    },
    'management_review': {
        'name': 'Management's Review',
        'model': ManagementReview,
        'role': 'Approver',
        'transitions': None
    }
}

INITIAL = 'sample_leave_request'
```
#### Step 4: Business Rules
- Transition rules and conditions must be defined under **app/rules**
```python
def validate_request(self):
    return self.reason == 'Emergency'
```

#### Step 5: Configure Field Visibility & Custom Forms (Optional)
- Include **config.py** in the workflow app and define **ACTIVITY_CONFIG** as Nested Ordered Dictionary to have more control over what gets displayed on the UI.
- Define for each activity model, the visibility of fields, for display on templates and forms 
    - **create:** field will appear on activity create/initiate form
    - **update:** field will be available for activity update/revise operation
    - **display:** available for display in activity detail view
```python
from collections import OrderedDict


ACTIVITY_CONFIG = OrderedDict([
    ('Foo', OrderedDict([
        ('Fields', OrderedDict([
            ('subject', ['create', 'update', 'display']),
            ('employee_name', ['create', 'update', 'display']),
            ('from', ['create', 'update', 'display']),
            ('to', ['create', 'update', 'display']),
            ('reason', ['create', 'update', 'display']),
            ('creation_date', ['display']),
            ('last_updated', ['display'])
        ])),
        ('Relations', OrderedDict([
            ('Itinerary', OrderedDict([
                ('destination', ['create', 'update', 'display']),
                ('date', ['create', 'update', 'display'])
            ])),
            ...
            ...
        ]))
    ])),
    ...
    ...
])

# register fields that need WYSIWYG editor

WYSIWYG_CONFIG = {
    'RequestInitiation': ['reason']
}

# register custom forms

FORM_CONFIG = {
    'RequestInitiation': 'CustomRequestForm'
}
```

#### Step 6: Access/Permission Configuration (Optional)
The core logic to restrict access is defined as **AccessDeniedMixin** under **core/mixins** which developers can customize depending on the requirements

#### Demo Instructions
Execute the below command to configure ActivFlow for demo purpose
```
python demo.py
```
**Submitter:** john.doe/12345, **Reviewer:** jane.smith/12345
