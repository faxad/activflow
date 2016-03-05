"""Generic views for CRUD operations"""

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.shortcuts import render, render_to_response
from django.template import RequestContext
from django.views import generic
from django.views.generic import TemplateView

from djangoflow.core.constants import WORKFLOW_APPS
from djangoflow.core.helpers import (
    discover,
    get_errors,
    get_model,
    get_model_instance,
    get_form_instance,
    get_app_name,
    get_request_task_id
)

from djangoflow.core.mixins import AuthMixin
from djangoflow.core.models import Request, Task


#@login_required
def workflows(request):
    """Discovers models available for CRUD operations"""
    return render(
        request,
        'index.html',
        {'workflows': WORKFLOW_APPS})


class WorkflowDetail(TemplateView):
    """Generic view to list worflow requests & tasks"""
    template_name = 'core/workflow.html'

    def get_context_data(self, **kwargs):
        context = super(WorkflowDetail, self).get_context_data(**kwargs)
        app_title = get_app_name(**kwargs)
        content_type = ContentType.objects.get_for_model(
            apps.get_model(app_title, 'FirstActivity'))
        context['instances'] = content_type.get_all_objects_for_this_type()
        return context


# class EntityList(generic.ListView):
#     """Generic view for List/Display operation"""
#     template_name = 'core/index.html'
#     context_object_name = 'objects'

#     def dispatch(self, request, *args, **kwargs):
#         """Overriding dispatch on ListView"""
#         self.model = get_model(**kwargs)

#         return super(EntityList, self).dispatch(
#             request, *args, **kwargs)


class ViewActivity(generic.DetailView):
    """Displays activity details"""
    template_name = 'core/detail.html'

    def dispatch(self, request, *args, **kwargs):
        """Overriding dispatch on DetailView"""
        self.model = get_model(**kwargs)

        return super(ViewActivity, self).dispatch(
            request, *args, **kwargs)


class DeleteActivity(generic.DeleteView):
    """Deletes activity instance"""
    def dispatch(self, request, *args, **kwargs):
        """Overriding dispatch on DeleteView"""
        self.model = get_model(**kwargs)
        instance = get_model_instance(**kwargs)
        app_title = get_app_name(**kwargs)
        self.success_url = reverse_lazy(
            'index', args=(app_title, instance.title,))

        return super(DeleteActivity, self).dispatch(
            request, *args, **kwargs)


class CreateActivity(generic.View):
    """Creates activity instance"""
    def get(self, request, **kwargs):
        """GET request handler for Create operation"""
        form = get_form_instance(**kwargs)
        context = {'form': form}

        return render(request, 'core/create.html', context)

    def post(self, request, **kwargs):
        """POST request handler for Create operation"""
        model = get_model(**kwargs)
        form = get_form_instance(**kwargs)(request.POST)
        app_title = get_app_name(**kwargs)
        identifier = get_request_task_id(**kwargs)

        if form.is_valid():
            instance = model(**form.cleaned_data)

            if instance.is_initial_activity:
                instance.initiate_request()

            # return HttpResponseRedirect(
            #     reverse('index', args=(
            #         app_title, instance.title,)))
            context = {
                'form': form,
                'next': instance.next()
            }
        else:
            context = {
                'form': form,
                'error_message': get_errors(form.errors)
            }

        return render_to_response(
            'core/create.html',
            context,
            context_instance=RequestContext(request))


class UpdateActivity(generic.View):
    """Updates an existing activity instance"""
    def get(self, request, **kwargs):
        """GET request handler for Update operation"""
        instance = get_model_instance(**kwargs)
        form = get_form_instance(**kwargs)
        context = {
            'form': form(instance=instance),
            'object': instance,
        }

        return render(request, 'core/update.html', context)

    def post(self, request, **kwargs):
        """POST request handler for Update operation"""
        instance = get_model_instance(**kwargs)
        app_title = get_app_name(**kwargs)
        form = get_form_instance(
            **kwargs)(request.POST, instance=instance)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(
                reverse('index', args=(
                    app_title, instance.title,)))
        else:
            context = {
                'form': form,
                'object': instance,
                'error_message': get_errors(form.errors)
            }

            return render_to_response(
                'core/update.html',
                context,
                context_instance=RequestContext(request))
