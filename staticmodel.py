"""
**StaticModel** provides a simple framework for modeling objects that
might otherwise be modeled using persistence technologies such as
the Django ORM, but that do not belong in the database.

******
Models
******

A model is defined using the class statement to create a sub-class
of StaticModel.

Member attribute names are declared with the `_attr_names` class
attribute. The value should be a sequence of strings.

Members are declared with an uppercase class attribute. Member values
should be sequences with the same number of items as the value of
`_attr_names`.

Members are instances of the Model.

>>> from __future__ import absolute_import
>>>
>>> from staticmodel import StaticModel
>>>
>>>
>>> class Animal(StaticModel):
...     _attr_names = 'name', 'description', 'domesticated'
...
...     DOG = 'Spot', "Man's best friend", True
...     CAT = 'Fluffy', "Man's gracious overlord", True
>>>

The entire collection of members can be retrieved with the :py:meth:`members.all` method.

>>> from pprint import pprint as pp
>>>
>>>
>>> pp(list(Animal.members.all()))
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>]
>>>

 **NOTE:** These :py:class:`StaticModel.members` methods return generators:

   - :py:meth:`~StaticModel.members.all`
   - :py:meth:`~StaticModel.members.filter`
   - :py:meth:`~StaticModel.members.values`
   - :py:meth:`~StaticModel.members.values_list`

 For demonstration purposes in all of these examples, we consume
 those generators with :py:func:`list`.

**********
Sub-models
**********

Models can have sub-models. Sub-models are created using normal
sub-class semantics.

>>> class Mammal(Animal):
...     DEER = 'Bambi', 'Likes to hide', False
...     ANTELOPE = 'Speedy', 'Likes to run', False
>>>

Sub-models **inherit the _attr_names attribute** of their parent model.

>>> Mammal._attr_names
('name', 'description', 'domesticated')
>>>
>>> Mammal.DEER
<Mammal.DEER: name='Bambi', description='Likes to hide', domesticated=False>
>>>

However, sub-models **DO NOT inherit the members** of their parent model.

>>> Mammal.DOG
Traceback (most recent call last):
    ...
AttributeError: 'Mammal' object has no attribute 'DOG'
>>>
>>> pp(list(Mammal.members.all()))
[<Mammal.DEER: name='Bambi', description='Likes to hide', domesticated=False>,
 <Mammal.ANTELOPE: name='Speedy', description='Likes to run', domesticated=False>]
>>>

Parent models **gain the members** of their sub-models. Notice that the
**Animal** model now contains the members just defined in the
**Mammal** sub-model.

>>> pp(list(Animal.members.all()))
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>,
 <Mammal.DEER: name='Bambi', description='Likes to hide', domesticated=False>,
 <Mammal.ANTELOPE: name='Speedy', description='Likes to run', domesticated=False>]
>>>

The members that the parent has gained behave just like the members
that were defined in the parent model, except they are instances of
the sub-model instead of the parent model.

>>> Animal.DEER
<Mammal.DEER: name='Bambi', description='Likes to hide', domesticated=False>
>>>

*********************
Member access methods
*********************

A model member may be retrieved using the model's :py:meth:`members.get` method.

>>> Mammal.members.get(name='Bambi')
<Mammal.DEER: name='Bambi', description='Likes to hide', domesticated=False>
>>>

Model members may be filtered with the model's :py:meth:`members.filter` method.

>>> pp(list(Animal.members.filter(domesticated=True)))
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>]
>>>

Additional attribute names can be provided by overriding `_attr_names`
in sub-models. If the intent is to extend the parent model's
attribute definitions, a good practice is to reference the parent
model's values as demonstrated in the **HousePet** model below.

Model filtering only uses attributes in the 'index' by default, and by
default, the index only includes the values of the base model's
`_attr_names` attribute. The index attributes of any model can be set
explicitly by overriding it's `_index_attr_names` attribute.

>>> class HousePet(Animal):
...     _attr_names = Animal._attr_names + ('facility',)
...     _index_attr_names = 'name', 'domesticated'
...
...     FISH = 'Nemo', 'Found at last', True, 'tank'
...     RODENT = 'Freddy', 'The Golden One', True, 'cage'
>>>

Filtering a model with an attribute name that is not in its index
will raise a ValueError exception.

>>> pp(list(HousePet.members.filter(species='clownfish')))
Traceback (most recent call last):
    ...
ValueError: Attribute 'species' is not in the index.
>>>

To force a non-indexed linear search over any and all attributes
that exist on any model members, add the keyword argument
`_unindexed_search=True` to the .filter() method.

>>> pp(list(HousePet.members.filter(facility='tank', _unindexed_search=True)))
[<HousePet.FISH: name='Nemo', description='Found at last', domesticated=True, facility='tank'>]
>>>

The name of the member used on the model is automatically in the
index and can be used in queries.

>>> HousePet.members.get(_member_name='FISH')
<HousePet.FISH: name='Nemo', description='Found at last', domesticated=True, facility='tank'>
>>>
>>> pp(list(Animal.members.filter(_member_name='RODENT')))
[<HousePet.RODENT: name='Freddy', description='The Golden One', domesticated=True, facility='cage'>]
>>>

Sub-models can provide completely different attribute names if desired.
If they do so, they should probably also provide corresponding index
values.

>>> class FarmAnimal(Animal):
...     _attr_names = 'food_provided', 'character', 'occupation', 'butcher_involved'
...     _index_attr_names = _attr_names
...     PIG = 'bacon', 'Porky Pig', "President, All Folks Actors Guild", True
...     CHICKEN = 'eggs', 'Chicken Little', 'Salesman, Falling Sky Insurance', False
>>>

=====================
Primitive Collections
=====================

Model members may be rendered as primitive collections.

>>> # Custom function for formatting primitive collections in doctest
>>> from jsonify import jsonify
>>>
>>>
>>> jsonify(list(HousePet.members.values()))
[
  {
    "name": "Nemo",
    "description": "Found at last",
    "domesticated": true,
    "facility": "tank"
  },
  {
    "name": "Freddy",
    "description": "The Golden One",
    "domesticated": true,
    "facility": "cage"
  }
]
>>>
>>> jsonify(list(HousePet.members.values_list()))
[
  [
    "Nemo",
    "Found at last",
    true,
    "tank"
  ],
  [
    "Freddy",
    "The Golden One",
    true,
    "cage"
  ]
]
>>>

The primitive collections may be filtered by providing criteria.

>>> jsonify(list(Animal.members.values(criteria={'name': 'Freddy'})))
[
  {
    "name": "Freddy",
    "description": "The Golden One",
    "domesticated": true
  }
]
>>>

The same rules apply for `criteria` as for .filter() with regards to
attributes in the index.

>>> jsonify(list(Animal.members.values(criteria={'facility': 'tank'})))
Traceback (most recent call last):
    ...
ValueError: Attribute 'facility' is not in the index.
>>>
>>> jsonify(list(Animal.members.values(criteria={'facility': 'tank', '_unindexed_search': True})))
[
  {
    "name": "Nemo",
    "description": "Found at last",
    "domesticated": true
  }
]
>>>

Notice that when the `Animal` model was used to execute .values() or
.values_list(), the `facility` attribute was not included in the
results. This is because the default attributes for these methods is
the value of Animal._attr_names, which does not include `facility`.

Specific attributes for model.values() and model.values_list() may be
provided by passing them as positional parameters to those methods.

>>> jsonify(list(Animal.members.values('name', 'domesticated', 'facility')))
[
  {
    "name": "Spot",
    "domesticated": true
  },
  {
    "name": "Fluffy",
    "domesticated": true
  },
  {
    "name": "Bambi",
    "domesticated": false
  },
  {
    "name": "Speedy",
    "domesticated": false
  },
  {
    "name": "Nemo",
    "domesticated": true,
    "facility": "tank"
  },
  {
    "name": "Freddy",
    "domesticated": true,
    "facility": "cage"
  }
]
>>>
>>> jsonify(list(Animal.members.values_list('name', 'description', 'facility')))
[
  [
    "Spot",
    "Man's best friend"
  ],
  [
    "Fluffy",
    "Man's gracious overlord"
  ],
  [
    "Bambi",
    "Likes to hide"
  ],
  [
    "Speedy",
    "Likes to run"
  ],
  [
    "Nemo",
    "Found at last",
    "tank"
  ],
  [
    "Freddy",
    "The Golden One",
    "cage"
  ]
]
>>>

Notice that some members have the `facility` attribute and some don't,
reflecting their actual contents. No placeholders are added in the
results.

Members that don't have ANY of the attributes are excluded from the
results. In the following examples, notice the absence of FarmAnimal members.

>>> jsonify(list(Animal.members.values()))
[
  {
    "name": "Spot",
    "description": "Man's best friend",
    "domesticated": true
  },
  {
    "name": "Fluffy",
    "description": "Man's gracious overlord",
    "domesticated": true
  },
  {
    "name": "Bambi",
    "description": "Likes to hide",
    "domesticated": false
  },
  {
    "name": "Speedy",
    "description": "Likes to run",
    "domesticated": false
  },
  {
    "name": "Nemo",
    "description": "Found at last",
    "domesticated": true
  },
  {
    "name": "Freddy",
    "description": "The Golden One",
    "domesticated": true
  }
]
>>>
>>> jsonify(list(Animal.members.values_list()))
[
  [
    "Spot",
    "Man's best friend",
    true
  ],
  [
    "Fluffy",
    "Man's gracious overlord",
    true
  ],
  [
    "Bambi",
    "Likes to hide",
    false
  ],
  [
    "Speedy",
    "Likes to run",
    false
  ],
  [
    "Nemo",
    "Found at last",
    true
  ],
  [
    "Freddy",
    "The Golden One",
    true
  ]
]
>>>

The model.values_list() method can be passed the `flat=True` parameter
to collapse the values in the result. This usually only makes sense
when combined with limiting the results to a single attribute name.

>>> jsonify(list(Animal.members.values_list('name', flat=True)))
[
  "Spot",
  "Fluffy",
  "Bambi",
  "Speedy",
  "Nemo",
  "Freddy"
]
>>>
"""
import six

