"""URL configuration for core app"""

from django.conf.urls import url
from django.views.generic import TemplateView

from djangoflow.core.views import (
    index,
    EntityList,
    EntityDetail,
    EntityUpdate,
    EntityDelete,
    EntityCreate
)

urlpatterns = [
    url(r'^$', index, name='main'),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/List/$',
        EntityList.as_view(),
        name='index'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/(?P<pk>\d+)/$',
        EntityDetail.as_view(),
        name='detail'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Delete/(?P<pk>\d+)$',
        EntityDelete.as_view(),
        name='delete'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Update/(?P<pk>\d+)/$',
        EntityUpdate.as_view(),
        name='update'
    ),
    url(
        r'^(?P<app_name>\w+)/(?P<model_name>\w+)/Create/$',
        EntityCreate.as_view(),
        name='create'
    ),
    url(r'^Denied/$', TemplateView.as_view(template_name='core/denied.html'))
]
