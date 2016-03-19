"""Tests for Core app"""
from django.contrib.auth.models import User, Group
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client

from djangoflow.core.models import Request
from djangoflow.tests.models import Foo, Corge


class CoreTests(TestCase):
    """Core workflow engine tests"""
    def setUp(self, **kwargs):
        """Test Setup"""
        self.client = Client()

        self.submitter = Group.objects.create(name='Submitter')
        self.reviewer = Group.objects.create(name='Reviewer')

        self.john_doe = User.objects.create_user(
            'john_doe',
            'john@company.com',
            '12345')

        self.jane_smith = User.objects.create_user(
            'jane_smith',
            'jane@company.com',
            '12345')

        self.client.login(username='john_doe', password='12345')

    def test_available_workflows(self):
        """Tests view that lists workflows"""
        response = self.client.get(reverse('workflows'))
        self.assertEqual(response.status_code, 200)

    def test_workflow_detail_view_with_no_requests(self):
        """Test to get requests for a workflow"""
        response = self.client.get(reverse(
            'workflow-detail',
            kwargs={'app_name': 'tests'}))

        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context['instances'], [])

    def test_workflow_initiation_to_finish(self):
        """Tests the entire workflow cycle"""
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': 'Initial'
        }

        for verb in ('get', 'post'):
            response = getattr(self.client, verb)(reverse(
                'create',
                kwargs=request_args))

            if verb == 'get':
                # Permission Denied
                self.assertTrue('Permission Denied' in response.content)
                # Adds user to the group with permission
                self.submitter.user_set.add(self.john_doe)

            response = getattr(self.client, verb)(reverse(
                'create',
                kwargs=request_args))

            self.assertEqual(response.context['form']._meta.model, Foo)

        # Post the form with validation failure
        response = self.client.post(reverse(
            'create',
            kwargs=request_args),
            {'bar': 'example - small e', 'baz': 'WL', 'qux': 'Nothing'})

        self.assertEqual(response.status_code, 200)
        # No instance gets created because form is invalid
        self.assertEqual(Foo.objects.count(), 0)

        # Post the form again without any validation failure
        response = self.client.post(reverse(
            'create',
            kwargs=request_args),
            {'bar': 'Example - big E', 'baz': 'WL', 'qux': 'Nothing'})

        instances = Foo.objects.all()
        instance = instances.first()

        # Instance gets saved successfully against form submit
        self.assertEqual(instances.count(), 1)

        # Redirects the control to update form
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': instance.id
        }

        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        # Update activity
        for verb in ('get', 'post'):
            response = getattr(self.client, verb)(reverse(
                'update',
                kwargs=request_args))

            self.assertEqual(response.context['form']._meta.model, Foo)

        # Post the form with SAVE action
        response = self.client.post(reverse(
            'update',
            kwargs=request_args),
            {'bar': 'Example', 'baz': 'WL', 'qux': 'Nothing', 'save': 'Save'})

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse(
                'update',
                kwargs=request_args))

        # Post the form with SUBMIT action (to next activity)
        response = self.client.post(reverse(
            'update',
            kwargs=request_args),
            {
                'bar': 'Example',
                'baz': 'WL',
                'qux': 'Nothing',
                'submit': 'corge_activity'
            })

        # Control redirects to workflow detail
        self.assertRedirects(
            response,
            reverse(
                'workflow-detail',
                kwargs={
                    'app_name': 'tests'}))

        # Initiate task for next (last) activity
        final_task = instance.task.request.tasks.latest('id')

        # Posts the form for last (final) activity
        response = self.client.post(reverse(
            'create',
            kwargs={
                'app_name': 'tests',
                'model_name': 'Corge',
                'pk': final_task.id
                }),
            {'grault': 'Example - big E', 'thud': 23})

        instances = Corge.objects.all()
        instance = instances.first()

        # New instance for last activity gets created
        self.assertEqual(instances.count(), 1)

        request_args = {
            'app_name': 'tests',
            'model_name': 'Corge',
            'pk': instance.id
        }

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        # Finish the workflow cycle
        response = self.client.post(reverse(
            'update', kwargs=request_args),
            {'grault': 'Example - big E', 'thud': 23, 'finish': 'Finish'})

    def test_rollback(self):
        """Tests rollback feature"""
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': 'Initial'
        }

        # Post the form again without any validation failure
        response = self.client.post(reverse(
            'create',
            kwargs=request_args),
            {'bar': 'Example - big E', 'baz': 'WL', 'qux': 'Nothing'})

        instances = Foo.objects.all()
        instance = instances.first()

        # Redirects the control to update form
        request_args = {
            'app_name': 'tests',
            'model_name': 'Foo',
            'pk': instance.id
        }

        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        # Post the form with SAVE action
        response = self.client.post(reverse(
            'update',
            kwargs=request_args),
            {'bar': 'Example', 'baz': 'WL', 'qux': 'Nothing', 'save': 'Save'})

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse(
                'update',
                kwargs=request_args))

        # Post the form with SUBMIT action (to next activity)
        response = self.client.post(reverse(
            'update',
            kwargs=request_args),
            {
                'bar': 'Example',
                'baz': 'WL',
                'qux': 'Nothing',
                'submit': 'corge_activity'
            })

        # Control redirects to workflow detail
        self.assertRedirects(
            response,
            reverse(
                'workflow-detail',
                kwargs={
                    'app_name': 'tests'}))

        # Initiate task for next (last) activity
        final_task = instance.task.request.tasks.latest('id')

        # Posts the form for last (final) activity
        response = self.client.post(reverse(
            'create',
            kwargs={
                'app_name': 'tests',
                'model_name': 'Corge',
                'pk': final_task.id
                }),
            {'grault': 'Example - big E', 'thud': 23})

        instances = Corge.objects.all()
        instance = instances.latest('id')

        request_args = {
            'app_name': 'tests',
            'model_name': 'Corge',
            'pk': instance.id
        }

        # Control redirects to update after save
        self.assertRedirects(
            response,
            reverse('update', kwargs=request_args),
            status_code=302,
            target_status_code=200)

        self.client.post(reverse(
            'rollback',
            kwargs={
                'app_name': 'tests',
                'model_name': 'Corge',
                'pk': instance.id
            }))

        request = Request.objects.all().latest('id')
        final_task = request.tasks.latest('id')
        self.assertEqual(final_task.flow_ref_key, 'foo_activity')


    # def test_list_view(self):
    #     """Tests for list view"""
    #     response = self.client.get(reverse(
    #         'index',
    #         kwargs={'app_name': 'tests', 'model_name': 'Foo'}))

    #     self.assertEqual(response.status_code, 200)
    #     self.assertQuerysetEqual(
    #         response.context['objects'],
    #         [repr(self.foo)])

    # def test_delete_view(self):
    #     """Tests for delete view"""
    #     response = self.client.post(reverse(
    #         'delete',
    #         kwargs={
    #             'app_name': 'tests',
    #             'model_name': 'Foo',
    #             'pk': self.foo.id
    #         }))

    #     self.assertRedirects(
    #         response,
    #         reverse(
    #             'index',
    #             kwargs={'app_name': 'tests', 'model_name': 'Foo'}),
    #         status_code=302,
    #         target_status_code=200)

    #     count = Foo.objects.filter(id=self.foo.id).count()

    #     self.assertEqual(count, 0)
