"""Command to create view permission for all models"""

from django.apps import apps

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from djangoflow.core.helpers import discover


class Command(BaseCommand):
    """Command to configure permission"""
    help = 'Configures the permissions for models'

    def handle(self, *args, **options):
        """Creates view_<model_name> permission"""
        discovered = discover()
        for app in discovered.keys():
            for model in discovered[app].keys():
                content_type = ContentType.objects.get_for_model(
                     apps.get_model(app, model))
                model_name = model.lower()
                Permission.objects.get_or_create(
                    codename='view_{0}'.format(model_name),
                    name='Can view {0}'.format(model_name),
                    content_type=content_type)

        self.stdout.write(
            self.style.SUCCESS('Successfully configured permissions'))
