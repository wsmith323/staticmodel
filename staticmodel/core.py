from __future__ import unicode_literals

from collections import Iterable, OrderedDict
from itertools import chain

import six

from .compat.preparable import Prepareable
from .compat.partialmethod import partialmethod
from .compat.simplenamespace import SimpleNamespace
from .util import format_kwargs


class ATTR_NAME:
    class CLASS_VAR:
        ATTR_NAMES = '_field_names'
    class INSTANCE_VAR:
        MEMBER_NAME = '_member_name'
        RAW_VALUE = '_raw_value'


class StaticModelMeta(six.with_metaclass(Prepareable, type)):
    @classmethod
    def __prepare__(mcs, name, bases, **kwargs):
        return OrderedDict()

    def __new__(mcs, name, bases, attrs, **kwargs):

        # Extract members into _raw_members dict before class is
        # created.
        raw_members = OrderedDict()
        for attr_name in tuple(attrs.keys()):
            if attr_name.startswith('_'):
                continue
            if attr_name != attr_name.upper():
                continue

            raw_members[attr_name] = attrs[attr_name]
            del attrs[attr_name]

        attrs['_{}__raw_members'.format(name)] = raw_members

        return super(StaticModelMeta, mcs).__new__(mcs, name, bases, attrs)

    def __init__(cls, *args, **kwargs):
        super(StaticModelMeta, cls).__init__(*args, **kwargs)

        cls._submodels = OrderedDict()
        cls._instances = SimpleNamespace(
            by_id=OrderedDict(), by_member_name=OrderedDict())
        cls._indexes = {}

        # Now that the class has been created and initialized
        # sufficiently, go ahead and add the members, if any.
        raw_members_attr_name = '_{}__raw_members'.format(cls.__name__)
        raw_members = getattr(cls, raw_members_attr_name, None)
        if raw_members is not None:
            for name, value in raw_members.items():
                # __setattr__ is the entry point for member instance
                # creation.
                setattr(cls, name, value)

            delattr(cls, raw_members_attr_name)

        cls.members = StaticModelMemberManager(cls)

        cls._populate_ancestors(cls)

    #
    # Public API
    #
    class StaticModelError(Exception):
        pass

    class DoesNotExist(StaticModelError):
        pass

    class MultipleObjectsReturned(StaticModelError):
        pass

    def __repr__(cls):
        return '<StaticModel {}: Instances: {}, Fields: {}>'.format(
            cls.__name__, len(cls._instances.by_id), cls._field_names)

    def __getattribute__(cls, item):
        item = str(item)
        if item.upper() == item:
            try:
                return cls.__dict__[item]
            except KeyError:
                raise AttributeError('{!r} model does not contain member {!r}'.format(
                    cls.__name__, item))
        else:
            return super(StaticModelMeta, cls).__getattribute__(item)

    def __setattr__(cls, key, value):
        if key.startswith('_') or key != key.upper():
            super(StaticModelMeta, cls).__setattr__(key, value)
        else:
            try:
                existing_value = getattr(cls, key)
            except AttributeError:
                pass
            else:
                raise TypeError('{}.{} already exists with value {!r}'.format(
                    cls.__name__, key, existing_value))

            if isinstance(value.__class__, cls.__class__):
                instance = value
                cls._process_new_instance(key, instance)
            else:
                instance = cls(raw_value=value, member_name=key)

            super(StaticModelMeta, cls).__setattr__(key, instance)

    def __call__(
            cls, raw_value=None, member_name=None, field_names=None, *field_values,
            **kwargs):
        if field_values and raw_value:
            raise ValueError("Positional and 'raw_value' parameters are mutually"
                             " exclusive")

        if member_name is not None and member_name.upper() != member_name:
            raise ValueError(
                "Value for 'member_name' parameter must be all uppercase.")

        if raw_value and isinstance(raw_value, Iterable) and not isinstance(
                raw_value, str):
            field_values = raw_value

        instance = super(StaticModelMeta, cls).__call__()

        field_names = field_names or cls._field_names or tuple(
            'value{}'.format(i) for i in range(len(field_values)))
        instance.__dict__.update(dict(zip(field_names, field_values)))

        setattr(instance, ATTR_NAME.INSTANCE_VAR.RAW_VALUE, raw_value)

        cls._process_new_instance(member_name, instance)

        return instance

    def submodels(cls):
        return (submodel for submodel in cls._submodels.keys())

    def register_submodel(cls, submodel):
        cls._submodels[submodel] = None

    def remove_submodel(cls, submodel):
        del cls._submodels[submodel]

    #
    # Private API
    #
    def _populate_ancestors(cls, child):
        # This method recursively adds sub_class members to all
        # ancestor classes that are instances of this metaclass,
        # enabling parent classes to have members that are instances
        # of child classes not yet defined when the parent class
        # definition is executed.
        mcs = cls.__class__
        for parent in child.__bases__:
            if isinstance(parent, mcs):
                if parent is StaticModel:
                    continue
                for member in cls._instances.by_id.values():
                    member_name = getattr(
                        member, ATTR_NAME.INSTANCE_VAR.MEMBER_NAME, None)
                    if member_name is not None:
                        setattr(parent, member_name, member)
                parent.register_submodel(cls)
                cls._populate_ancestors(parent)

    def _process_new_instance(cls, member_name, instance):
        instance_cn = getattr(instance, ATTR_NAME.INSTANCE_VAR.MEMBER_NAME, None)
        if instance_cn and member_name and instance_cn != member_name:
            raise ValueError(
                'Constant value {!r} already has a member name'.format(
                    instance))

        setattr(instance, ATTR_NAME.INSTANCE_VAR.MEMBER_NAME, member_name)

        cls._instances.by_id[id(instance)] = instance
        if member_name is not None:
            cls._instances.by_member_name[member_name] = instance
        cls._index_instance(instance)

    def _index_instance(cls, instance):
        for index_attr in (ATTR_NAME.INSTANCE_VAR.RAW_VALUE, ) + cls._field_names:
            index = cls._indexes.setdefault(index_attr, OrderedDict())
            try:
                value = getattr(instance, index_attr)
            except AttributeError:
                continue
            else:
                if callable(value):
                    value = value()
                if isinstance(value, cls) or isinstance(value.__class__, cls.__class__):
                    key = id(value)
                else:
                    key = cls._index_key_for_value(value)
                index.setdefault(key, []).append(instance)

    def _index_key_for_value(cls, obj):
        return str(obj)

    def _get_index_search_results(cls, kwargs):
        # Make sure ATTR_NAME.INSTANCE_VAR.MEMBER_NAME gets processed
        # first if it is present. There is no point in hitting the
        # other indexes if we miss there.
        sorted_kwargs = sorted(
            kwargs.items(), key=lambda x: x[0] != ATTR_NAME.INSTANCE_VAR.MEMBER_NAME)

        for field_name, field_value in sorted_kwargs:
            if field_name == ATTR_NAME.INSTANCE_VAR.MEMBER_NAME:
                index = cls._instances.by_member_name
                try:
                    result = index[field_value]
                except KeyError:
                    raise StopIteration
                else:
                    yield result

            else:
                try:
                    index = cls._indexes[field_name]
                except KeyError:
                    raise ValueError(
                        'Invalid field {!r}'.format(field_name))
                else:
                    result = index.get(cls._index_key_for_value(field_value), [])
                    for item in result:
                        yield item


