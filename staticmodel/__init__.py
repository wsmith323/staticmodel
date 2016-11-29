"""
********
Overview
********

**Static Model** provides a simple framework for modeling objects that
might otherwise be modeled using persistence technologies such as
the Django ORM, but that do not belong in the database.

******
Models
******

A model is defined using a class definition to create a sub-class
of StaticModel.

Member field names are declared with the `_field_names` class
attribute. The value should be a sequence of strings.

Members are declared with an uppercase class attribute. Member values
should be sequences with the same number of items as the value of
`_field_names`.

When the class definition is processed by the underlying metaclass,
the **members are transformed into instances of the model**.

>>> from staticmodel import StaticModel
>>>
>>>
>>> class Animal(StaticModel):
...     _field_names = 'name', 'description', 'domesticated'
...
...     DOG = 'Spot', "Man's best friend", True
...     CAT = 'Fluffy', "Man's gracious overlord", True
>>>

The entire collection of members can be retrieved with the ``members.all()`` method.

>>> from pprint import pprint as pp
>>>
>>>
>>> pp(list(Animal.members.all()))
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>]
>>>

 **NOTE:** These methods return generators:

   - ``members.all()``
   - ``members.filter()``
   - ``members.values()``
   - ``members.values_list()``

 For demonstration purposes in all of these examples, we consume
 those generators with ``list()``.

**********
Sub-models
**********

Models can have sub-models. Sub-models are created using normal
sub-class semantics.

>>> class WildAnimal(Animal):
...     DEER = 'Bambi', 'Likes to hide', False
...     ANTELOPE = 'Speedy', 'Likes to run', False
>>>

Sub-models **inherit the _field_names attribute** of their parent model.

>>> WildAnimal._field_names
('name', 'description', 'domesticated')
>>>
>>> WildAnimal.DEER
<WildAnimal.DEER: name='Bambi', description='Likes to hide', domesticated=False>
>>>

However, sub-models **DO NOT inherit the members** of their parent model.

>>> WildAnimal.DOG
Traceback (most recent call last):
    ...
AttributeError: 'WildAnimal' model does not contain member 'DOG'
>>>
>>> pp(list(WildAnimal.members.all()))
[<WildAnimal.DEER: name='Bambi', description='Likes to hide', domesticated=False>,
 <WildAnimal.ANTELOPE: name='Speedy', description='Likes to run', domesticated=False>]
>>>

Parent models **gain the members** of their sub-models. Notice that the
**Animal** model now contains the members just defined in the
**WildAnimal** sub-model.

>>> pp(list(Animal.members.all()))
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>,
 <WildAnimal.DEER: name='Bambi', description='Likes to hide', domesticated=False>,
 <WildAnimal.ANTELOPE: name='Speedy', description='Likes to run', domesticated=False>]
>>>

The members that the parent has gained behave just like the members
that were defined in the parent model, except they are instances of
the sub-model instead of the parent model.

>>> Animal.DEER
<WildAnimal.DEER: name='Bambi', description='Likes to hide', domesticated=False>
>>>

*********************
Member access methods
*********************

A model member may be retrieved using the model's ``members.get()`` method.

>>> WildAnimal.members.get(name='Bambi')
<WildAnimal.DEER: name='Bambi', description='Likes to hide', domesticated=False>
>>>

Model members may be filtered with the model's ``members.filter()`` method.

>>> pp(list(Animal.members.filter(domesticated=True)))
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>]
>>>

Additional field names can be provided by overriding ``_field_names``
in sub-models. If the intent is to extend the parent model's
field definitions, a good practice is to reference the parent
model's values as demonstrated in the **SmallHousePet** model below.

>>> class SmallHousePet(Animal):
...     _field_names = Animal._field_names + ('facility',)
...
...     FISH = 'Nemo', 'Found at last', True, 'tank'
...     RODENT = 'Freddy', 'The Golden One', True, 'cage'
>>>

Filtering a model with an field name that is not in ``_field_names``
will raise a ValueError exception.

>>> pp(list(SmallHousePet.members.filter(species='hamster')))
Traceback (most recent call last):
    ...
ValueError: Invalid field 'species'
>>>

The name of the member used on the model is also available.

>>> member = SmallHousePet.members.get(_member_name='FISH')
>>> member
<SmallHousePet.FISH: name='Nemo', description='Found at last', domesticated=True, facility='tank'>
>>>
>>> member._member_name
'FISH'
>>> pp(list(Animal.members.filter(_member_name='RODENT')))
[<SmallHousePet.RODENT: name='Freddy', description='The Golden One', domesticated=True, facility='cage'>]
>>>

Sub-models can provide completely different field names if desired.

>>> class FarmAnimal(Animal):
...     _field_names = 'food_provided', 'character', 'occupation', 'butcher_involved'
...     PIG = 'bacon', 'Porky Pig', "President, All Folks Actors Guild", True
...     CHICKEN = 'eggs', 'Chicken Little', 'Salesman, Falling Sky Insurance', False
>>>

>>> pp(list(FarmAnimal.members.all()))
[<FarmAnimal.PIG: food_provided='bacon', character='Porky Pig', occupation='President, All Folks Actors Guild', butcher_involved=True>,
 <FarmAnimal.CHICKEN: food_provided='eggs', character='Chicken Little', occupation='Salesman, Falling Sky Insurance', butcher_involved=False>]
>>> pp(list(FarmAnimal.members.filter(butcher_involved=True)))
[<FarmAnimal.PIG: food_provided='bacon', character='Porky Pig', occupation='President, All Folks Actors Guild', butcher_involved=True>]
>>>

Only field names that exist on the model can be used. Parent models
know nothing about sub-model fields.

>>> pp(list(Animal.members.filter(butcher_involved=True)))
Traceback (most recent call last):
...
ValueError: Invalid field 'butcher_involved'
>>>

=====================
Primitive Collections
=====================

Model members may be rendered as primitive collections.

>>> # Custom function for formatting primitive collections that returns
>>> # the same results in python 2 and 3.
>>> from staticmodel.util import jsonify
>>>
>>>
>>> jsonify(list(SmallHousePet.members.values()))
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
>>> jsonify(list(SmallHousePet.members.values_list()))
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

The same rules apply for ``criteria`` as for ``.filter()`` with regards to
valid fields.

>>> jsonify(list(Animal.members.values(criteria={'species': 'hamster'})))
Traceback (most recent call last):
    ...
ValueError: Invalid field 'species'
>>>

Notice that when the ``Animal`` model was used to execute ``.values()`` or
``.values_list()``, the ``facility`` field was not included in the
results. This is because the default fields for these methods is
the value of ``Animal._field_names``, which does not include ``facility``.

Specific fields for ``.values()`` and ``.values_list()`` may be
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

Notice that some members have the ``facility`` field and some don't,
reflecting their actual contents. No placeholders are added in the
results.

Members that don't have ANY of the fields are excluded from the
results. In the following examples, notice the absence of
``FarmAnimal`` members.

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

The ``values_list()`` method can be passed the ``flat=True`` parameter
to collapse the values in the result. This usually only makes sense
when limiting the results to a single field name.

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
from .core import StaticModel
