from collections import OrderedDict
from collections.abc import Iterable
from functools import partialmethod
from types import SimpleNamespace


class ATTR_NAME:
    class INSTANCE_VAR:
        CONSTANT_NAME = '_constant_name'
        RAW_VALUE = '_raw_value'


class ConstantModelMeta(type):
    _attr_names = tuple()

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
        cls._attr_names = tuple(kwargs.pop('attr_names', cls._attr_names))
        cls._index_attr_names = (ATTR_NAME.INSTANCE_VAR.RAW_VALUE,) + tuple(
            kwargs.pop('index_attr_names', cls._attr_names))

        super().__init__(*args, **kwargs)

        cls._instances = SimpleNamespace(
            by_id=OrderedDict(), by_constant_name=OrderedDict())
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

        cls._populate_ancestors(cls)

    def _populate_ancestors(cls, child):
        # This method recursively adds sub_class members to all
        # ancestor classes that are instances of this metaclass,
        # enabling parent classes to have members that are instances
        # of child classes not yet defined when the parent class
        # definition is executed.
        mcs = cls.__class__
        for parent in child.__bases__:
            if isinstance(parent, mcs):
                for member in cls.all():
                    constant_name = getattr(
                        member, ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME, None)
                    if constant_name is not None:
                        setattr(parent, constant_name, member)

                cls._populate_ancestors(parent)

    #
    # Public API
    #

    def __repr__(cls):
        return '<ConstantModel {}: Instances: {}, Indexes: {}>'.format(
            cls.__name__, len(cls._instances.by_id), cls._index_attr_names)

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
                instance = cls(raw_value=value, constant_name=key)

            super().__setattr__(key, instance)

    def __call__(
            cls, *attr_values, raw_value=None, constant_name=None, attr_names=None,
            **kwargs):
        if attr_values and raw_value:
            raise ValueError("Positional and 'raw_value' parameters are mutually"
                             " exclusive")

        if constant_name is not None and constant_name.upper() != constant_name:
            raise ValueError(
                "Value for 'constant_name' parameter must be all uppercase.")

        if raw_value and isinstance(raw_value, Iterable) and not isinstance(
                raw_value, str):
            attr_values = raw_value

        instance = super().__call__()

        attr_names = attr_names or cls._attr_names or tuple(
            'value{}'.format(i) for i in range(len(attr_values)))
        instance.__dict__.update(dict(zip(attr_names, attr_values)))

        setattr(instance, ATTR_NAME.INSTANCE_VAR.RAW_VALUE, raw_value)

        cls._process_new_instance(constant_name, instance)

        return instance

    def _process_new_instance(cls, constant_name, instance):
        instance_cn = getattr(instance, ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME, None)
        if instance_cn and constant_name and instance_cn != constant_name:
            raise ValueError(
                'Constant value {!r} already has a constant name'.format(
                    instance))

        setattr(instance, ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME, constant_name)

        cls._instances.by_id[id(instance)] = instance
        if constant_name is not None:
            cls._instances.by_constant_name[constant_name] = instance
        if cls._index_attr_names:
            cls._index_instance(instance)

    def all(cls):
        return (instance for instance in cls._instances.by_id.values())

    def filter(cls, **kwargs):
        if bool(kwargs.pop('_unindexed_search', False)):
            index_search_results = cls.all
        else:
            index_search_results = cls._get_index_search_results(kwargs)

        validated_result_ids = set()
        for result in index_search_results:
            for attr_name, attr_value in kwargs.items():
                if (attr_name == ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME and
                        cls._instances.by_constant_name.get(attr_value) is result):
                    continue

                try:
                    value = getattr(result, attr_name)
                except AttributeError:
                    break

                if value != attr_value:
                    break

            else:
                result_id = id(result)
                if result_id not in validated_result_ids:
                    validated_result_ids.add(result_id)
                    yield result

        if not validated_result_ids:
            raise cls._build_filter_error(kwargs)

    def get(cls, **kwargs):
        try:
            results = cls.filter(**kwargs)
            result = next(results)
        except cls.DoesNotExist:
            raise cls.DoesNotExist(
                '{}.get({}) yielded no objects.'.format(
                    cls.__name__, _format_kwargs(kwargs)))

        try:
            next(results)
        except StopIteration:
            return result
        else:
            raise cls.MultipleObjectsReturned(
                '{}.get({}) yielded multiple objects.'.format(
                    cls.__name__, _format_kwargs(kwargs)))

    def _values(cls, item_func, attr_names=None, criteria=None):
        if attr_names is None:
            attr_names = cls._attr_names

        elif not frozenset(attr_names).issubset(frozenset(cls._attr_names)):
            raise ValueError(
                "Parameter 'attr_names' is not a subset of available attribute names.")

        if criteria is None:
            results = cls.all
        else:
            results = cls.filter(**criteria)

        for item in results:
            yield item_func(item, attr_names)

    values = partialmethod(_values, lambda item, attr_names: dict(tuple(
        attr_name, getattr(item, attr_name, None)) for attr_name in attr_names))
    values_list = partialmethod(_values, lambda item, attr_names: tuple(
        getattr(item, attr_name, None) for attr_name in attr_names))

    #
    # Private API
    #
    def _index_instance(cls, instance):
        for index_attr in cls._index_attr_names:
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
        # Make sure ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME gets processed
        # first if it is present. There is no point in hitting the
        # other indexes if we miss there.
        sorted_kwargs = sorted(
            kwargs.items(), key=lambda x: x[0] != ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME)

        for attr_name, attr_value in sorted_kwargs:
            if attr_name == ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME:
                index = cls._instances.by_constant_name
                try:
                    result = index[attr_value]
                except KeyError:
                    raise StopIteration
                else:
                    yield result

            else:
                try:
                    index = cls._indexes[attr_name]
                except KeyError:
                    raise ValueError(
                        'Attribute {!r} is not in the index.'.format(attr_name))
                else:
                    result = index.get(cls._index_key_for_value(attr_value), [])
                    for item in result:
                        yield item

    def _build_filter_error(cls, kwargs):
        return cls.DoesNotExist(
            '{}.filter({}) yielded no objects.'.format(
                cls.__name__, _format_kwargs(kwargs)))

    class ConstantLookupError(Exception):
        pass

    class DoesNotExist(ConstantLookupError):
        pass

    class MultipleObjectsReturned(ConstantLookupError):
        pass


class ConstantModel(metaclass=ConstantModelMeta):
    def __repr__(self):
        return '{}({})'.format(self.__class__.__name__, _format_kwargs(self.__dict__))


def _format_kwargs(kwargs):
    return ', '.join('{}={!r}'.format(k, v) for k, v in kwargs.items())
