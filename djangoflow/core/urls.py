"""URL configuration for core app"""

from django.conf.urls import url
from django.views.generic import TemplateView

from djangoflow.core.views import (
    workflows,
    WorkflowDetail,
    CreateActivity,
    ViewActivity,
    UpdateActivity,
    DeleteActivity,
)

urlpatterns = [
    url(r'^$', workflows, name='workflows'),
    url(r'^(?P<app_name>\w+)$', WorkflowDetail.as_view(), name='workflow-detail'),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Create/(?P<pk>\d+|Initial)$',
        CreateActivity.as_view(),
        name='create'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Update/(?P<pk>\d+)/$',
        UpdateActivity.as_view(),
        name='update'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/View/$',
        ViewActivity.as_view(),
        name='view'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Delete/(?P<pk>\d+)$',
        DeleteActivity.as_view(),
        name='delete'
    ),
    url(r'^Denied/$', TemplateView.as_view(template_name='core/denied.html'))
]


"""
/
/<workflow>/
/<workflow>/<activity>/Create/<None>
/<workflow>/<activity>/Create/<pk> where pk=request/task id
/<workflow>/<activity>/Update/<pk> where pk=activity instance id
/<workflow>/<activity>/View/<pk> where pk=activity instance id
/<workflow>/<activity>/Delete/<pk> where pk=activity instance id

"""
