"""
**ConstantModel** provides a simple framework for modeling complex
*Statically Defined Objects*. These are objects that might otherwise
be modeled using persistence technologies such as Django models, but
that do not belong in the database.

#######################################
The case for Statically Defined Objects
#######################################

Often, portions of an application's data model are comprised of
*fixture* data. These are usually small collections of objects that
rarely change.

Often these fixtures are *code-significant*. In other words, the code
has knowledge about individual instances or groups of instances.

When these fixtures are modeled using traditional persistence
technologies, problems often arise. Keeping the persistently stored
versions of the objects correct across development, testing, staging,
and production environments becomes challenging.

Very often, there is no business reason for these collections of
objects to be in the database. The application users have no need
to modify them. The application provides no facility *to* modify them.
The hardware resources required to read them from persistent storage
is just needless overhead.

These objects are not really data at all. They are code. The only
versions that need to exist are the static definitions in the code,
and the instances in memory created by executing the code.

Furthermore, when the object definitions *do* occasionally change,
it is highly likely that those changes should be subject to the same
quality control processes as the rest of the code.

######################
Why use ConstantModel?
######################

Say we wanted to create a small collection of objects that modeled
animals. Each object would have significance in our code. Users would
not need to modify them. We now know that Statically Defined Objects
make much more sense than persisting these to the database.

These basic requirements could be satisfied using standard python
language features such as Enum, SimpleNamespace, namedtuple,
custom classes, etc.

However, requirements often get more complex. Let us also assert that
our animal objects will have multiple attributes. In addition, we need
a shallow class hierarchy with some polymorphic methods. Enum,
SimpleNamespace, and namedtuple just dropped out as contenders. We are
now in custom class territory. Let us further assert that we need to be
able to retrieve and filter these objects by their attribute values.
The amount of complexity in those custom classes just went way up. Now,
lets add the constraint that we desire code that is declarative,
concise, and has a fairly high signal-to-noise ratio. Well, in order for
us to have all the functionality we want, the complexity has to go
somewhere. We will have to find ways to remove it *from* our code, or
spend a considerable amount of time managing it *in* our code.

Enter ConstantModel.

ConstantModel is intended to simplify the creation of Statically
Defined Objects. ConstantModel definitions declare member attribute
names and member attribute values in a very concise manner. Members
are instances of the model. The ConstantModel metaclass processes each
model definition and provides each model with some special behavior.

The following explanations and examples provide details about that
behavior.

##########
The Basics
##########

******
Models
******

A model is defined using the class statement to create a sub-class
of ConstantModel.

Member attribute names are declared with the `_attr_names` class
attribute. The value should be a sequence of strings.

Members are declared with an uppercase class attribute. Member values
should be sequences with the same number of items as the value of
`_attr_names`.

Models can contain anything normal classes can contain, and that code
should work as expected, for the most part.

>>> from pprint import pprint as pp
>>>
>>> from constantmodel import ConstantModel
>>>
>>>
>>> class Animal(ConstantModel):
...     _attr_names = 'species', 'name', 'description', 'domesticated'
...
...     DOG = 'unknown', 'Spot', "Man's best friend", True
...     CAT = 'irrelevant', 'Fluffy', "Man's gracious overlord", True
...
...     model_greeting = 'Greetings.'
...     member_greeting = 'Hello.'
...
...     def member_talk(self, greeting=None):
...         greeting = greeting or self.member_greeting
...         print('{greeting} My name is {name}. Pleased to meet you.'.format(
...             greeting=greeting, name=self.get_name()))
...
...     def get_name(self):
...         return self.name
...
...     @classmethod
...     def model_talk(cls, greeting=None, members_spoken=None):
...         greeting = greeting or cls.model_greeting
...         print('{greeting} We are {cls.__name__}s.'.format(greeting=greeting,
...             cls=cls))
...
...         if members_spoken is None:
...             members_spoken = set()
...
...         for member in cls.all():
...             if member.__class__ is not cls:
...                 continue
...             member_id = id(member)
...             if member_id not in members_spoken:
...                 members_spoken.add(member_id)
...                 member.member_talk()
...
...         for submodel in cls.submodels():
...             submodel.model_talk(members_spoken=members_spoken)
...

The entire collection of members can be retrieved with the :py:meth:`~ConstantModel.all` method.

>>> pp(list(Animal.all()))
[<Animal.DOG: species='unknown', name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: species='irrelevant', name='Fluffy', description="Man's gracious overlord", domesticated=True>]
>>>

 **NOTE:** These :py:class:`ConstantModel` methods return generators:

   - :py:meth:`~ConstantModel.all`
   - :py:meth:`~ConstantModel.filter`
   - :py:meth:`~ConstantModel.values`
   - :py:meth:`~ConstantModel.values_list`

 For demonstration purposes in all of these examples, we consume
 those generators with :py:func:`list`.

**********
Sub-models
**********

Models can have sub-models. Sub-models are created using normal
sub-class semantics.

>>> class Mammal(Animal):
...     DEER = 'whitetail', 'Bambi', 'Likes to hide', False
...     ANTELOPE = 'pronghorn', 'Speedy', 'Likes to run', False

Sub-models **inherit the member attribute names** of their parent model.

>>> Mammal._attr_names
('species', 'name', 'description', 'domesticated')
>>>
>>> Mammal.DEER
<Mammal.DEER: species='whitetail', name='Bambi', description='Likes to hide', domesticated=False>
>>>

However, sub-models **DO NOT inherit the members** of their parent model.

>>> Mammal.DOG
Traceback (most recent call last):
    ...
AttributeError: 'Mammal' object has no attribute 'DOG'
>>>
>>> pp(list(Mammal.all()))
[<Mammal.DEER: species='whitetail', name='Bambi', description='Likes to hide', domesticated=False>,
 <Mammal.ANTELOPE: species='pronghorn', name='Speedy', description='Likes to run', domesticated=False>]
>>>

Parent models **gain the members** of their sub-models. Notice that the
**Animal** model now contains the members just defined in the
**Mammal** sub-model.

>>> pp(list(Animal.all()))
[<Animal.DOG: species='unknown', name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: species='irrelevant', name='Fluffy', description="Man's gracious overlord", domesticated=True>,
 <Mammal.DEER: species='whitetail', name='Bambi', description='Likes to hide', domesticated=False>,
 <Mammal.ANTELOPE: species='pronghorn', name='Speedy', description='Likes to run', domesticated=False>]
>>>

The members that the parent has gained behave just like the members
that were defined in the parent model, except they are instances of
the sub-model instead of the parent model.

>>> Animal.DEER
<Mammal.DEER: species='whitetail', name='Bambi', description='Likes to hide', domesticated=False>
>>>

*********************
Member access methods
*********************

A model member may be retrieved using the model's :py:meth:`~ConstantModel.get` method.

>>> Mammal.get(name='Bambi')
<Mammal.DEER: species='whitetail', name='Bambi', description='Likes to hide', domesticated=False>
>>>

Model members may be filtered with the model's :py:meth:`~ConstantModel.filter` method.

>>> pp(list(Animal.filter(domesticated=True)))
[<Animal.DOG: species='unknown', name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: species='irrelevant', name='Fluffy', description="Man's gracious overlord", domesticated=True>]
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
...     _index_attr_names = 'name', 'domesticated', 'facility'
...
...     FISH = 'clownfish', 'Nemo', 'Found at last', True, 'tank'
...     RODENT = 'hamster', 'Freddy', 'The Golden One', True, 'cage'
...
...     def member_talk(self, greeting=None):
...         super().member_talk(
...             greeting=greeting or "Come in. Excuse the mess. My human hasn't cleaned"
...                 " my {} in a while.".format(self.facility))
...
>>>

Filtering a model with an attribute name that is not in its index
will raise a ValueError exception.

>>> pp(list(HousePet.filter(species='clownfish')))
Traceback (most recent call last):
    ...
ValueError: Attribute 'species' is not in the index.
>>>

To force a non-indexed linear search over any and all attributes
that exist on any model members, add the keyword argument
`_unindexed_search=True` to the .filter() method.

>>> pp(list(HousePet.filter(species='clownfish', _unindexed_search=True)))
[<HousePet.FISH: species='clownfish', name='Nemo', description='Found at last', domesticated=True, facility='tank'>]
>>>

The name of the constant used on the model is automatically in the
index and can be used in queries.

>>> HousePet.get(_constant_name='FISH')
<HousePet.FISH: species='clownfish', name='Nemo', description='Found at last', domesticated=True, facility='tank'>
>>>
>>> pp(list(Animal.filter(_constant_name='RODENT')))
[<HousePet.RODENT: species='hamster', name='Freddy', description='The Golden One', domesticated=True, facility='cage'>]
>>>

Sub-models can provide completely different attribute names if desired.
If they do so, they should probably also provide corresponding index
values.

>>> class FarmAnimal(Animal):
...     _attr_names = 'food_provided', 'character', 'occupation', 'butcher_involved'
...     _index_attr_names = _attr_names
...     PIG = 'bacon', 'Porky Pig', "President, All Folks Actors Guild", True
...     CHICKEN = 'eggs', 'Chicken Little', 'Salesman, Falling Sky Insurance', False
...
...     model_greeting = 'Howdy!'
...     member_greeting = 'Howdy!'
...
...     def member_talk(self, greeting=None):
...         if self.butcher_involved:
...             super().member_talk(greeting="Help! Save me! They are going to eat me!")
...         else:
...             super().member_talk(greeting=greeting)
...
...     @classmethod
...     def model_talk(cls, greeting=None, members_spoken=None):
...         super().model_talk(greeting=greeting, members_spoken=members_spoken)
...         print("Well, we shur did 'njoy chewin' the fat for a spell.")
...         print("Ya'll come back an' see us real soon now, ya hear!")
...         print("(And don't pay Porky no mine. He always bin a bit of a drama queen.)")
...
...     def get_name(self):
...         return self.character
>>>

=====================
Primitive Collections
=====================

Model members may be rendered as primitive collections.

>>> pp(list(HousePet.values()))
[{'species': 'clownfish',
  'name': 'Nemo',
  'description': 'Found at last',
  'domesticated': True,
  'facility': 'tank'},
 {'species': 'hamster',
  'name': 'Freddy',
  'description': 'The Golden One',
  'domesticated': True,
  'facility': 'cage'}]
>>>
>>> pp(list(HousePet.values_list()))
[('clownfish', 'Nemo', 'Found at last', True, 'tank'),
 ('hamster', 'Freddy', 'The Golden One', True, 'cage')]
>>>

The primitive collections may be filtered by providing criteria.

>>> pp(list(Animal.values(criteria={'species': 'hamster'})))
[{'species': 'hamster',
  'name': 'Freddy',
  'description': 'The Golden One',
  'domesticated': True}]
>>>

The same rules apply for `criteria` as for .filter() with regards to
attributes in the index.

>>> pp(list(Animal.values(criteria={'facility': 'tank'})))
Traceback (most recent call last):
    ...
ValueError: Attribute 'facility' is not in the index.
>>>
>>> pp(list(Animal.values(criteria={'facility': 'tank', '_unindexed_search': True})))
[{'species': 'clownfish',
  'name': 'Nemo',
  'description': 'Found at last',
  'domesticated': True}]
>>>

Notice that when the `Animal` model was used to execute .values() or
.values_list(), the `facility` attribute was not included in the
results. This is because the default attributes for these methods is
the value of Animal._attr_names, which does not include `facility`.

Specific attributes for model.values() and model.values_list() may be
provided via the `attr_names` parameter to those methods.

>>> pp(list(Animal.values(attr_names=['species', 'domesticated', 'facility'])), width=40)
[{'species': 'unknown',
  'domesticated': True},
 {'species': 'irrelevant',
  'domesticated': True},
 {'species': 'whitetail',
  'domesticated': False},
 {'species': 'pronghorn',
  'domesticated': False},
 {'species': 'clownfish',
  'domesticated': True,
  'facility': 'tank'},
 {'species': 'hamster',
  'domesticated': True,
  'facility': 'cage'}]
>>>
>>> pp(list(Animal.values_list(attr_names=['name', 'description', 'facility'])))
[('Spot', "Man's best friend"),
 ('Fluffy', "Man's gracious overlord"),
 ('Bambi', 'Likes to hide'),
 ('Speedy', 'Likes to run'),
 ('Nemo', 'Found at last', 'tank'),
 ('Freddy', 'The Golden One', 'cage')]
>>>

Notice that some members have the `facility` attribute and some don't,
reflecting their actual contents. No placeholders are added in the
results.

Members that don't have ANY of the attributes are excluded from the
results. In the following examples, notice the absence of FarmAnimal members.

>>> pp(list(Animal.values()))
[{'species': 'unknown',
  'name': 'Spot',
  'description': "Man's best friend",
  'domesticated': True},
 {'species': 'irrelevant',
  'name': 'Fluffy',
  'description': "Man's gracious overlord",
  'domesticated': True},
 {'species': 'whitetail',
  'name': 'Bambi',
  'description': 'Likes to hide',
  'domesticated': False},
 {'species': 'pronghorn',
  'name': 'Speedy',
  'description': 'Likes to run',
  'domesticated': False},
 {'species': 'clownfish',
  'name': 'Nemo',
  'description': 'Found at last',
  'domesticated': True},
 {'species': 'hamster',
  'name': 'Freddy',
  'description': 'The Golden One',
  'domesticated': True}]
>>>
>>> pp(list(Animal.values_list()))
[('unknown', 'Spot', "Man's best friend", True),
 ('irrelevant', 'Fluffy', "Man's gracious overlord", True),
 ('whitetail', 'Bambi', 'Likes to hide', False),
 ('pronghorn', 'Speedy', 'Likes to run', False),
 ('clownfish', 'Nemo', 'Found at last', True),
 ('hamster', 'Freddy', 'The Golden One', True)]
>>>

The model.values_list() method can be passed the `flat=True` parameter
to collapse the values in the result. This usually only makes sense
when combined with limiting the results to a single attribute name.

>>> pp(list(Animal.values_list(attr_names=['name'], flat=True)))
['Spot', 'Fluffy', 'Bambi', 'Speedy', 'Nemo', 'Freddy']
>>>

************
Polymorphism
************

When each model is defined, it registers itself with its parent model.
The sub-models of any model are available via the :py:meth:`~ConstantModel.submodels` method.

>>> pp(list(Animal.submodels()))
[<ConstantModel Mammal: Instances: 2, Indexes: ('species', 'name', 'description', 'domesticated')>,
 <ConstantModel HousePet: Instances: 2, Indexes: ('name', 'domesticated', 'facility')>,
 <ConstantModel FarmAnimal: Instances: 2, Indexes: ('food_provided', 'character', 'occupation', 'butcher_involved')>]
>>>

The following recursive function demonstrates using the :py:meth:`~ConstantModel.submodels` method
to walk the entire model tree.

>>> def walk_submodels(model, indent=''):
...     print('{}Model:{}'.format(indent, model.__name__))
...     print('{}  Members:'.format(indent))
...     for member in model.all():
...         print('{}    {}'.format(indent, member._constant_name))
...     submodels = list(model.submodels())
...     if submodels:
...         print('{}  Sub-models:'.format(indent))
...         new_indent = indent + '    '
...         for submodel in submodels:
...             walk_submodels(submodel, indent=new_indent)
...
>>> walk_submodels(Animal)
Model:Animal
  Members:
    DOG
    CAT
    DEER
    ANTELOPE
    FISH
    RODENT
    PIG
    CHICKEN
  Sub-models:
    Model:Mammal
      Members:
        DEER
        ANTELOPE
    Model:HousePet
      Members:
        FISH
        RODENT
    Model:FarmAnimal
      Members:
        PIG
        CHICKEN
>>>

Finally, polymorphic methods work as expected.

>>> Animal.model_talk(greeting='Grrrreeeeetings.')
Grrrreeeeetings. We are Animals.
Hello. My name is Spot. Pleased to meet you.
Hello. My name is Fluffy. Pleased to meet you.
Greetings. We are Mammals.
Hello. My name is Bambi. Pleased to meet you.
Hello. My name is Speedy. Pleased to meet you.
Greetings. We are HousePets.
Come in. Excuse the mess. My human hasn't cleaned my tank in a while. My name is Nemo. Pleased to meet you.
Come in. Excuse the mess. My human hasn't cleaned my cage in a while. My name is Freddy. Pleased to meet you.
Howdy! We are FarmAnimals.
Help! Save me! They are going to eat me! My name is Porky Pig. Pleased to meet you.
Howdy! My name is Chicken Little. Pleased to meet you.
Well, we shur did 'njoy chewin' the fat for a spell.
Ya'll come back an' see us real soon now, ya hear!
(And don't pay Porky no mine. He always bin a bit of a drama queen.)
>>>
"""
from collections import OrderedDict
from collections.abc import Iterable
from functools import partialmethod
from itertools import chain
from types import SimpleNamespace


