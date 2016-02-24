# djangoflow

[![Build Status](https://travis-ci.org/faxad/djangoflow.svg?branch=master)](https://travis-ci.org/faxad/djangoflow)
[![Coverage Status](https://coveralls.io/repos/github/faxad/djangoflow/badge.svg?branch=master)](https://coveralls.io/github/faxad/djangoflow?branch=master)
[![Code Health](https://landscape.io/github/faxad/djangoflow/master/landscape.svg?style=flat)](https://landscape.io/github/faxad/djangoflow/master)
[![Codacy Badge](https://api.codacy.com/project/badge/grade/82d97392eecb4ffab85403390f6b25af)](https://www.codacy.com/app/fawadhq/djangoflow)
[![Code Issues](https://www.quantifiedcode.com/api/v1/project/2807a5b5bcdb46258ef0bcf7bb4e4d0f/badge.svg)](https://www.quantifiedcode.com/app/project/2807a5b5bcdb46258ef0bcf7bb4e4d0f)

### About
The intention was to develop a generic framework for rapid development of CRUD based web applications. The framework simplifies the development process by relying only on Model creation. The generic framework takes care of providing the necessary Views, Templates, Forms and URLs.

Additionally, a simple configuration allows the developer to specify what fields to display in Create, Update, Display and Preview operations.

### Technology Stack
- Python 2.7x, 3.4x, 3.5x
- Django 1.9x
- Bootstrap 3.x

### Usage & Configuration

#### Step 1: App Registration for CRUD Operations
- Add your app to **CRUD_APPS** under **core/constants**
- Comment out the **tests** app (for demo purpose only)
```python
CRUD_APPS = [
    'tests',
    'procurement_logistics'
]
```
#### Step 2: Model Configuration
- All models must inherit from **AbstractEntity** and use the **BaseEntityMixin**
```python
from djangoflow.core.mixins import BaseEntityMixin
from djangoflow.core.models import AbstractEntity

class Supplier(AbstractEntity, BaseEntityMixin):
    """Sample representation of Supplier"""
    name = CharField("Name", max_length=200, validators=[validate_name])
    category = CharField(verbose_name="Category/Type", max_length=10, choices=(
        ('PB', 'Public'), ('PR', 'Private')))
    remarks = TextField("Remarks", blank=True)

    def clean(self):
        """Custom validation logic should go here"""
        pass
```
#### Step 3: Define Validation Logic (Optional)
- Custom validation logic should go under **clean()** on the model itself
- Custom field specific validation should be defined and applied to the field as **validators** attribute

#### Step 4: Configure Field Visibility
- Add **crud.py** under your app and define **FIELD_CONFIG** as Nested Ordered Dictionary
- Include the models which you want to be exposed for CRUD operations
- Define for each model the visbility of fields for display on the templates and forms 
    - **create:** available on create form
    - **update:** available on update form
    - **display:** available for display in detail view
    - **preview:** available for display in list view
```python
FIELD_CONFIG = odict([
    ('Supplier', odict([
        ('name', ['create', 'update', 'display', 'preview']),
        ('category', ['create', 'update', 'display']),
        ('remarks', ['create', 'update', 'display', 'preview']),
        ('creation_date', ['display']),
        ('last_updated', ['display'])
    ])),
])
```

#### Step 5: Configure Permissions
Execute the following management command to configure the permissions
- ./manage.py configauth
