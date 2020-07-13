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
        self._validate_field_values(*args, **kwargs)

        kwargs['choices'] = tuple(self._static_model.members.all().values_list(
            self._value_field_name, self._display_field_name))

        super(StaticModelFieldMixin, self).__init__(*args, **kwargs)

    @property
    def static_model(self):
        return self._static_model

    @property
    def value_field_name(self):
        return self._value_field_name

    @property
    def display_field_name(self):
        return self._display_field_name

    def deconstruct(self):
        name, path, args, kwargs = super(StaticModelFieldMixin, self).deconstruct()

        kwargs.update(dict(
            static_model=self._static_model,
            value_field_name=self._value_field_name,
            display_field_name=self._display_field_name,
        ))

        # del kwargs["choices"]

        return name, path, args, kwargs

    def _validate_field_values(self, *constructor_args, **constructor_kwargs):
        for member in self._static_model.members.all():
            value = getattr(member, self._value_field_name, None)
            self._validate_member_value(member, value, *constructor_args, **constructor_kwargs)

            display_value = getattr(member, self._display_field_name, None)
            if not isinstance(display_value, six.string_types):
                raise ValueError(
                    'Field {!r} of member {!r} must be a string.'.format(
                    self._display_field_name, member._member_name))

    def _validate_member_value(self, member, value, *constructor_args, **constructor_kwargs):
        raise NotImplementedError

    def get_prep_value(self, value):
        if isinstance(value, self._static_model):
            return getattr(value, self._value_field_name)
        else:
            return value

    def from_db_value(self, value, expression, connection, context):
        if value is None:
            return value
        else:
            return self._static_model.members.get(**{self._value_field_name: value})

    def to_python(self, db_value):
        if db_value is None or isinstance(db_value, self._static_model):
            return db_value
        else:
            return self._static_model.members.get(**{self._value_field_name: db_value})

    def contribute_to_class(self, cls, name, **kwargs):
        super(StaticModelFieldMixin, self).contribute_to_class(cls, name, **kwargs)

        def _get_FIELD_display(instance):
            member = getattr(instance, self.attname)
            return getattr(member, self._display_field_name)

        setattr(cls, 'get_{}_display'.format(self.name), _get_FIELD_display)


class StaticModelStringFieldMixin(StaticModelFieldMixin):
    def _validate_member_value(self, member, value, *constructor_args, **constructor_kwargs):
        if not isinstance(value, six.string_types):
            raise ValueError('Field {!r} of member {!r} must be a string.'.format(
                self._value_field_name, member._member_name))


class StaticModelCharField(StaticModelStringFieldMixin, models.CharField):
    def get_internal_type(self):
        return 'CharField'

    def _validate_member_value(self, member, value, *constructor_args, **constructor_kwargs):
        super(StaticModelCharField, self)._validate_member_value(
            member, value, *constructor_args, **constructor_kwargs)
        max_length = constructor_kwargs.get('max_length')
        if max_length is not None and len(value) > max_length:
            raise ValueError('Length of field {!r} of member {!r} must be <= {}'.format(
                self._value_field_name, member._member_name, max_length))


class StaticModelTextField(StaticModelStringFieldMixin, models.TextField):
    def get_internal_type(self):
        return 'TextField'


class StaticModelIntegerField(StaticModelFieldMixin, models.IntegerField):
    def get_internal_type(self):
        return 'IntegerField'

    def _validate_member_value(self, member, value, *constructor_args, **constructor_kwargs):
        if not isinstance(value, six.integer_types):
            raise ValueError('Field {!r} of member {!r} must be an integer.'.format(
                self._value_field_name, member._member_name))


try:
    from south.modelsinspector import add_introspection_rules
except ImportError:
    pass
else:
    SOUTH_RULES = [
      (
        (StaticModelFieldMixin, ),
        [],
        {
            "static_model": ["static_model", {'default': None}],
            "value_field_name": ["value_field_name", {'default': None}],
            "display_field_name": ["display_field_name", {'default': None}],
        },
      )
    ]

    add_introspection_rules(SOUTH_RULES, [
        "^staticmodel\.django\.fields\.StaticModelCharField",
        "^staticmodel\.django\.fields\.StaticModelIntegerField",
    ])
