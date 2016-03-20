"""Mixins"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render

from djangoflow.core.constants import REQUEST_IDENTIFIER
from djangoflow.core.helpers import (
    get_model,
    flow_config,
    get_request_params
)


class BaseEntityMixin(object):
    """Properties and methods that apply to all
    models defined under core
    """
    @property
    def title(self):
        """Returns entity title"""
        return self.__class__.__name__


class AccessDeniedMixin(LoginRequiredMixin, object):
    """Checks the permission"""
    def check(self, request, **kwargs):
        """
        - Super user can perform all activities
        - Requester can view all activities
        - TODO: Historical activities cannot be updated
        - TODO: Entire request can be deleted
        - Task assignee can update activity
        - Task assignee can perform rollback
        """
        model = get_model(**kwargs)
        view = self.__class__.__name__
        user = request.user
        groups = list(user.groups.all())

        if self.request.user.is_superuser:
            return

        @property
        def is_user_an_assingee():
            model.objects.filter(task__assignee__in=groups).count() != 0

        def check_for_view():
            return model.objects.filter(
                Q(task__assignee__in=groups) |
                Q(task__request__requester=user)
            ).count() != 0

        def check_for_create():
            module = get_request_params('app_name', request, **kwargs)
            flow = flow_config(module).FLOW
            initial = flow_config(module).INITIAL
            activity = initial if get_request_params(
                'pk', request, **kwargs
            ) == REQUEST_IDENTIFIER else self.task.flow_ref_key
            return flow[activity]['role'] in [group.name for group in groups]

        def check_for_update():
            return is_user_an_assingee

        def check_for_rollback():
            return is_user_an_assingee

        return None if {
            'ViewActivity': check_for_view,
            'CreateActivity': check_for_create,
            'UpdateActivity': check_for_update,
            'RollBackActivity': check_for_rollback,
        }.get(view)() else render(request, 'core/denied.html')
