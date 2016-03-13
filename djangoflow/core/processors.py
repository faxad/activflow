"""Common template processors"""

from djangoflow.core.helpers import get_request_params


def global_context(request):
    """Returns the title of the model"""
    def get_value(key): return get_request_params(key, request)

    return {
        'entity_title': get_value('model_name'),
        'app_title': get_value('app_name'),
        'identifier': get_value('pk')
    }