from collections import Iterable, OrderedDict
from compat2.partialmethod import partialmethod
from itertools import chain
from compat2.simplenamespace import SimpleNamespace

from compat2.preparable import Prepareable


class ATTR_NAME:
    class CLASS_VAR:
        ATTR_NAMES = '_attr_names'
        INDEX_ATTR_NAMES = '_index_attr_names'
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
        attr_names = tuple(getattr(cls, ATTR_NAME.CLASS_VAR.ATTR_NAMES, ()))

        index_attr_names = tuple(getattr(
            cls, ATTR_NAME.CLASS_VAR.INDEX_ATTR_NAMES, ())) or attr_names

        setattr(cls, ATTR_NAME.CLASS_VAR.ATTR_NAMES, attr_names)
        setattr(cls, ATTR_NAME.CLASS_VAR.INDEX_ATTR_NAMES, index_attr_names)

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
        return '<StaticModel {}: Instances: {}, Indexes: {}>'.format(
            cls.__name__, len(cls._instances.by_id), cls._index_attr_names)

    def __getattribute__(cls, item):
        item = str(item)
        if item.upper() == item:
            try:
                return cls.__dict__[item]
            except KeyError:
                raise AttributeError('{!r} object has no attribute {!r}'.format(
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
            cls, raw_value=None, member_name=None, attr_names=None, *attr_values,
            **kwargs):
        if attr_values and raw_value:
            raise ValueError("Positional and 'raw_value' parameters are mutually"
                             " exclusive")

        if member_name is not None and member_name.upper() != member_name:
            raise ValueError(
                "Value for 'member_name' parameter must be all uppercase.")

        if raw_value and isinstance(raw_value, Iterable) and not isinstance(
                raw_value, str):
            attr_values = raw_value

        instance = super(StaticModelMeta, cls).__call__()

        attr_names = attr_names or cls._attr_names or tuple(
            'value{}'.format(i) for i in range(len(attr_values)))
        instance.__dict__.update(dict(zip(attr_names, attr_values)))

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
        for index_attr in (ATTR_NAME.INSTANCE_VAR.RAW_VALUE, ) + cls._index_attr_names:
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

        for attr_name, attr_value in sorted_kwargs:
            if attr_name == ATTR_NAME.INSTANCE_VAR.MEMBER_NAME:
                index = cls._instances.by_member_name
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


class StaticModelMemberManager:
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
    def _values_base(self, item_func, *attr_names, **kwargs):
        criteria = kwargs.pop('criteria', {})
        allow_flat = kwargs.pop('allow_flat', False)
        flat = kwargs.pop('flat', False)

        if not attr_names:
            attr_names = self.model._attr_names

        elif not frozenset(attr_names).issubset(frozenset(chain(
                (ATTR_NAME.INSTANCE_VAR.MEMBER_NAME,
                 ATTR_NAME.INSTANCE_VAR.MEMBER_NAME),
                chain(self.model.__dict__.keys(), self.model._attr_names),
                chain.from_iterable(chain(
                    submodel.__dict__.keys(), submodel._attr_names)
                        for submodel in self.model.submodels())
                ))):
            raise ValueError(
                "Attribute names must be a subset of those available.")

        if not criteria:
            results = self.all()
        else:
            results = self.filter(**criteria)

        if allow_flat and flat:
            for rendered_item in chain.from_iterable(
                    item_func(item, attr_names) for item in results):
                if rendered_item:
                    yield rendered_item
        else:
            for item in results:
                rendered_item = item_func(item, attr_names)
                if rendered_item:
                    yield rendered_item

    def _build_filter_error(self, kwargs):
        return self.model.DoesNotExist(
            '{}.filter({}) yielded no objects.'.format(
                self.model.__name__, _format_kwargs(kwargs)))

    #
    # Public API
    #
    def all(self):
        return (instance for instance in self.model._instances.by_id.values())

    def filter(self, **kwargs):
        if bool(kwargs.pop('_unindexed_search', False)):
            index_search_results = self.all()
        else:
            index_search_results = self.model._get_index_search_results(kwargs)

        validated_result_ids = set()
        for result in index_search_results:
            for attr_name, attr_value in kwargs.items():
                if (attr_name == ATTR_NAME.INSTANCE_VAR.MEMBER_NAME and
                        self.model._instances.by_member_name.get(
                            attr_value) is result):
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
                        self.model.__name__, _format_kwargs(kwargs)))

        try:
            next(results)
        except StopIteration:
            return result
        else:
            raise self.model.MultipleObjectsReturned(
                '{}.get({}) yielded multiple objects.'.format(
                    self.model.__name__, _format_kwargs(kwargs)))

    def _values_item(item, attr_names):
        rendered_item = []
        for attr_name in attr_names:
            attr_value = getattr(item, attr_name, None)
            if attr_value is not None:
                rendered_item.append((attr_name, attr_value))
        return OrderedDict(rendered_item)
    values = partialmethod(_values_base, _values_item)

    def _values_list_item(item, attr_names):
        rendered_item = []
        for attr_name in attr_names:
            attr_value = getattr(item, attr_name, None)
            if attr_value is not None:
                rendered_item.append(attr_value)
        return tuple(rendered_item)
    values_list = partialmethod(_values_base, _values_list_item, allow_flat=True)


class StaticModel(six.with_metaclass(StaticModelMeta)):
    """
    Base class for constant models.
    """
    def __repr__(self):
        return '<{}.{}: {}>'.format(
            self.__class__.__name__,
            getattr(self, ATTR_NAME.INSTANCE_VAR.MEMBER_NAME),
            _format_kwargs(OrderedDict(
                (attr_name, getattr(self, attr_name, None))
                for attr_name in self._attr_names)),
        )


def _format_kwargs(kwargs):
    return ', '.join('{}={!r}'.format(k, v) for k, v in kwargs.items())
