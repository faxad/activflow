"""URL configuration for core app"""

from django.conf.urls import url
from django.views.generic import TemplateView

from djangoflow.core.views import (
    index,
    Workflow,
    CreateActivity,
    ViewActivity,
    UpdateActivity,
    DeleteActivity,
)

urlpatterns = [
    url(r'^$', index, name='main'),
    url(r'^(?P<app_name>\w+)$', Workflow.as_view(), name='workflow'),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/CreateActivity/(?P<pk>\d+)$',
        CreateActivity.as_view(),
        name='create'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/List/$',
        ViewActivity.as_view(),
        name='index'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Delete/(?P<pk>\d+)$',
        DeleteActivity.as_view(),
        name='delete'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Update/(?P<pk>\d+)/$',
        UpdateActivity.as_view(),
        name='update'
    ),
    url(r'^Denied/$', TemplateView.as_view(template_name='core/denied.html'))
]
