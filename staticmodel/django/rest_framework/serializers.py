"""
*********************************
Django Rest Framework integration
*********************************

**Static Model** provides custom DRF serializer fields in the
``staticmodel.django.rest_framework.serializers`` module:

 * ``StaticModelCharField`` (sub-class of ``rest_framework.serializers.CharField``)
 * ``StaticModelIntegerField`` (sub-class of ``rest_framework.serializers.IntegerField``)

Currently, only a single field value is extracted from the static model
instance when serializing. Support for serializing the entire instance
as a nested dict will be added in the future.

When deserializing, the single field value is looked up in the static model
and the corresponding member is returned.

All fields take the following keyword arguments in addition to the
arguments taken by their respective parent classes:

 * ``static_model``: The static model class associated with this field.
 * ``lookup_field_name``: The static model field name that will be
   returned during serialization and that will be used to lookup the
   static model member when deserializing. Defaults to the first field
   name in ``static_model._field_names``.
"""
from rest_framework import serializers
from staticmodel import StaticModel


class StaticModelFieldMixin(object):

    def __init__(self, *args, **kwargs):
        static_model = kwargs.pop('static_model', None)
        if not static_model:
            raise TypeError("Parameter 'static_model' is required")
        if not issubclass(static_model, StaticModel):
            raise TypeError("Parameter 'static_model' must be a StaticModel class")
        self._static_model = static_model

        lookup_field_name = kwargs.pop('lookup_field_name', None)
        if lookup_field_name and lookup_field_name not in self._static_model._field_names:
            raise ValueError("Parameter 'lookup_field' must be one of: {}".format(
                ', '.join(self._static_model._field_names)))
        if not lookup_field_name:
            lookup_field_name = self._static_model._field_names[0]
        self._lookup_field_name = lookup_field_name

        super().__init__(*args, **kwargs)

    def to_native(self, value):
        return getattr(value, self._lookup_field_name)

    def from_native(self, value):
        return self._static_model.members.get(**{self._lookup_field_name: value})


class StaticModelCharField(StaticModelFieldMixin, serializers.CharField):
    pass


class StaticModelIntegerField(StaticModelFieldMixin, serializers.IntegerField):
    pass
