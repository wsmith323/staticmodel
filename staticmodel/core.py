from collections import Iterable, OrderedDict
from functools import partialmethod
from itertools import chain
from types import SimpleNamespace

from .util import format_kwargs


class AttrName:
    class CLASS:
        FIELD_NAMES = '_field_names'

    class INSTANCE:
        MEMBER_NAME = '_member_name'
        RAW_VALUE = '_raw_value'


class StaticModelMeta(type):
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

        return super().__new__(mcs, name, bases, attrs)

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cls._submodels = OrderedDict()
        cls._members = SimpleNamespace(
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
    def __repr__(cls):
        return '<StaticModel {}: Members: {}, Fields: {}>'.format(
            cls.__name__, len(cls._members.by_id), cls._field_names)

    def __getattribute__(cls, item):
        item = str(item)
        if item.upper() == item:
            try:
                return cls.__dict__[item]
            except KeyError:
                raise AttributeError('{!r} model does not contain member {!r}'.format(
                    cls.__name__, item))
        else:
            return super().__getattribute__(item)

    def __setattr__(cls, key, value):
        if key.startswith('_') or key != key.upper():
            super().__setattr__(key, value)
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

            super().__setattr__(key, instance)

    def __call__(
            cls, raw_value=None, member_name=None, field_names=None, *field_values,
            **kwargs):
        if field_values and raw_value:
            raise ValueError("Positional and 'raw_value' parameters are mutually"
                             " exclusive")

        if member_name is not None and member_name.upper() != member_name:
            raise ValueError(
                "Value for 'member_name' parameter must be all uppercase.")

        if raw_value and isinstance(raw_value, Iterable) and not isinstance(raw_value, str):
            field_values = raw_value

        field_names = field_names or getattr(cls, '_field_names', None)
        if not field_names:
            raise ValueError("At lease one field must be defined")

        instance = super().__call__(**dict(zip(field_names, field_values)))

        setattr(instance, AttrName.INSTANCE.RAW_VALUE, raw_value)

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
                for member in cls._members.by_id.values():
                    member_name = getattr(
                        member, AttrName.INSTANCE.MEMBER_NAME, None)
                    if member_name is not None:
                        setattr(parent, member_name, member)
                parent.register_submodel(cls)
                cls._populate_ancestors(parent)

    def _process_new_instance(cls, member_name, instance):
        instance_member_name = getattr(instance, AttrName.INSTANCE.MEMBER_NAME, None)
        if instance_member_name and member_name and instance_member_name != member_name:
            raise ValueError('Member {!r} already has a member name'.format(instance))

        setattr(instance, AttrName.INSTANCE.MEMBER_NAME, member_name)

        cls._members.by_id[id(instance)] = instance
        if member_name is not None:
            cls._members.by_member_name[member_name] = instance
        cls._index_instance(instance)

    def _index_instance(cls, instance):
        for index_attr in (AttrName.INSTANCE.RAW_VALUE,) + cls._field_names:
            index = cls._indexes.setdefault(index_attr, OrderedDict())
            try:
                value = getattr(instance, index_attr)
            except AttributeError:
                continue
            else:
                key = cls._index_key_for_value(value)
                index.setdefault(key, []).append(instance)

    def _index_key_for_value(cls, value):
        try:
            return hash(value)
        except TypeError:
            return hash(repr(value))

    def _get_index_search_results(cls, criteria):
        # Make sure ATTR_NAME.INSTANCE_VAR.MEMBER_NAME gets processed
        # first if it is present. There is no point in hitting the
        # other indexes if we miss there.
        sorted_kwargs = sorted(
            criteria.items(),
            key=lambda x: x[0] != AttrName.INSTANCE.MEMBER_NAME)

        for field_name, field_value in sorted_kwargs:
            if field_name == AttrName.INSTANCE.MEMBER_NAME:
                index = cls._members.by_member_name
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
                    if field_name in cls._field_names:
                        continue
                    else:
                        raise cls.InvalidField(
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
    # Public API
    #
    def all(self):
        return StaticModelMembers(
            self.model._members.by_id.values(), model=self.model)

    def filter(self, **criteria):
        if not criteria:
            return self.all()

        index_search_results = self.model._get_index_search_results(criteria)

        results = []

        validated_member_ids = set()
        for member in index_search_results:
            for field_name, field_value in criteria.items():
                if (field_name == AttrName.INSTANCE.MEMBER_NAME and
                        self.model._members.by_member_name.get(
                            field_value) is member):
                    continue

                try:
                    value = getattr(member, field_name)
                except AttributeError:
                    break

                if value != field_value:
                    break

            else:
                member_id = id(member)
                if member_id not in validated_member_ids:
                    validated_member_ids.add(member_id)
                    results.append(member)

        return StaticModelMembers(results, model=self.model)

    def get(self, _return_none=False, **kwargs):
        results = self.filter(**kwargs)
        if not results:
            if _return_none:
                return None
            else:
                raise self.model.DoesNotExist(
                    '{}.members.get({}) yielded no objects.'.format(
                        self.model.__name__, format_kwargs(kwargs)))

        elif len(results) == 1:
            return results[0]
        else:
            raise self.model.MultipleObjectsReturned(
                '{}.members.get({}) yielded multiple objects.'.format(
                    self.model.__name__, format_kwargs(kwargs)))

    def choices(self, *fields, **criteria):
        if len(fields) > 2:
            raise ValueError(
                'Maximum number of specified fields for {0}.members.choices() is 2'.format(
                    self.model.__name__))
        if fields:
            for field in fields:
                if field not in self.model._field_names:
                    raise ValueError('{0}.members.choices() requires {0} field name(s)'.format(
                        self.model.__name__))
        else:
            fields = self.model._field_names[:2]

        if len(fields) < 2:
            fields = [fields[0], fields[0]]

        return self.filter(**criteria).values_list(*fields)


class StaticModel(metaclass=StaticModelMeta):
    """
    Base class for static models.
    """
    class StaticModelError(Exception):
        pass

    class DoesNotExist(StaticModelError):
        pass

    class MultipleObjectsReturned(StaticModelError):
        pass

    class InvalidField(StaticModelError):
        pass

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __repr__(self):
        return '<{}.{}: {}>'.format(
            self.__class__.__name__,
            getattr(self, AttrName.INSTANCE.MEMBER_NAME),
            format_kwargs(self._as_dict),
        )

    @property
    def _as_dict(self):
        return OrderedDict(
            (field_name, getattr(self, field_name, None))
            for field_name in self._field_names)


class StaticModelMembers(list):

    def __init__(self, *args, **kwargs):
        self.model = kwargs.pop('model')
        super().__init__(*args, **kwargs)

    def _values_base(self, item_func, *field_names, **kwargs):
        allow_flat = kwargs.pop('allow_flat', False)
        flat = kwargs.pop('flat', False)

        if not field_names:
            field_names = self.model._field_names

        elif not frozenset(field_names).issubset(frozenset(chain(
                (AttrName.INSTANCE.MEMBER_NAME,
                 AttrName.INSTANCE.MEMBER_NAME),
                chain(self.model.__dict__.keys(), self.model._field_names),
                chain.from_iterable(chain(
                    submodel.__dict__.keys(), submodel._field_names)
                        for submodel in self.model.submodels())
                ))):
            raise ValueError(
                "Field names must be a subset of those available.")

        results = []

        if allow_flat and flat:
            for rendered_item in chain.from_iterable(
                    item_func(item, field_names) for item in self):
                if rendered_item:
                    results.append(rendered_item)
        else:
            for item in self:
                rendered_item = item_func(item, field_names)
                if rendered_item:
                    results.append(rendered_item)

        return results

    def _values_item(item, field_names):
        item_dict = item._as_dict
        return OrderedDict((key, item_dict.pop(key, None)) for key in field_names)
    values = partialmethod(_values_base, _values_item)

    def _values_list_item(item, field_names):
        rendered_item = []
        for field_name in field_names:
            rendered_item.append(getattr(item, field_name, None))
        return tuple(rendered_item)
    values_list = partialmethod(_values_base, _values_list_item, allow_flat=True)
