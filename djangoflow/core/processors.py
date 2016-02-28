"""Common template processors"""

from djangoflow.core.helpers import (
    get_model_name,
    get_app_name,
    get_request_task_id
)


def global_context(request):
    """Returns the title of the model"""
    return {
        'entity_title': get_model_name(request),
        'app_title': get_app_name(request),
        'identifier': get_request_task_id(request)
    }
