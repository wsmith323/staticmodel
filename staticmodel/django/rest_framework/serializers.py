"""Django REST Framework serializer fields backed by StaticModel members."""

from collections.abc import Mapping
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from staticmodel import StaticModel


class StaticModelFieldMixin:

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

        self._expand = kwargs.pop('static_model_expand', False)

        super().__init__(*args, **kwargs)

    def to_representation(self, value):
        if value is None:
            return value
        elif isinstance(value, self._static_model):
            if self._expand:
                return dict(value._as_dict)
            else:
                return getattr(value, self._lookup_field_name)
        else:
            raise ValueError("Invalid value for 'value' parameter")

    def to_internal_value(self, data):
        if data is None:
            return data
        else:
            if isinstance(data, Mapping):
                try:
                    lookup_value = data[self._lookup_field_name]
                except KeyError:
                    raise ValidationError("Representation missing field '{}'".format(
                        self._lookup_field_name))
            else:
                lookup_value = data
            try:
                return self._static_model.members.get(**{self._lookup_field_name: lookup_value})
            except self._static_model.DoesNotExist as e:
                raise ValidationError("Value {!r} is invalid".format(data))


class StaticModelCharField(StaticModelFieldMixin, serializers.CharField):
    pass


class StaticModelIntegerField(StaticModelFieldMixin, serializers.IntegerField):
    pass
