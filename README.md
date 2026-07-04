# StaticModel

**StaticModel** provides a framework for modeling collections of complex
constants in Python.

Use it when specific values in a small, static collection are part of your
application behavior and should live in code instead of a database.

Read the full documentation:
https://staticmodel.readthedocs.org/en/latest.

## Quick Example

```pycon
>>> from staticmodel import StaticModel
>>>
>>>
>>> class AnimalType(StaticModel):
...     _field_names = 'name', 'description', 'has_legs'
...
...     DOG = 'Dog', "Man's best friend", True
...     SNAKE = 'Snake', "Man's slithering companion", False
...
...     def walk(self):
...         if self.has_legs:
...             return '{} walking...'.format(self.name)
...         return "{} can't walk.".format(self.name)
...
>>> AnimalType.DOG.walk()
'Dog walking...'
>>> AnimalType.members.get(name='Snake')
<AnimalType.SNAKE: name='Snake', description="Man's slithering companion", has_legs=False>
```

## Documentation

- [User Guide](docs/user-guide.md)
    - [StaticModel classes](docs/user-guide.md#staticmodel-classes)
    - [Member access methods](docs/user-guide.md#member-access-methods)
    - [Sub-models](docs/user-guide.md#sub-models)
    - [Primitive collections](docs/user-guide.md#primitive-collections)
    - [Django model fields](docs/user-guide.md#django-model-fields)
    - [Django REST Framework serializer fields](docs/user-guide.md#django-rest-framework-serializer-fields)
- [Why StaticModel?](docs/rationale.md)
