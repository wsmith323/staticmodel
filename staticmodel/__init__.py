"""
************
Introduction
************

**Static Model** is a simple framework for modeling what can be thought
of as "complex constants".

===========================
What is a complex constant?
===========================

To explain what complex constants are, it first helps to understand
what they are not.

The data that our software processes is often represented as
collections of multi-valued objects. These collections are often
stored in a database and frameworks such as the Django ORM can be used
to define and access them. Each item in the collection may have one or
more unique identifiers, but the code does not know or care about any
specific item in the collection. These collections are *NOT* complex
constants.

Some collections, though, are tightly integrated with the code, in that
the code uses specific items and values within a collection to affect
its behavior. These collections should not be stored in a database.
Doing so introduces many problems into the development, maintainence,
and deployment of the code. These collections should be defined
statically and used throughout the code via those definitions. Those
definitions *ARE* complex constants. Like normal constants, they are
stored in memory only.

**Can't we just use built-in collection types for this?**

The simple answer is: **Yes**.

However, as our code evolves and the collections become more numerous,
gain more members, and gain more values, using the built-in types leads
to code that is harder to write, harder to read, verbose, repetitive,
and ugly.

**Static Model** was created to solve these problems.

But before we delve into the features of Static Model, lets look
at some of the problems associated with implementing complex
constants using built-in collection types.

==================================================
The problems using built-ins for complex constants
==================================================

Let's start with a couple of normal constants and then modify them
as the code evolves.

>>> # Prettier collection display
>>> from pprint import pprint as pp
>>>
>>>
>>> ANIMAL_TYPE_ID_DOG = 1
>>> ANIMAL_TYPE_ID_AFRICAN_SWALLOW = 2
>>>
>>>
>>> class Animal(object):
...     def __init__(self, name, type_id):
...         self.name = name
...         self.type_id = type_id
...
...         self.can_fly = type_id == ANIMAL_TYPE_ID_AFRICAN_SWALLOW
...         self.domesticated = type_id == ANIMAL_TYPE_ID_DOG
...
...     def __repr__(self):
...         return "<{}: name={!r}, type_id={!r}>".format(
...             self.__class__.__name__, self.name, self.type_id)
...
...     def fly(self):
...         if self.can_fly:
...             return "My name is {}. Taking off now.".format(self.name)
...         elif self.domesticated:
...             return "My name is {}. My owner is nuts.".format(self.name)
...         else:
...             return "My name is {}. Unable to comply.".format(self.name)
...
...
>>> animals = [Animal('Spot', ANIMAL_TYPE_ID_DOG), Animal('Coco', ANIMAL_TYPE_ID_AFRICAN_SWALLOW)]
>>>
>>> pp(animals)
[<Animal: name='Spot', type_id=1>, <Animal: name='Coco', type_id=2>]
>>> pp([animal.fly() for animal in animals])
['My name is Spot. My owner is nuts.', 'My name is Coco. Taking off now.']

Naming and using constants this way is common in many languages. The
upper case names signify to the developer that the values cannot or
should not be changed once the initial values are assigned. The shared
prefix in the name establishes that these constants are associated with
each other and our class definition. The code compares variables to the
constants to affect its behavior.

But, what if we need the constant values to have associated values?

That sounds like the perfect use case for the built-in mapping type,
 the dictionary:

>>> ANIMAL_TYPE_ID_DOG = 1
>>> ANIMAL_TYPE_ID_AFRICAN_SWALLOW = 2
>>>
>>>
>>> ANIMAL_TYPE_NAME_MAP = {
...     ANIMAL_TYPE_ID_DOG: 'Dog',
...     ANIMAL_TYPE_ID_AFRICAN_SWALLOW: 'African Swallow',
...     }
>>>
>>>
>>> class Animal(object):
...     def __init__(self, name, type_id):
...         self.name = name
...         self.type_id = type_id
...         self.type_name = ANIMAL_TYPE_NAME_MAP[self.type_id]
...
...         self.can_fly = type_id == ANIMAL_TYPE_ID_AFRICAN_SWALLOW
...         self.domesticated = type_id == ANIMAL_TYPE_ID_DOG
...
...     def __repr__(self):
...         return "<{}: name={!r}, type_id={}, type_name={!r}>".format(
...             self.__class__.__name__, self.name, self.type_id, self.type_name)
...
...     def fly(self):
...         if self.can_fly:
...             return "{}: My name is {}. Taking off now.".format(self.type_name, self.name)
...         elif self.domesticated:
...             return "{}: My name is {}. My owner is nuts.".format(self.type_name, self.name)
...         else:
...             return "{}: My name is {}. Unable to comply.".format(self.name, selftype_name)
...
...
>>> animals = [Animal('Spot', ANIMAL_TYPE_ID_DOG), Animal('Coco', ANIMAL_TYPE_ID_AFRICAN_SWALLOW)]
>>>
>>> pp(animals)
[<Animal: name='Spot', type_id=1, type_name='Dog'>,
 <Animal: name='Coco', type_id=2, type_name='African Swallow'>]
>>> pp([animal.fly() for animal in animals])
['Dog: My name is Spot. My owner is nuts.',
 'African Swallow: My name is Coco. Taking off now.']

This works well enough, but what happens when we add more animal
types and behavior that depends on them?

>>> ANIMAL_TYPE_ID_DOG = 1
>>> ANIMAL_TYPE_ID_AFRICAN_SWALLOW = 2
>>> ANIMAL_TYPE_ID_CAT = 3
>>> ANIMAL_TYPE_ID_SNAKE = 4
>>>
>>>
>>> ANIMAL_TYPE_NAME_MAP = {
...     ANIMAL_TYPE_ID_DOG: 'Dog',
...     ANIMAL_TYPE_ID_AFRICAN_SWALLOW: 'African Swallow',
...     ANIMAL_TYPE_ID_CAT: 'Cat',
...     ANIMAL_TYPE_ID_SNAKE: 'Snake',
...     }
>>>
>>>
>>> class Animal(object):
...     leg_count = 0
...
...     def __init__(self, name, type_id):
...         self.name = name
...         self.type_id = type_id
...         self.type_name = ANIMAL_TYPE_NAME_MAP[self.type_id]
...
...         self.can_fly = type_id == ANIMAL_TYPE_ID_AFRICAN_SWALLOW
...         self.domesticated = type_id in (ANIMAL_TYPE_ID_DOG, ANIMAL_TYPE_ID_CAT)
...         self.likes_to_swim = type_id in (ANIMAL_TYPE_ID_DOG, ANIMAL_TYPE_ID_SNAKE)
...
...         if type_id == ANIMAL_TYPE_ID_SNAKE:
...             self.leg_count = 0
...         elif type_id == ANIMAL_TYPE_ID_AFRICAN_SWALLOW:
...             self.leg_count = 2
...         else:
...             self.leg_count = 4
...
...     def __repr__(self):
...         return "<{}: name={!r}, type_id={}, type_name-{}>".format(
...             self.__class__.__name__, self.name, self.type_id, self.type_name)
...
...     def fly(self):
...         if self.can_fly:
...             return "{}: My name is {}. Taking off now.".format(self.type_name, self.name)
...         elif self.domesticated:
...             return "{}: My name is {}. My owner is nuts.".format(self.type_name, self.name)
...         else:
...             return "{}: My name is {}. Unable to comply.".format(self.type_name, self.name)
...
...     def walk(self):
...         if self.leg_count == 0:
...             return "{}s can't walk. No legs.".format(self.type_name)
...         elif self.can_fly:
...             return "Ok, but I'd rather fly"
...         else:
...             return "Walking"
...
...     def swim(self):
...         return ("Swimming" if self.likes_to_swim else "{}s don't like to swim.".format(
...             self.type_name))
...
...
>>> animals = [
...     Animal('Spot', ANIMAL_TYPE_ID_DOG),
...     Animal('Coco', ANIMAL_TYPE_ID_AFRICAN_SWALLOW),
...     Animal('Fluffy', ANIMAL_TYPE_ID_CAT),
...     Animal('Sly', ANIMAL_TYPE_ID_SNAKE),
... ]
>>>
>>> pp(animals)
[<Animal: name='Spot', type_id=1, type_name-Dog>,
 <Animal: name='Coco', type_id=2, type_name-African Swallow>,
 <Animal: name='Fluffy', type_id=3, type_name-Cat>,
 <Animal: name='Sly', type_id=4, type_name-Snake>]
>>> pp([animal.fly() for animal in animals])
['Dog: My name is Spot. My owner is nuts.',
 'African Swallow: My name is Coco. Taking off now.',
 'Cat: My name is Fluffy. My owner is nuts.',
 'Snake: My name is Sly. Unable to comply.']
>>> pp([animal.walk() for animal in animals])
['Walking', "Ok, but I'd rather fly", 'Walking', "Snakes can't walk. No legs."]
>>> pp([animal.swim() for animal in animals])
['Swimming',
 "African Swallows don't like to swim.",
 "Cats don't like to swim.",
 'Swimming']

When we add more constant values, the code begins to get repetitious.

Also, the imperative code necessary to determine the main class
attributes starts to get relatively complicated.

This code might be improved a bit by giving the constant mapping values
multiple attributes, making it more declarative. We could use some more
mappings to make this happen.

>>> ANIMAL_TYPE_ID_DOG = 1
>>> ANIMAL_TYPE_ID_AFRICAN_SWALLOW = 2
>>> ANIMAL_TYPE_ID_CAT = 3
>>> ANIMAL_TYPE_ID_SNAKE = 4
>>>
>>>
>>> ANIMAL_TYPE_ID_ATTR_MAP = {
...     ANIMAL_TYPE_ID_DOG: {'name': 'Dog', 'can_fly': False, 'domesticated': True, 'leg_count': 4,
...         'likes_to_swim': True},
...     ANIMAL_TYPE_ID_AFRICAN_SWALLOW: {'name': 'African Swallow', 'can_fly': True, 'domesticated': False, 'leg_count': 2,
...         'likes_to_swim': False},
...     ANIMAL_TYPE_ID_CAT: {'name': 'Cat', 'can_fly': False, 'domesticated': True, 'leg_count': 4,
...         'likes_to_swim': False},
...     ANIMAL_TYPE_ID_SNAKE: {'name': 'Snake', 'can_fly': False, 'domesticated': False,
...         'leg_count': 0, 'likes_to_swim': True},
...     }
>>>
>>>
>>> class Animal(object):
...     leg_count = 0
...
...     def __init__(self, name, type_id):
...         self.name = name
...         self.type_id = type_id
...
...         type_attrs = ANIMAL_TYPE_ID_ATTR_MAP[self.type_id]
...
...         self.type_name = type_attrs['name']
...         self.can_fly = type_attrs['can_fly']
...         self.domesticated = type_attrs['domesticated']
...         self.likes_to_swim = type_attrs['likes_to_swim']
...         self.leg_count = type_attrs['leg_count']
...
...     def __repr__(self):
...         return "<{}: name={!r}, type_id={}, type_name={!r}>".format(
...             self.__class__.__name__, self.name, self.type_id, self.type_name)
...
...     def fly(self):
...         if self.can_fly:
...             return "{}: My name is {}. Taking off now.".format(self.type_name, self.name)
...         elif self.domesticated:
...             return "{}: My name is {}. My owner is nuts.".format(self.type_name, self.name)
...         else:
...             return "{}: My name is {}. Unable to comply.".format(self.type_name, self.name)
...
...     def walk(self):
...         if self.leg_count == 0:
...             return "{}s can't walk. No legs.".format(self.type_name)
...         elif self.can_fly:
...             return "Ok, but I'd rather fly"
...         else:
...             return "Walking"
...
...     def swim(self):
...         return ("Swimming" if self.likes_to_swim
...                 else "{}s don't like to swim.".format(self.type_name))
...
...
>>> animals = [
...     Animal('Spot', ANIMAL_TYPE_ID_DOG),
...     Animal('Coco', ANIMAL_TYPE_ID_AFRICAN_SWALLOW),
...     Animal('Fluffy', ANIMAL_TYPE_ID_CAT),
...     Animal('Sly', ANIMAL_TYPE_ID_SNAKE),
... ]
>>>
>>> pp(animals)
[<Animal: name='Spot', type_id=1, type_name='Dog'>,
 <Animal: name='Coco', type_id=2, type_name='African Swallow'>,
 <Animal: name='Fluffy', type_id=3, type_name='Cat'>,
 <Animal: name='Sly', type_id=4, type_name='Snake'>]
>>> pp([animal.fly() for animal in animals])
['Dog: My name is Spot. My owner is nuts.',
 'African Swallow: My name is Coco. Taking off now.',
 'Cat: My name is Fluffy. My owner is nuts.',
 'Snake: My name is Sly. Unable to comply.']
>>> pp([animal.walk() for animal in animals])
['Walking', "Ok, but I'd rather fly", 'Walking', "Snakes can't walk. No legs."]
>>> pp([animal.swim() for animal in animals])
['Swimming',
 "African Swallows don't like to swim.",
 "Cats don't like to swim.",
 'Swimming']

The changes have made our class a little simpler, but have made our
constant declarations even more repetitious. In addition there is lots
of ugly noise created by using mappings with string literals.

We can get rid of some of the repetition and ugliness by replacing
the mappings with namedtuples and accessing the type attributes
where they are used instead of copying them to the instance in our
class's __init__ method.

>>> from collections import namedtuple
>>>
>>>
>>> ANIMAL_TYPE_ID_DOG = 1
>>> ANIMAL_TYPE_ID_AFRICAN_SWALLOW = 2
>>> ANIMAL_TYPE_ID_CAT = 3
>>> ANIMAL_TYPE_ID_SNAKE = 4
>>>
>>>
>>> AnimalTypeAttrs = namedtuple('AnimalTypeAttrs', (
...     'name', 'can_fly', 'domesticated', 'leg_count', 'likes_to_swim'))
>>>
>>>
>>> ANIMAL_TYPE_ID_ATTR_MAP = {
...     ANIMAL_TYPE_ID_DOG: AnimalTypeAttrs('Dog', False, True, 4, True),
...     ANIMAL_TYPE_ID_AFRICAN_SWALLOW: AnimalTypeAttrs('African Swallow', True, False, 2, False),
...     ANIMAL_TYPE_ID_CAT: AnimalTypeAttrs('Cat', False, True, 4, False),
...     ANIMAL_TYPE_ID_SNAKE: AnimalTypeAttrs('Snake', False, False, 0, True),
... }
>>>
>>>
>>> class Animal(object):
...     def __init__(self, name, type_id):
...         self.name = name
...         self.type_id = type_id
...         self.type_attrs = ANIMAL_TYPE_ID_ATTR_MAP[self.type_id]
...
...     def __repr__(self):
...         return "<{}: name={!r}, type_id={}, type_name={!r}>".format(
...             self.__class__.__name__, self.name, self.type_id, self.type_attrs.name)
...
...     def fly(self):
...         type_name = self.type_attrs.name
...         if self.type_attrs.can_fly:
...             return "{}: My name is {}. Taking off now.".format(type_name, self.name)
...         elif self.type_attrs.domesticated:
...             return "{}: My name is {}. My owner is nuts.".format(type_name, self.name)
...         else:
...             return "{}: My name is {}. Unable to comply.".format(type_name, self.name)
...
...     def walk(self):
...         if self.type_attrs.leg_count == 0:
...             return "{}s can't walk. No legs.".format(self.type_attrs.name)
...         elif self.type_attrs.can_fly:
...             return "Ok, but I'd rather fly"
...         else:
...             return "Walking"
...
...     def swim(self):
...         return ("Swimming" if self.type_attrs.likes_to_swim
...                 else "{}s don't like to swim.".format( self.type_attrs.name))
...
...
>>> animals = [
...     Animal('Spot', ANIMAL_TYPE_ID_DOG),
...     Animal('Coco', ANIMAL_TYPE_ID_AFRICAN_SWALLOW),
...     Animal('Fluffy', ANIMAL_TYPE_ID_CAT),
...     Animal('Sly', ANIMAL_TYPE_ID_SNAKE),
... ]
>>>
>>> pp(animals)
[<Animal: name='Spot', type_id=1, type_name='Dog'>,
 <Animal: name='Coco', type_id=2, type_name='African Swallow'>,
 <Animal: name='Fluffy', type_id=3, type_name='Cat'>,
 <Animal: name='Sly', type_id=4, type_name='Snake'>]
>>> pp([animal.fly() for animal in animals])
['Dog: My name is Spot. My owner is nuts.',
 'African Swallow: My name is Coco. Taking off now.',
 'Cat: My name is Fluffy. My owner is nuts.',
 'Snake: My name is Sly. Unable to comply.']
>>> pp([animal.walk() for animal in animals])
['Walking', "Ok, but I'd rather fly", 'Walking', "Snakes can't walk. No legs."]
>>> pp([animal.swim() for animal in animals])
['Swimming',
 "African Swallows don't like to swim.",
 "Cats don't like to swim.",
 'Swimming']

This is much better, but there are still issues. There is still a
lot of repetition in the code. Look at all the places where the
strings `ANIMAL` and `Animal` are used.

The relationship between our constants and our class is part of what
is causing the repetition. We are using the word 'animal' in our
constant definitions to communicate to the developer that they are
related to our class, but as far as the code is concerned, no real
relationship exists. Another reason is that the prefix-as-namespace
convention for naming constants is less than ideal.

In addition to the above issues, it is often necessary to build a
list of two-item tuples for use as choices with things like Django
model field definitions. We can use a list comprehension to create
such a list from our attribute mapping. However, since we want our
choice list to be in the same order that it is defined in the code,
a regular dict will no longer work, as it is unordered. Changing
our attribute mapping to an OrderedDict will fix this.

So, lets attempt to address as many of these issues as we can.

>>> from collections import namedtuple, OrderedDict
>>>
>>>
>>> # Simple descriptor class to represent a django model field
>>> class IntegerField(object):
...     def __init__(self, choices=None):
...         self.choices = choices if choices is not None else []
...
...     def __set__(self, instance, value):
...         if value not in self.choices:
...             raise ValueError("'{}' is not a valid choice".format(value))
...         self._value = value
...
...     def __get__(self, instance, owner):
...         return self._value
...
...
>>> class Animal(object):
...     class TypeId:
...         DOG = 1
...         AFRICAN_SWALLOW = 2
...         CAT = 3
...         SNAKE = 4
...
...     TypeAttrs = namedtuple('TypeAttrs', (
...         'name', 'can_fly', 'domesticated', 'leg_count', 'likes_to_swim'))
...
...     TYPE_ID_ATTR_MAP = OrderedDict([
...         (TypeId.DOG, TypeAttrs('Dog', False, True, 4, True)),
...         (TypeId.AFRICAN_SWALLOW, TypeAttrs('African Swallow', True, False, 2, False)),
...         (TypeId.CAT, TypeAttrs('Cat', False, True, 4, False)),
...         (TypeId.SNAKE, TypeAttrs('Snake', False, False, 0, True)),
...     ])
...
...     type_id = IntegerField(choices=[(type_id, type_attrs.name)
...         for type_id, type_attrs in TYPE_ID_ATTR_MAP.items()])
...
...     def __init__(self, name, type_id):
...         self.name = name
...         self.type_id = type_id
...         self.type_attrs = self.TYPE_ID_ATTR_MAP[self.type_id]
...
...     def __repr__(self):
...         return "<{}: name={!r}, type_id={}, type_name={!r}>".format(
...             self.__class__.__name__, self.name, self.type_id, self.type_attrs.name)
...
...     def fly(self):
...         type_name = self.type_attrs.name
...         if self.type_attrs.can_fly:
...             return "{}: My name is {}. Taking off now.".format(type_name, self.name)
...         elif self.type_attrs.domesticated:
...             return "{}: My name is {}. My owner is nuts.".format(type_name, self.name)
...         else:
...             return "{}: My name is {}. Unable to comply.".format(type_name, self.name)
...
...     def walk(self):
...         if self.type_attrs.leg_count == 0:
...             return "{}s can't walk. No legs.".format(self.type_attrs.name)
...         elif self.type_attrs.can_fly:
...             return "Ok, but I'd rather fly"
...         else:
...             return "Walking"
...
...     def swim(self):
...         return ("Swimming" if self.type_attrs.likes_to_swim
...                 else "{}s don't like to swim.".format(self.type_attrs.name))
...
...

Again, this is better. We have eliminated a lot of the repetition of
the word 'Animal' by moving our constant definitions into the class
namespace, replaced the prefix-as-namespace convention with a class
definition used solely for its namespace, and defined a choices
attribute for our types.

But there is still repetition in the code. Look at all the places that
the strings `TYPE` and `Type` are used. *Is there a way to decrease the
repetition even further?*

Another observation is that the behavior of the methods is entirely
dependent upon each animal's type. Ideally, we should move the
methods to the class of each type instance. We can do that with
namedtuples, but we have to create a subclass of the generated
class and then define our methods on it. Providing all these sub-classes
with behavior that applies to every member would require an additional
mixin definition and inclusion of that mixin in the super-class list
for each sub-class. *Is there a simpler way?*

Also, suppose we want choice lists that only contain portions of the
items, filtered on various combinations of attribute values. We could
use additional list comprehensions to build them, *but is there an
easier way?*

The answer to all these questions is *Yes, there is*.

=========================
The Static Model solution
=========================

To wet your appetite, lets take our existing code and refactor it using
**Static Model**.

>>> from staticmodel import StaticModel
>>>
>>>
>>> class Animal(object):
...     class Type(StaticModel):
...         _field_names = 'id', 'name', 'can_fly', 'domesticated', 'leg_count', 'likes_to_swim'
...         DOG = 1, 'Dog', False, True, 4, True
...         AFRICAN_SWALLOW = 2, 'African Swallow', True, False, 2, False
...         CAT = 3, 'Cat', False, True, 4, False
...         SNAKE = 4, 'Snake', False, False, 0, True
...
...         def fly(self, animal):
...             if self.can_fly:
...                 return "{}: My name is {}. Taking off now.".format(self.name, animal.name)
...             elif self.domesticated:
...                 return "{}: My name is {}. My owner is nuts.".format(self.name, animal.name)
...             else:
...                 return "{}: My name is {}. Unable to comply.".format(self.name, animal.name)
...
...         def walk(self, animal):
...             if self.leg_count == 0:
...                 return "{}s can't walk. No legs.".format(self.name)
...             elif self.can_fly:
...                 return "Ok, but I'd rather fly"
...             else:
...                 return "Walking"
...
...         def swim(self, animal):
...             return ("Swimming" if self.likes_to_swim
...                     else "{}s don't like to swim.".format(self.name))
...
...     def __init__(self, name, animal_type):
...         self.name = name
...         self.type = animal_type
...
...     def __repr__(self):
...         return "<{}: name={!r}, type={!r}>".format(
...             self.__class__.__name__, self.name, self.type)
...
...     def fly(self):
...         return self.type.fly(self)
...
...     def walk(self):
...         return self.type.walk(self)
...
...     def swim(self):
...         return self.type.swim(self)
...
...
>>> animals = [
...     Animal('Spot', Animal.Type.DOG),
...     Animal('Coco', Animal.Type.AFRICAN_SWALLOW),
...     Animal('Fluffy', Animal.Type.CAT),
...     Animal('Sly', Animal.Type.SNAKE),
... ]
>>>
>>> pp(animals)
[<Animal: name='Spot', type=<Type.DOG: id=1, name='Dog', can_fly=False, domesticated=True, leg_count=4, likes_to_swim=True>>,
 <Animal: name='Coco', type=<Type.AFRICAN_SWALLOW: id=2, name='African Swallow', can_fly=True, domesticated=False, leg_count=2, likes_to_swim=False>>,
 <Animal: name='Fluffy', type=<Type.CAT: id=3, name='Cat', can_fly=False, domesticated=True, leg_count=4, likes_to_swim=False>>,
 <Animal: name='Sly', type=<Type.SNAKE: id=4, name='Snake', can_fly=False, domesticated=False, leg_count=0, likes_to_swim=True>>]
>>> pp([animal.fly() for animal in animals])
['Dog: My name is Spot. My owner is nuts.',
 'African Swallow: My name is Coco. Taking off now.',
 'Cat: My name is Fluffy. My owner is nuts.',
 'Snake: My name is Sly. Unable to comply.']
>>> pp([animal.walk() for animal in animals])
['Walking', "Ok, but I'd rather fly", 'Walking', "Snakes can't walk. No legs."]
>>> pp([animal.swim() for animal in animals])
['Swimming',
 "African Swallows don't like to swim.",
 "Cats don't like to swim.",
 'Swimming']
>>>

Notice the lack of repetition in the constant declaration. Notice
that the type-dependent behavior has been moved to the Type class
and the Animal class delegates to those methods, passing itself
for context. Notice the provided api for building lists of
primitives.

These are just some of the features of **Static Model**.

**********
User Guide
**********

=============
Static Models
=============

A static model is defined using a class definition to create
a sub-class of ``staticmodel.StaticModel``.

Member field names are declared with the ``_field_names`` class
attribute. The value should be a sequence of strings.

Members are declared with an uppercase class attribute. Member values
should be sequences with the same number of items as the value of
``_field_names``.

The subclass of StaticModel that is created can have other attributes
and methods, just like a regular class. The only restriction is that
identifier names must be lower case or begin with an underscore.

Once the class has been defined, **the members are transformed into
instances of the model**.

>>> from staticmodel import StaticModel
>>>
>>>
>>> class AnimalType(StaticModel):
...     _field_names = 'name', 'description', 'domesticated', 'has_legs'
...     _WALKING_TEXT = "{} walking..."
...
...     DOG = 'Dog', "Man's best friend", True, True
...     CAT = 'Cat', "Man's gracious overlord", True, True
...     SNAKE = 'Snake', "Man's slithering companion", True, False
...
...     def walk(self):
...         if self.has_legs:
...             return self._WALKING_TEXT.format(self.name)
...         else:
...             return "{} can't walk.".format(self.name)
>>>

=====================
Member access methods
=====================

If the member name (the attribute name of the member defined on the
model) is known, it can be accessed just like any other attribute.

>>> AnimalType.DOG
<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>
>>>

The entire collection of members can be retrieved with the ``members.all()`` method.

>>> pp(AnimalType.members.all())
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>,
 <AnimalType.SNAKE: name='Snake', description="Man's slithering companion", domesticated=True, has_legs=False>]
>>> pp([item.walk() for item in AnimalType.members.all()])
['Dog walking...', 'Cat walking...', "Snake can't walk."]
>>>

Model members may be filtered with the model's ``members.filter()``
method.

>>> pp(AnimalType.members.filter(has_legs=True))
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>]
>>>

Providing no criteria to ``members.filter()`` is the same as calling
``members.all()``.

>>> pp(AnimalType.members.filter())
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>,
 <AnimalType.SNAKE: name='Snake', description="Man's slithering companion", domesticated=True, has_legs=False>]
>>>

The ``members.all()`` and ``members.filter()`` methods return an empty
list if no members were found.

>>> class NoMembers(StaticModel):
...     _field_names = ('something',)
...
>>> pp(NoMembers.members.all())
[]
>>> pp(NoMembers.members.filter(something='nothing'))
[]
>>>

A single model member may be retrieved directly using the model's
``members.get()`` method.

>>> AnimalType.members.get(name='Dog')
<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>
>>>

The ``members.get()`` method raises ``<model>.DoesNotExist`` if the query
is unsuccessful and ``<model>.MultipleObjectsReturned`` if more than one
is returned.

>>> try:
...     AnimalType.members.get(name='Eagle')
... except AnimalType.DoesNotExist as e:
...     print(e)
AnimalType.members.get(name='Eagle') yielded no objects.
>>> try:
...     AnimalType.members.get(domesticated=True)
... except AnimalType.MultipleObjectsReturned as e:
...     print(e)
AnimalType.members.get(domesticated=True) yielded multiple objects.
>>>

The ``members.choices()`` method is a shortcut for generating lists of
2 item tuples for use in Django field definitions, etc. By default, it
returns all members and uses the first two fields defined on the model.

>>> pp(AnimalType.members.choices())
[('Dog', "Man's best friend"),
 ('Cat', "Man's gracious overlord"),
 ('Snake', "Man's slithering companion")]
>>>

If field names are specified, there must be no more than 2.

>>> try:
...     AnimalType.members.choices('name', 'description', 'domesticated')
... except ValueError as e:
...     print(e)
Maximum number of specified fields for AnimalType.members.choices() is 2
>>>

If only a singe field name is provided, or if the model only has one
field, then the same field is used for both items of the tuple.

>>> pp(AnimalType.members.choices('name'))
[('Dog', 'Dog'), ('Cat', 'Cat'), ('Snake', 'Snake')]
>>>

The ``members.choices()`` method may also be provided with criteria to
limit the members included in the results, much like
``members.filter()``.

>>> pp(AnimalType.members.choices(has_legs=True))
[('Dog', "Man's best friend"), ('Cat', "Man's gracious overlord")]
>>> pp(AnimalType.members.choices('name', has_legs=True))
[('Dog', 'Dog'), ('Cat', 'Cat')]
>>>


----------------------
The _member_name field
----------------------

The name of each member's class attribute on the model and parent
models is available as the ``_member_name`` field on the member.

>>> AnimalType.DOG._member_name
'DOG'
>>>

The ``_member_name`` field *can* be used in member queries, though
getting the attribute off the model class is more concise.

>>> AnimalType.members.get(_member_name='CAT')
<AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>
>>> getattr(AnimalType, 'DOG')
<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>
>>>

==========
Sub-models
==========

Models can have sub-models. Sub-models are created using normal
sub-class syntax.

>>> class WildAnimalType(AnimalType):
...     DEER = 'Deer', 'Likes to hide', False, True
...     ANTELOPE = 'Antelope', 'Likes to run', False, True
...
...     def walk(self):
...         return '{}warily'.format(super().walk())
>>>

Sub-models inherit the ``_field_names`` attribute of their parent model.

>>> WildAnimalType._field_names
('name', 'description', 'domesticated', 'has_legs')
>>>
>>> WildAnimalType.DEER
<WildAnimalType.DEER: name='Deer', description='Likes to hide', domesticated=False, has_legs=True>
>>>

However, sub-models DO NOT inherit the members of their parent model.

>>> WildAnimalType.DOG
Traceback (most recent call last):
    ...
AttributeError: 'WildAnimalType' model does not contain member 'DOG'
>>>
>>> pp(WildAnimalType.members.all())
[<WildAnimalType.DEER: name='Deer', description='Likes to hide', domesticated=False, has_legs=True>,
 <WildAnimalType.ANTELOPE: name='Antelope', description='Likes to run', domesticated=False, has_legs=True>]
>>>

Parent models **gain the members** of their sub-models. Notice that the
``AnimalType`` model now contains the members just defined in the
``WildAnimalType`` sub-model.

>>> pp(AnimalType.members.all())
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>,
 <AnimalType.SNAKE: name='Snake', description="Man's slithering companion", domesticated=True, has_legs=False>,
 <WildAnimalType.DEER: name='Deer', description='Likes to hide', domesticated=False, has_legs=True>,
 <WildAnimalType.ANTELOPE: name='Antelope', description='Likes to run', domesticated=False, has_legs=True>]
>>>

The members that the parent has gained are accessed exactly the same
way as the other members, and behave as expected.

>>> pp([item.walk() for item in AnimalType.members.all()])
['Dog walking...',
 'Cat walking...',
 "Snake can't walk.",
 'Deer walking...warily',
 'Antelope walking...warily']
>>>


-----------------
Additional fields
-----------------

Additional field names can be provided by overriding ``_field_names``
in sub-models. A good practice is to reference the parent model's
values as demonstrated in the ``SmallHousePet`` model below.

>>> class SmallHousePet(AnimalType):
...     _field_names = AnimalType._field_names + ('facility',)
...
...     FISH = 'Fish', 'Likes to swim', True, True, 'tank'
...     RODENT = 'Rodent', 'Likes to eat', True, True, 'cage'
>>>

Member queries on the sub-model can use the additional field names.

>>> pp(SmallHousePet.members.filter(facility='tank'))
[<SmallHousePet.FISH: name='Fish', description='Likes to swim', domesticated=True, has_legs=True, facility='tank'>]
>>>

Parent models are not aware of additional fields that have been added
by sub-models, so those additional fields cannot be used in member
queries.

>>> try:
...     AnimalType.members.filter(facility='tank')
... except AnimalType.InvalidField as e:
...     print(e)
...
Invalid field 'facility'
>>>

=====================
Primitive Collections
=====================

Model members may be rendered as primitive collections.

The methods ``members.all()`` and ``members.filter()`` return a
list with the methods ``values()`` and ``values_list()`` defined on it.

The ``values()`` method returns a list of dictionaries.

>>> # Custom function that returns the same results in python 2 and 3
>>> # for lists containing dictionaries.
>>> from staticmodel.util import jsonify
>>>
>>>
>>> jsonify(AnimalType.members.all().values())
[
  {
    "name": "Dog",
    "description": "Man's best friend",
    "domesticated": true,
    "has_legs": true
  },
  {
    "name": "Cat",
    "description": "Man's gracious overlord",
    "domesticated": true,
    "has_legs": true
  },
  {
    "name": "Snake",
    "description": "Man's slithering companion",
    "domesticated": true,
    "has_legs": false
  },
  {
    "name": "Deer",
    "description": "Likes to hide",
    "domesticated": false,
    "has_legs": true
  },
  {
    "name": "Antelope",
    "description": "Likes to run",
    "domesticated": false,
    "has_legs": true
  },
  {
    "name": "Fish",
    "description": "Likes to swim",
    "domesticated": true,
    "has_legs": true
  },
  {
    "name": "Rodent",
    "description": "Likes to eat",
    "domesticated": true,
    "has_legs": true
  }
]
>>> jsonify(AnimalType.members.filter(name='Rodent').values())
[
  {
    "name": "Rodent",
    "description": "Likes to eat",
    "domesticated": true,
    "has_legs": true
  }
]
>>>

The ``values_list()`` method returns a list of tuples.

>>> pp(AnimalType.members.all().values_list())
[('Dog', "Man's best friend", True, True),
 ('Cat', "Man's gracious overlord", True, True),
 ('Snake', "Man's slithering companion", True, False),
 ('Deer', 'Likes to hide', False, True),
 ('Antelope', 'Likes to run', False, True),
 ('Fish', 'Likes to swim', True, True),
 ('Rodent', 'Likes to eat', True, True)]
>>> pp(AnimalType.members.filter(domesticated=False).values_list())
[('Deer', 'Likes to hide', False, True),
 ('Antelope', 'Likes to run', False, True)]
>>>

Notice that when the ``AnimalType`` model was used to execute ``.values()`` or
``.values_list()``, the ``facility`` field was not included in the
results. This is because the default fields for these methods is
the value of ``AnimalType._field_names``, which does not include ``facility``.

Specific fields for ``.values()`` and ``.values_list()`` may be
provided by passing them as positional parameters to those methods.

>>> jsonify(AnimalType.members.all().values('name', 'domesticated', 'facility'))
[
  {
    "name": "Dog",
    "domesticated": true,
    "facility": null
  },
  {
    "name": "Cat",
    "domesticated": true,
    "facility": null
  },
  {
    "name": "Snake",
    "domesticated": true,
    "facility": null
  },
  {
    "name": "Deer",
    "domesticated": false,
    "facility": null
  },
  {
    "name": "Antelope",
    "domesticated": false,
    "facility": null
  },
  {
    "name": "Fish",
    "domesticated": true,
    "facility": "tank"
  },
  {
    "name": "Rodent",
    "domesticated": true,
    "facility": "cage"
  }
]
>>> pp(AnimalType.members.all().values_list('name', 'description', 'facility'))
[('Dog', "Man's best friend", None),
 ('Cat', "Man's gracious overlord", None),
 ('Snake', "Man's slithering companion", None),
 ('Deer', 'Likes to hide', None),
 ('Antelope', 'Likes to run', None),
 ('Fish', 'Likes to swim', 'tank'),
 ('Rodent', 'Likes to eat', 'cage')]
>>>

Notice that some members have the ``facility`` field set to None (or null
when converted to JSON). These are placeholders for fields that were
requested, but do not exist on that member.

The ``values_list()`` method can be passed the ``flat=True`` parameter
to collapse the values in the result.

>>> jsonify(AnimalType.members.all().values_list('facility', flat=True))
[
  "tank",
  "cage"
]
>>>

Using ``flat=True`` usually only makes sense when limiting the results
to a single field name.

>>> jsonify(AnimalType.members.all().values_list('name', 'description', flat=True))
[
  "Dog",
  "Man's best friend",
  "Cat",
  "Man's gracious overlord",
  "Snake",
  "Man's slithering companion",
  "Deer",
  "Likes to hide",
  "Antelope",
  "Likes to run",
  "Fish",
  "Likes to swim",
  "Rodent",
  "Likes to eat"
]
>>>
"""
from .core import StaticModel

import os
with open(os.path.join(os.path.dirname(__file__), 'VERSION.txt')) as f:
    __version__ = f.read().strip()
