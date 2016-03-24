"""Common template processors"""

from activflow.core.helpers import (
    get_request_params,
    flow_config
)


def global_context(request):
    """Sets up global template context"""
    def get_value(key):
        """Returns value against specified key"""
        return get_request_params(key, request)

    app_title = get_value('app_name')
    activity_identifier = get_value('model_name')

    try:
        flow = flow_config(app_title).FLOW
        activity_title = flow[
            [identifier for identifier in flow if flow[identifier][
                'model']().title == activity_identifier][0]]['name']
    except (IndexError, LookupError):
        activity_title = None

    return {
        'entity_title': activity_identifier,
        'app_title': app_title,
        'identifier': get_value('pk'),
        'activity_title': activity_title
    }
