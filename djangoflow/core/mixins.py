"""Mixins"""

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin)

from django.db.models import Q
from django.shortcuts import render

from djangoflow.core.constants import (
    CRUD_OPERATIONS,
    REQUEST_IDENTIFIER
)

from djangoflow.core.helpers import (
    get_model_name,
    get_app_name,
    get_model,
    flow_config,
    get_task_id
)


class BaseEntityMixin(object):
    """Properties and methods that apply to all
    models defined under core
    """
    @property
    def title(self):
        """Returns entity title"""
        return self.__class__.__name__


class AuthMixin(LoginRequiredMixin, PermissionRequiredMixin):
    """Sets permission required check"""
    def get_permission_required(self):
        """Returns permission names used by the mixin"""
        return ['{0}.{1}_{2}'.format(
            get_app_name(request=self.request),
            CRUD_OPERATIONS[self.__class__.__name__.replace(
                'Entity', '').lower()],
            get_model_name(request=self.request).lower())]


class AccessDeniedMixin(object):
    """Checks the permission"""
    def check(self, request, **kwargs):
        """
        - Super user can view/update all activities
        - Requester can view all activities
        - Task assignee can update activity
        - TODO: Historical activities cannot be updated
        """
        model = get_model(**kwargs)
        view = self.__class__.__name__
        groups = list(self.request.user.groups.all())

        if self.request.user.is_superuser:
            return

        def check_for_view():
            return model.objects.filter(
                Q(task__assignee__in=groups) |
                Q(task__request__requester=self.request.user)
            ).count() != 0

        def check_for_create():
            module = get_app_name(request, **kwargs)
            flow = flow_config(module).FLOW
            initial = flow_config(module).INITIAL
            activity = initial if get_task_id(
                request, **kwargs) == REQUEST_IDENTIFIER else self.task.flow_ref_key
            return flow[activity]['role'] in [group.name for group in groups]

        def check_for_update():
            return model.objects.filter(task__assignee__in=groups).count() != 0

        return None if {
            'ViewActivity': check_for_view,
            'CreateActivity': check_for_create,
            'UpdateActivity': check_for_update,
        }.get(view)() else render(request, 'core/denied.html')