class StaticModelMemberManager(object):
    """
    Manager API for StaticModel instances.

    The .members attribute on each model class is an instance of this
    class.
    """

    def __init__(self, model):
        self.model = model

    #
    # Private API
    #
    def _values_base(self, item_func, *field_names, **kwargs):
        criteria = kwargs.pop('criteria', {})
        allow_flat = kwargs.pop('allow_flat', False)
        flat = kwargs.pop('flat', False)

        if not field_names:
            field_names = self.model._field_names

        elif not frozenset(field_names).issubset(frozenset(chain(
                (ATTR_NAME.INSTANCE_VAR.MEMBER_NAME,
                 ATTR_NAME.INSTANCE_VAR.MEMBER_NAME),
                chain(self.model.__dict__.keys(), self.model._field_names),
                chain.from_iterable(chain(
                    submodel.__dict__.keys(), submodel._field_names)
                        for submodel in self.model.submodels())
                ))):
            raise ValueError(
                "Field names must be a subset of those available.")

        if not criteria:
            results = self.all()
        else:
            results = self.filter(**criteria)

        if allow_flat and flat:
            for rendered_item in chain.from_iterable(
                    item_func(item, field_names) for item in results):
                if rendered_item:
                    yield rendered_item
        else:
            for item in results:
                rendered_item = item_func(item, field_names)
                if rendered_item:
                    yield rendered_item

    def _build_filter_error(self, kwargs):
        return self.model.DoesNotExist(
            '{}.filter({}) yielded no objects.'.format(
                self.model.__name__, format_kwargs(kwargs)))

    #
    # Public API
    #
    def all(self):
        return (instance for instance in self.model._instances.by_id.values())

    def filter(self, **kwargs):
        index_search_results = self.model._get_index_search_results(kwargs)

        validated_result_ids = set()
        for result in index_search_results:
            for field_name, field_value in kwargs.items():
                if (field_name == ATTR_NAME.INSTANCE_VAR.MEMBER_NAME and
                        self.model._instances.by_member_name.get(
                            field_value) is result):
                    continue

                try:
                    value = getattr(result, field_name)
                except AttributeError:
                    break

                if value != field_value:
                    break

            else:
                result_id = id(result)
                if result_id not in validated_result_ids:
                    validated_result_ids.add(result_id)
                    yield result

        if not validated_result_ids:
            raise self._build_filter_error(kwargs)

    def get(self, _return_none=False, **kwargs):
        try:
            results = self.filter(**kwargs)
            result = next(results)
        except self.model.DoesNotExist:
            if _return_none:
                return None
            else:
                raise self.model.DoesNotExist(
                    '{}.get({}) yielded no objects.'.format(
                        self.model.__name__, format_kwargs(kwargs)))

        try:
            next(results)
        except StopIteration:
            return result
        else:
            raise self.model.MultipleObjectsReturned(
                '{}.get({}) yielded multiple objects.'.format(
                    self.model.__name__, format_kwargs(kwargs)))

    def _values_item(item, field_names):
        rendered_item = []
        for field_name in field_names:
            field_value = getattr(item, field_name, None)
            if field_value is not None:
                rendered_item.append((field_name, field_value))
        return OrderedDict(rendered_item)
    values = partialmethod(_values_base, _values_item)

    def _values_list_item(item, field_names):
        rendered_item = []
        for field_name in field_names:
            field_value = getattr(item, field_name, None)
            if field_value is not None:
                rendered_item.append(field_value)
        return tuple(rendered_item)
    values_list = partialmethod(_values_base, _values_list_item, allow_flat=True)


class StaticModel(six.with_metaclass(StaticModelMeta), object):
    """
    Base class for static models.
    """
    def __repr__(self):
        return '<{}.{}: {}>'.format(
            self.__class__.__name__,
            getattr(self, ATTR_NAME.INSTANCE_VAR.MEMBER_NAME),
            format_kwargs(OrderedDict(
                (field_name, getattr(self, field_name, None))
                for field_name in self._field_names)),
        )
