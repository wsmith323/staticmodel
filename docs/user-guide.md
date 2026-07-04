# StaticModel User Guide


## StaticModel Classes


A StaticModel class is defined using a class definition to create a sub-class
of `staticmodel.StaticModel`.

Member field names are declared with the `_field_names` class
attribute. The value should be a sequence of strings.

Members are declared with an uppercase class attribute. Member values
should be sequences with the same number of items as the value of
`_field_names`.

The subclass of `StaticModel` that is created can have other attributes
and methods, just like a regular class. The only restriction is that
**identifier names must be lower case or begin with an underscore**.

Once the class has been defined, **the members are transformed into
instances of the model**.

```pycon
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

```

## Member access methods


If the member name (the attribute name of the member defined on the
model) is known, it can be accessed just like any other attribute.

```pycon
>>> AnimalType.DOG
<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>

```

The entire collection of members can be retrieved with the
`members.all()` method.

```pycon
>>> pp(AnimalType.members.all())
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>,
 <AnimalType.SNAKE: name='Snake', description="Man's slithering companion", domesticated=True, has_legs=False>]
>>> pp([item.walk() for item in AnimalType.members.all()])
['Dog walking...', 'Cat walking...', "Snake can't walk."]

```

Model members may be filtered with the model's `members.filter()`
method.

```pycon
>>> pp(AnimalType.members.filter(has_legs=True))
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>]

```

Providing no criteria to `members.filter()` is the same as calling
`members.all()`.

```pycon
>>> pp(AnimalType.members.filter())
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>,
 <AnimalType.SNAKE: name='Snake', description="Man's slithering companion", domesticated=True, has_legs=False>]

```

The `members.all()` and `members.filter()` methods return an empty
list if no members were found.

```pycon
>>> class NoMembers(StaticModel):
...     _field_names = ('something',)
...
>>> pp(NoMembers.members.all())
[]
>>> pp(NoMembers.members.filter(something='nothing'))
[]
>>>

```

A single model member may be retrieved directly using the model's
`members.get()` method.

```pycon
>>> AnimalType.members.get(name='Dog')
<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>
>>>

```

The `members.get()` method raises `<model>.DoesNotExist` if the query
is unsuccessful and `<model>.MultipleObjectsReturned` if more than one
is returned.

```pycon
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

```


The `members.choices()` method is a shortcut for generating lists of
2-item tuples for use in things like Django field definitions. By
default, it returns all members and uses the first two fields defined on
the model.

```pycon
>>> pp(AnimalType.members.choices())
[('Dog', "Man's best friend"),
 ('Cat', "Man's gracious overlord"),
 ('Snake', "Man's slithering companion")]
>>>

```

If field names are specified, there must be no more than 2.

```pycon
>>> try:
...     AnimalType.members.choices('name', 'description', 'domesticated')
... except ValueError as e:
...     print(e)
Maximum number of specified fields for AnimalType.members.choices() is 2

```

If only a singe field name is provided, or if the model only has one
field, then the same field is used for both items of the tuple.

```pycon
>>> pp(AnimalType.members.choices('name'))
[('Dog', 'Dog'), ('Cat', 'Cat'), ('Snake', 'Snake')]

```

The `members.choices()` method may also be provided with criteria to
limit the members included in the results, much like
`members.filter()`.

```pycon
>>> pp(AnimalType.members.choices(has_legs=True))
[('Dog', "Man's best friend"), ('Cat', "Man's gracious overlord")]
>>> pp(AnimalType.members.choices('name', has_legs=True))
[('Dog', 'Dog'), ('Cat', 'Cat')]

```


### The _member_name field


The name of each member's class attribute on the model and parent
models is available as the `_member_name` field on the member.

```pycon
>>> AnimalType.DOG._member_name
'DOG'

```

The `_member_name` field can be used in member queries if needed.

```pycon
>>> AnimalType.members.get(_member_name='CAT')
<AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>
>>> AnimalType.members.filter(_member_name='DOG')
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>]

```

However, if only a single member is needed, using the built-in
`getattr()` is more concise.

```pycon
>>> getattr(AnimalType, 'SNAKE')
<AnimalType.SNAKE: name='Snake', description="Man's slithering companion", domesticated=True, has_legs=False>

```

## Sub-models


Models can have sub-models. Sub-models are created using normal
sub-class syntax.

```pycon
>>> class WildAnimalType(AnimalType):
...     DEER = 'Deer', 'Likes to hide', False, True
...     ANTELOPE = 'Antelope', 'Likes to run', False, True
...
...     def walk(self):
...         return '{}warily'.format(super().walk())

```

Sub-models inherit the `_field_names` attribute of their parent model.

```pycon
>>> WildAnimalType._field_names
('name', 'description', 'domesticated', 'has_legs')
>>> WildAnimalType.DEER
<WildAnimalType.DEER: name='Deer', description='Likes to hide', domesticated=False, has_legs=True>

```

However, sub-models DO NOT inherit the members of their parent model.

```pycon
>>> WildAnimalType.DOG
Traceback (most recent call last):
    ...
AttributeError: 'WildAnimalType' model does not contain member 'DOG'
>>> pp(WildAnimalType.members.all())
[<WildAnimalType.DEER: name='Deer', description='Likes to hide', domesticated=False, has_legs=True>,
 <WildAnimalType.ANTELOPE: name='Antelope', description='Likes to run', domesticated=False, has_legs=True>]

```

