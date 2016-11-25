from __future__ import unicode_literals

from django.db import models
import six


class StaticModelFieldMixin(object):
    def __init__(self, *args, **kwargs):
        self._static_model = kwargs.pop('static_model', None)
        assert self._static_model, 'static_model required'

        self._value_field_name = kwargs.pop('value_field_name',
                                       self._static_model._field_names[0])
        self._display_field_name = kwargs.pop('display_field_name',
                                              self._value_field_name)
        self._validate_field_values()

        kwargs['choices'] = tuple(self._static_model.members.values_list(
            self._value_field_name, self._display_field_name))

        super(StaticModelFieldMixin, self).__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super(StaticModelFieldMixin, self).deconstruct()

        kwargs.update(dict(
            static_model=self._static_model,
            value_field_name=self._value_field_name,
            display_field_name=self._display_field_name,
        ))

        del kwargs["choices"]

        return name, path, args, kwargs

    def _validate_field_values(self):
        for member in self._static_model.members.all():
            value = getattr(member, self._value_field_name)
            self._validate_member_value(member, value)

            display_value = getattr(member, self._display_field_name)
            if not isinstance(display_value, six.string_types):
                raise ValueError(
                    'Field {!r} of member {!r} must be a string.'.format(
                    self._display_field_name, member._member_name))

    def _validate_member_value(self, member, value):
        raise NotImplementedError

    def get_prep_value(self, member):
        return super(StaticModelFieldMixin, self).get_prep_value(
            getattr(member, self._value_field_name))

    def to_python(self, db_value):
        return super(StaticModelFieldMixin, self).to_python(
            self._static_model.members.get(**{self._value_field_name: db_value}))


class StaticModelCharField(StaticModelFieldMixin, models.CharField):

    def _validate_member_value(self, member, value):
        if not isinstance(value, six.string_types):
            raise ValueError('Field {!r} of member {!r} must be a string.'.format(
                self._value_field_name, member._member_name))


class StaticModelIntegerField(StaticModelFieldMixin, models.IntegerField):

    def _validate_member_value(self, member, value):
        if not isinstance(value, six.integer_types):
            raise ValueError('Field {!r} of member {!r} must be an integer.'.format(
                self._value_field_name, member._member_name))
