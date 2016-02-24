"""Haystack search index configuration.
This must be kept in sync with the models"""

from haystack import indexes
from djangoflow.tests.models import Foo


class SupplierIndex(indexes.SearchIndex, indexes.Indexable):
    """Indexing configuration for Foo"""
    text = indexes.CharField(document=True, use_template=True)
    bar = indexes.CharField(model_attr='bar')
    qux = indexes.CharField(model_attr='qux')

    def get_model(self):
        """Model instance"""
        return Foo

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.all()
