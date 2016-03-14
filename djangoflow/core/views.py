"""Generic views for CRUD operations"""

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import generic
from django.views.generic import TemplateView

from djangoflow.core.constants import WORKFLOW_APPS, REQUEST_IDENTIFIER
from djangoflow.core.helpers import (
    get_errors,
    get_model,
    get_model_instance,
    get_form_instance,
    get_app_name,
    get_task_id,
    flow_config
)

from djangoflow.core.mixins import AuthMixin, AccessDeniedMixin


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
        config = flow_config(app_title)
        model = config.FLOW[config.INITIAL]['model']().title
        content_type = ContentType.objects.get_for_model(
            apps.get_model(app_title, model))
        context['instances'] = content_type.get_all_objects_for_this_type()
        context['request_identifier'] = REQUEST_IDENTIFIER

        return context


class ViewActivity(generic.DetailView, AccessDeniedMixin):
    """Displays activity details"""
    template_name = 'core/detail.html'

    def dispatch(self, request, *args, **kwargs):
        """Overriding dispatch on DetailView"""
        self.model = get_model(**kwargs)
        denied = self.check(request, **kwargs)
        return denied if denied else super(ViewActivity, self).dispatch(
            request, *args, **kwargs)


class DeleteActivity(generic.DeleteView):
    """Deletes activity instance"""
    def dispatch(self, request, *args, **kwargs):
        """Overriding dispatch on DeleteView"""
        self.model = get_model(**kwargs)
        instance = get_model_instance(request, **kwargs)
        app_title = get_app_name(**kwargs)
        self.success_url = reverse_lazy(
            'index', args=(app_title, instance.title,))

        return super(DeleteActivity, self).dispatch(
            request, *args, **kwargs)


class CreateActivity(generic.View, AccessDeniedMixin):
    """Creates activity instance"""
    def get(self, request, **kwargs):
        """GET request handler for Create operation"""
        form = get_form_instance(**kwargs)
        context = {'form': form}

        denied = self.check(request, **kwargs)
        return denied if denied else render(
            request, 'core/create.html', context)

    @transaction.atomic
    def post(self, request, **kwargs):
        """POST request handler for Create operation"""
        model = get_model(**kwargs)
        form = get_form_instance(**kwargs)(request.POST)
        app_title = get_app_name(**kwargs)

        if form.is_valid():
            instance = model(**form.cleaned_data)

            if instance.is_initial:
                instance.initiate_request(request.user)
            else:
                instance.assign_task(
                    get_task_id(**kwargs))
                instance.task.initiate()

            return HttpResponseRedirect(
                reverse('update', args=(
                    app_title, instance.title, instance.id)))
        else:
            context = {
                'form': form,
                'error_message': get_errors(form.errors)
            }

            return render(request, 'core/create.html', context)


class UpdateActivity(generic.View, AccessDeniedMixin):
    """Updates an existing activity instance"""
    def get(self, request, **kwargs):
        """GET request handler for Update operation"""
        instance = get_model_instance(request, **kwargs)
        form = get_form_instance(**kwargs)
        context = {
            'form': form(instance=instance),
            'object': instance,
            'next': instance.next()
        }

        denied = self.check(request, **kwargs)
        return denied if denied else render(
            request, 'core/update.html', context)

    @transaction.atomic
    def post(self, request, **kwargs):
        """POST request handler for Update operation"""
        instance = get_model_instance(request, **kwargs)
        app_title = get_app_name(**kwargs)
        form = get_form_instance(
            **kwargs)(request.POST, instance=instance)

        if form.is_valid():
            form.save()

            if 'save' in request.POST:
                return HttpResponseRedirect(
                    reverse('update', args=(
                        app_title, instance.title, instance.id)))
            else:
                self.task.submit(
                    app_title, self.request.user, request.POST['submit'])

                return HttpResponseRedirect(
                    reverse('workflow-detail', args=[app_title]))
        else:
            context = {
                'form': form,
                'object': instance,
                'next': instance.next(),
                'error_message': get_errors(form.errors)
            }

            return render(request, 'core/update.html', context)
