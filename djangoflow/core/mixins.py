"""Mixins"""

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin)

from django.db.models import Q
from django.shortcuts import render

from djangoflow.core.constants import CRUD_OPERATIONS
from djangoflow.core.helpers import get_model_name, get_app_name, get_model


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


class PermissionDeniedMixin(object):
    """Checks the permission"""
    def check(self, request, **kwargs):
        """N/A"""
        model = get_model(**kwargs)

        if self.request.user.is_superuser:
            return

        groups = list(self.request.user.groups.all())

        if self.__class__.__name__ == "ViewActivity":
            if model.objects.filter(
                Q(task__assignee__in=groups) |
                Q(task__request__requester=self.request.user)
            ).count() != 0:
                    return
        else:
            if model.objects.filter(task__assignee__in=groups).count() != 0:
                return

        return render(request, 'core/denied.html')