Parent models **gain the members** of their sub-models. Notice that the
`AnimalType` model now contains the members just defined in the
`WildAnimalType` sub-model.

```pycon
>>> pp(AnimalType.members.all())
[<AnimalType.DOG: name='Dog', description="Man's best friend", domesticated=True, has_legs=True>,
 <AnimalType.CAT: name='Cat', description="Man's gracious overlord", domesticated=True, has_legs=True>,
 <AnimalType.SNAKE: name='Snake', description="Man's slithering companion", domesticated=True, has_legs=False>,
 <WildAnimalType.DEER: name='Deer', description='Likes to hide', domesticated=False, has_legs=True>,
 <WildAnimalType.ANTELOPE: name='Antelope', description='Likes to run', domesticated=False, has_legs=True>]

```

The members that the parent has gained are accessed exactly the same
way as the other members, and behave as expected.

```pycon
>>> pp([item.walk() for item in AnimalType.members.all()])
['Dog walking...',
 'Cat walking...',
 "Snake can't walk.",
 'Deer walking...warily',
 'Antelope walking...warily']

```


### Additional fields


Additional field names can be provided by overriding `_field_names`
in sub-models. A good practice is to reference the parent model's
values as demonstrated in the `SmallHousePet` model below.

```pycon
>>> class SmallHousePet(AnimalType):
...     _field_names = AnimalType._field_names + ('facility',)
...
...     FISH = 'Fish', 'Likes to swim', True, True, 'tank'
...     RODENT = 'Rodent', 'Likes to eat', True, True, 'cage'

```

Member queries on the sub-model can use the additional field names.

```pycon
>>> pp(SmallHousePet.members.filter(facility='tank'))
[<SmallHousePet.FISH: name='Fish', description='Likes to swim', domesticated=True, has_legs=True, facility='tank'>]

```

Parent models are not aware of additional fields that have been added
by sub-models, so those additional fields cannot be used in member
queries.

```pycon
>>> try:
...     AnimalType.members.filter(facility='tank')
... except AnimalType.InvalidField as e:
...     print(e)
...
Invalid field 'facility'

```

## Primitive Collections


Model members may be rendered as primitive collections.

The methods `members.all()` and `members.filter()` return a
list with the methods `values()` and `values_list()` defined on it.

The `values()` method returns a list of dictionaries.

```pycon
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

```

The `values_list()` method returns a list of tuples.

```pycon
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

```

Notice that when the `AnimalType` model was used to execute `.values()` or
`.values_list()`, the `facility` field was not included in the
results. This is because the default fields for these methods is
the value of `AnimalType._field_names`, which does not include `facility`.

Specific fields for `.values()` and `.values_list()` may be
provided by passing them as positional parameters to those methods.

```pycon
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

```

Notice that some members have the `facility` field set to None (or null
when converted to JSON). These are placeholders for fields that were
requested, but do not exist on that member.

The `values_list()` method can be passed the `flat=True` parameter
to collapse the values in the result.

```pycon
>>> jsonify(AnimalType.members.all().values_list('facility', flat=True))
[
  "tank",
  "cage"
]

```

Using `flat=True` usually only makes sense when limiting the results
to a single field name.

```pycon
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

```

## Django Model Fields


**StaticModel** provides custom Django model fields in the
`staticmodel.django.models` package:

 - `StaticModelCharField` (sub-class of `django.db.models.CharField`)
 - `StaticModelTextField` (sub-class of `django.db.models.TextField`)
 - `StaticModelIntegerField` (sub-class of `django.db.models.IntegerField`)

StaticModel members are returned, and can be set, as the value of the
fields on a django model object.

All fields take the following keyword arguments in addition to the
arguments taken by their respective parent classes:

 - `static_model`: The StaticModel class associated with this field.
 - `value_field_name`: The StaticModel field name whose value will
   be stored in the database. Defaults to the first field name in
   `static_model._field_names`.
 - `display_field_name`: The StaticModel field name whose value will
   be used as the display value in the `choices` passed to the parent
   field. Defaults to the value of `value_field_name`.

When the model field is instantiated, it validates the values of
`value_field_name` and `display_field_name` against
**every member** of the StaticModel to insure the fields exist and
contain a value appropriate for the value of the field. This ensures
that error-causing inconsistencies are detected early during
development.

## Django Rest Framework Serializer Fields


**StaticModel** provides custom serializer fields in the
`staticmodel.django.rest_framework.serializers` module:

 - `StaticModelCharField` (sub-class of `rest_framework.serializers.CharField`)
 - `StaticModelIntegerField` (sub-class of `rest_framework.serializers.IntegerField`)

All fields take the following keyword arguments in addition to the
arguments taken by their respective parent classes:

 - `static_model`: The StaticModel class associated with this field.
 - `lookup_field_name`: The StaticModel field name that will be used
   to lookup the StaticModel member when deserializing, and the field
   name to retrieve the value from when serializing (unless
   `static_model_expand=True`. See below.). Defaults to the first field
   name in `static_model._field_names`.
 - `static_model_expand`: When set to `True`, return the entire
   StaticModel member as a mapping. Defaults to `False`.

Regardless of the value of `static_model_expand`, if the value passed
during deserialization is a mapping, it will be used to retrieve the
lookup value using `lookup_field_name`.
