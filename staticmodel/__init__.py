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
>>> from staticmodel.util import jsonify
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
from .core import StaticModel
