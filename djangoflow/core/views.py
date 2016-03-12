"""Generic views for CRUD operations"""

from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseRedirect
from django.shortcuts import render
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
    get_task_id
)

from djangoflow.core.mixins import AuthMixin
from djangoflow.core.models import Task


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


class ViewActivity(generic.DetailView):
    """Displays activity details"""
    template_name = 'core/detail.html'

    def get_queryset(self):
        """Custom queryset"""
        if not self.request.user.is_superuser:
            query = (Q(task__assignee__in=list(
                        self.request.user.groups.all())) |
                     Q(task__request__requester=self.request.user))

            return self.model.objects.filter(query)
        else:
            return super(ViewActivity, self).get_queryset()

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
        instance = get_model_instance(request, **kwargs)
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

    @transaction.atomic
    def post(self, request, **kwargs):
        """POST request handler for Create operation"""
        model = get_model(**kwargs)
        form = get_form_instance(**kwargs)(request.POST)
        app_title = get_app_name(**kwargs)

        if form.is_valid():
            instance = model(**form.cleaned_data)

            if instance.is_initial_activity:
                instance.initiate_request()
            else:
                task_id = get_task_id(**kwargs)
                task = Task.objects.get(id=task_id)
                task.initiate()
                instance.task = task
                instance.save()

            return HttpResponseRedirect(
                reverse('update', args=(
                    app_title, instance.title, instance.id)))
        else:
            context = {
                'form': form,
                'error_message': get_errors(form.errors)
            }

            return render(request, 'core/create.html', context)


class UpdateActivity(generic.View):
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

        return render(request, 'core/update.html', context)

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
                next = request.POST['submit']
                task_id = instance.task.id
                task = Task.objects.get(id=task_id)
                task.submit(app_title, next)

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