class ATTR_NAME:
    class CLASS_VAR:
        ATTR_NAMES = '_attr_names'
        INDEX_ATTR_NAMES = '_index_attr_names'
    class INSTANCE_VAR:
        CONSTANT_NAME = '_constant_name'
        RAW_VALUE = '_raw_value'


class ConstantModelMeta(type):
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
        attr_names = tuple(getattr(cls, ATTR_NAME.CLASS_VAR.ATTR_NAMES, ()))

        index_attr_names = tuple(getattr(
            cls, ATTR_NAME.CLASS_VAR.INDEX_ATTR_NAMES, ())) or attr_names

        setattr(cls, ATTR_NAME.CLASS_VAR.ATTR_NAMES, attr_names)
        setattr(cls, ATTR_NAME.CLASS_VAR.INDEX_ATTR_NAMES, index_attr_names)

        super().__init__(*args, **kwargs)

        cls._submodels = OrderedDict()
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

    #
    # Public API
    #
    class ConstantLookupError(Exception):
        pass

    class DoesNotExist(ConstantLookupError):
        pass

    class MultipleObjectsReturned(ConstantLookupError):
        pass

    def __repr__(cls):
        return '<ConstantModel {}: Instances: {}, Indexes: {}>'.format(
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

    def submodels(cls):
        return (submodel for submodel in cls._submodels.keys())

    def register_submodel(cls, submodel):
        cls._submodels[submodel] = None

    def remove_submodel(cls, submodel):
        del cls._submodels[submodel]

    def all(cls):
        return (instance for instance in cls._instances.by_id.values())

    def filter(cls, **kwargs):
        if bool(kwargs.pop('_unindexed_search', False)):
            index_search_results = cls.all()
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

    def get(cls, _return_none=False, **kwargs):
        try:
            results = cls.filter(**kwargs)
            result = next(results)
        except cls.DoesNotExist:
            if _return_none:
                return None
            else:
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

    def _values_base(cls, item_func, attr_names=None, criteria=None, allow_flat=False,
                flat=False):
        if attr_names is None:
            attr_names = cls._attr_names

        elif not frozenset(attr_names).issubset(frozenset(chain(
                (ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME,
                 ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME),
                chain(cls.__dict__.keys(), cls._attr_names),
                chain.from_iterable(chain(
                    submodel.__dict__.keys(), submodel._attr_names)
                        for submodel in cls.submodels())
                ))):
            raise ValueError(
                "Parameter 'attr_names' is not a subset of available attribute names.")

        if criteria is None:
            results = cls.all()
        else:
            results = cls.filter(**criteria)

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
                if parent is ConstantModel:
                    continue
                for member in cls.all():
                    constant_name = getattr(
                        member, ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME, None)
                    if constant_name is not None:
                        setattr(parent, constant_name, member)
                parent.register_submodel(cls)
                cls._populate_ancestors(parent)

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


class ConstantModel(metaclass=ConstantModelMeta):
    """
    Base class for constant models.
    """
    def __repr__(self):
        return '<{}.{}: {}>'.format(
            self.__class__.__name__,
            getattr(self, ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME),
            _format_kwargs(OrderedDict(
                (attr_name, getattr(self, attr_name, None))
                for attr_name in self._attr_names)),
        )


def _format_kwargs(kwargs):
    return ', '.join('{}={!r}'.format(k, v) for k, v in kwargs.items())
