"""Mixins"""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render

from activflow.core.constants import REQUEST_IDENTIFIER
from activflow.core.helpers import (
    get_model,
    flow_config,
    get_request_params
)

from activflow.core.models import Task


class AccessDeniedMixin(LoginRequiredMixin, object):
    """Checks the permission"""
    def check(self, request, **kwargs):
        """
        - Super user can perform all activities
        - Requester can view all activities
        - Assignee can view all assigned activities
        - Assignee can initiate activity operation
        - Assignee can update activity details
        - Historical activities cannot be updated
        - TODO: Entire request can be deleted

        *assignee: Users who belong to a Group configured to play
         a specific role in the Business Process
        """
        model = get_model(**kwargs)
        view = self.__class__.__name__
        user = request.user
        groups = list(user.groups.all())

        if self.request.user.is_superuser:
            return

        def assignee_check():
            """Checks if logged-in user is task assignee"""
            return model.objects.filter(task__assignee__in=groups).count() == 0

        def check_for_view():
            """Check for view/display operation"""
            return model.objects.filter(
                Q(task__assignee__in=groups) |
                Q(task__request__requester=user)
            ).count() == 0

        def check_for_create():
            """Check for create/initiate operation"""
            module = get_request_params('app_name', request, **kwargs)
            flow = flow_config(module).FLOW
            initial = flow_config(module).INITIAL
            identifier = get_request_params(
                'pk', request, **kwargs)

            activity = initial if identifier == REQUEST_IDENTIFIER \
                else Task.objects.get(id=identifier).activity_ref

            return flow[activity]['role'] not in [
                group.name for group in groups]

        def check_for_update():
            """Check for update/revise operation"""
            return any([
                assignee_check(),
                not self.task.can_revise_activity if hasattr(
                    self, 'task') else False
            ])

        return render(
            request, 'core/denied.html') if {
                'ViewActivity': check_for_view,
                'CreateActivity': check_for_create,
                'UpdateActivity': check_for_update,
        }.get(view)() else None
