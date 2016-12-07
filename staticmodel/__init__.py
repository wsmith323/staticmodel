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
>>> pp(Animal.members.all())
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>]
>>>

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
>>> pp(WildAnimal.members.all())
[<WildAnimal.DEER: name='Bambi', description='Likes to hide', domesticated=False>,
 <WildAnimal.ANTELOPE: name='Speedy', description='Likes to run', domesticated=False>]
>>>

Parent models **gain the members** of their sub-models. Notice that the
**Animal** model now contains the members just defined in the
**WildAnimal** sub-model.

>>> pp(Animal.members.all())
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

>>> pp(Animal.members.filter(domesticated=True))
[<Animal.DOG: name='Spot', description="Man's best friend", domesticated=True>,
 <Animal.CAT: name='Fluffy', description="Man's gracious overlord", domesticated=True>]
>>>

*****************
Additional fields
*****************

Additional field names can be provided by overriding ``_field_names``
in sub-models. A good practice is to reference the parent model's
values as demonstrated in the ``SmallHousePet`` model below.

>>> class SmallHousePet(Animal):
...     _field_names = Animal._field_names + ('facility',)
...
...     FISH = 'Nemo', 'Found at last', True, 'tank'
...     RODENT = 'Freddy', 'The Golden One', True, 'cage'
>>>

Member queries on the sub-model can use the additional field names.

>>> pp(SmallHousePet.members.filter(facility='tank'))
[<SmallHousePet.FISH: name='Nemo', description='Found at last', domesticated=True, facility='tank'>]
>>>

Parent models are not aware of additional fields that have been added
by sub-models, so those additional fields cannot be used in member
queries.

>>> pp(Animal.members.filter(facility='tank'))
Traceback (most recent call last):
...
ValueError: Invalid field 'facility'
>>>

**********************
The _member_name field
**********************

The name of each member's class attribute on the model and parent
models is available as the ``_member_name`` field on the member.

>>> SmallHousePet.FISH._member_name
'FISH'
>>> Animal.FISH._member_name
'FISH'
>>>

The ``_member_name`` field can be used in member queries.

>>> Animal.members.get(_member_name='FISH')
<SmallHousePet.FISH: name='Nemo', description='Found at last', domesticated=True, facility='tank'>
>>> pp(Animal.members.filter(_member_name='RODENT'))
[<SmallHousePet.RODENT: name='Freddy', description='The Golden One', domesticated=True, facility='cage'>]
>>>

=====================
Primitive Collections
=====================

Model members may be rendered as primitive collections.

The ``members.all()`` method returns a sub-class of list with the
methods ``values()`` and ``values_list()`` defined on it.

>>> # Custom function for formatting primitive collections that returns
>>> # the same results in python 2 and 3.
>>> from staticmodel.util import jsonify
>>>
>>>
>>> jsonify(Animal.members.all().values())
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
>>> jsonify(Animal.members.filter(name='Freddy').values())
[
  {
    "name": "Freddy",
    "description": "The Golden One",
    "domesticated": true
  }
]
>>> jsonify(Animal.members.all().values_list())
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

Notice that when the ``Animal`` model was used to execute ``.values()`` or
``.values_list()``, the ``facility`` field was not included in the
results. This is because the default fields for these methods is
the value of ``Animal._field_names``, which does not include ``facility``.

Specific fields for ``.values()`` and ``.values_list()`` may be
provided by passing them as positional parameters to those methods.

>>> jsonify(Animal.members.all().values('name', 'domesticated', 'facility'))
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
>>> jsonify(Animal.members.all().values_list('name', 'description', 'facility'))
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
results.

>>> jsonify(Animal.members.all().values('facility'))
[
  {
    "facility": "tank"
  },
  {
    "facility": "cage"
  }
]
>>>
>>> jsonify(Animal.members.all().values_list('facility'))
[
  [
    "tank"
  ],
  [
    "cage"
  ]
]
>>>

The ``values_list()`` method can be passed the ``flat=True`` parameter
to collapse the values in the result.

>>> jsonify(Animal.members.all().values_list('facility', flat=True))
[
  "tank",
  "cage"
]

Using the ``flat=True`` usually only makes sense when limiting the
results to a single field name.

>>>
>>> jsonify(Animal.members.all().values_list('name', 'description', flat=True))
[
  "Spot",
  "Man's best friend",
  "Fluffy",
  "Man's gracious overlord",
  "Bambi",
  "Likes to hide",
  "Speedy",
  "Likes to run",
  "Nemo",
  "Found at last",
  "Freddy",
  "The Golden One"
]
>>>
"""
from .core import StaticModel

import os
with open(os.path.join(os.path.dirname(__file__), 'VERSION.txt')) as f:
    __version__ = f.read().strip()
