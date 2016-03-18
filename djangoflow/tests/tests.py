"""Tests for Core app"""
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test import Client

from djangoflow.tests.models import Foo


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

    def test_initiate_request(self):
        """Tests request initiation"""
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
                self.assertTrue('Permission Denied' in response.content)
                self.submitter.user_set.add(self.john_doe)

            response = getattr(self.client, verb)(reverse(
                'create',
                kwargs=request_args))

            self.assertEqual(response.context['form']._meta.model, Foo)

        response = self.client.post(reverse(
            'create',
            kwargs=request_args),
            {'bar': 'example - small e', 'baz': 'WL', 'qux': 'Nothing'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Foo.objects.count(), 0)

        response = self.client.post(reverse(
            'create',
            kwargs=request_args),
            {'bar': 'Example - big E', 'baz': 'WL', 'qux': 'Nothing'})

        instances = Foo.objects.all()
        instance = instances.first()
        self.assertEqual(instances.count(), 1)

        self.assertRedirects(
            response,
            reverse(
                'update',
                kwargs={
                    'app_name': 'tests',
                    'model_name': 'Foo',
                    'pk': instance.id
                }),
            status_code=302,
            target_status_code=200)

        # Update activity

        for verb in ('get', 'post'):
            response = getattr(self.client, verb)(reverse(
                'update',
                kwargs={
                    'app_name': 'tests',
                    'model_name': 'Foo',
                    'pk': instance.id
                }))

            self.assertEqual(response.context['form']._meta.model, Foo)

        response = self.client.post(reverse(
            'update',
            kwargs={
                'app_name': 'tests',
                'model_name': 'Foo',
                'pk': instance.id
            }),
            {'bar': 'Example', 'baz': 'WL', 'qux': 'Nothing', 'save': 'Save'})

        self.assertRedirects(
            response,
            reverse(
                'update',
                kwargs={
                    'app_name': 'tests',
                    'model_name': 'Foo',
                    'pk': instance.id
                }))

        response = self.client.post(reverse(
            'update',
            kwargs={
                'app_name': 'tests',
                'model_name': 'Foo',
                'pk': instance.id
            }),
            {
                'bar': 'Example',
                'baz': 'WL',
                'qux': 'Nothing',
                'submit': 'corge_activity'
            })

        self.assertRedirects(
            response,
            reverse(
                'workflow-detail',
                kwargs={
                    'app_name': 'tests'}))

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

    # def test_create_view(self):
    #     """Tests for create view"""
    #     for verb in ('get', 'post'):
    #         response = getattr(self.client, verb)(reverse(
    #             'create',
    #             kwargs={'app_name': 'tests', 'model_name': 'Foo'}))

    #         self.assertEqual(response.context['form']._meta.model, Foo)

    #     response = self.client.post(reverse(
    #         'create',
    #         kwargs={'app_name': 'tests', 'model_name': 'Foo'}),
    #         {'bar': 'example - small e', 'baz': 'WL', 'qux': 'Nothing'})

    #     self.assertEqual(response.status_code, 200)

    #     response = self.client.post(reverse(
    #         'create',
    #         kwargs={'app_name': 'tests', 'model_name': 'Foo'}),
    #         {'bar': 'Example - big E', 'baz': 'WL', 'qux': 'Nothing'})

    #     self.assertRedirects(
    #         response,
    #         reverse(
    #             'index',
    #             kwargs={'app_name': 'tests', 'model_name': 'Foo'}),
    #         status_code=302,
    #         target_status_code=200)

    # def test_udpate_view(self):
    #     """Tests for update view"""
    #     for verb in ('get', 'post'):
    #         response = getattr(self.client, verb)(reverse(
    #             'update',
    #             kwargs={
    #                 'app_name': 'tests',
    #                 'model_name': 'Foo',
    #                 'pk': self.foo.id
    #             }))

    #         self.assertEqual(response.context['form']._meta.model, Foo)

    #     response = self.client.post(reverse(
    #         'update',
    #         kwargs={
    #             'app_name': 'tests',
    #             'model_name': 'Foo',
    #             'pk': self.foo.id
    #         }),
    #         {'bar': 'Example', 'baz': 'WL', 'qux': 'Nothing'})

    #     self.assertRedirects(
    #         response,
    #         reverse(
    #             'index',
    #             kwargs={'app_name': 'tests', 'model_name': 'Foo'}),
    #         status_code=302,
    #         target_status_code=200)
