"""
*******************
Django model fields
*******************

**Static Model** provides custom Django model fields in the
``staticmodel.django.models`` package:

 * ``StaticModelCharField`` (sub-class of ``django.db.models.CharField``)
 * ``StaticModelTextField`` (sub-class of ``django.db.models.TextField``)
 * ``StaticModelIntegerField`` (sub-class of ``django.db.models.IntegerField``)

Static model members are returned, and can be set, as the value of the
fields on a django model object.

All fields take the following keyword arguments in addition to the
arguments taken by their respective parent classes:

 * ``static_model``: The static model class associated with this field.
 * ``value_field_name``: The static model field name whose value will
   be stored in the database. Defaults to the first field name in
   ``static_model._field_names``.
 * ``display_field_name``: The static model field name whose value will
   be used as the display value in the ``choices`` passed to the parent
   field. Defaults to the value of ``value_field_name``.

When the model field is instantiated, it validates the values of
``value_field_name`` and ``display_field_name`` against
**every member** of the static model to insure the fields exist and
contain a value appropriate for the value of the field. This ensures
that error-causing inconsistencies are detected early during
development.
"""
from django.core.exceptions import ValidationError
from django.db import models
from staticmodel import StaticModel


class StaticModelFieldMixin(object):
    def __init__(self, *args, **kwargs):
        self._static_model = kwargs.pop('static_model', None)
        if not self._static_model:
            raise ValueError('static_model required')
        if not issubclass(self._static_model, StaticModel):
            raise ValueError('static_model must be subclass of StaticModel')

        self._value_field_name = kwargs.pop('value_field_name', self._static_model._field_names[0])
        self._display_field_name = kwargs.pop('display_field_name', self._value_field_name)
        self._validate_field_values(*args, **kwargs)

        kwargs['choices'] = tuple(self._static_model.members.choices(
            self._value_field_name, self._display_field_name))

        super().__init__(*args, **kwargs)

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
        name, path, args, kwargs = super().deconstruct()

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
            if not isinstance(display_value, str):
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

    def clean(self, value, model_instance):
        if isinstance(value, self._static_model):
            db_value = getattr(value, self._value_field_name)
            sm_value = value
        else:
            db_value = value
            try:
                sm_value = self.to_python(value)
            except self._static_model.DoesNotExist:
                raise ValidationError("{} member not found for {}={!r}".format(
                    self._static_model.__name__, self._value_field_name, value))

        self.validate(db_value, model_instance)
        self.run_validators(db_value)
        return sm_value

    def contribute_to_class(self, cls, name, **kwargs):
        super().contribute_to_class(cls, name, **kwargs)

        def _get_FIELD_display(instance):
            member = getattr(instance, self.attname)
            return getattr(member, self._display_field_name)

        setattr(cls, 'get_{}_display'.format(self.name), _get_FIELD_display)


class StaticModelStringFieldMixin(StaticModelFieldMixin):
    def _validate_member_value(self, member, value, *constructor_args, **constructor_kwargs):
        if not isinstance(value, str):
            raise ValueError('Field {!r} of member {!r} must be a string.'.format(
                self._value_field_name, member._member_name))


class StaticModelCharField(StaticModelStringFieldMixin, models.CharField):
    def get_internal_type(self):
        return 'CharField'

    def _validate_member_value(self, member, value, *constructor_args, **constructor_kwargs):
        super()._validate_member_value(
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
        if not isinstance(value, int):
            raise ValueError('Field {!r} of member {!r} must be an integer.'.format(
                self._value_field_name, member._member_name))
