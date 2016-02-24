"""Mixins"""

from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin)

from djangoflow.core.constants import CRUD_OPERATIONS
from djangoflow.core.helpers import get_model_name, get_app_name


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
