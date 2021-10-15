from unittest import TestCase

from staticmodel import StaticModel
from types import SimpleNamespace


class OBJECT(StaticModel):
    _field_names = 'id', 'code', 'name'

    WAR = 1, 'war', 'War'
    PEACE = 2, 'peace', 'Peace'
    HATE = 3, 'hate', 'Hate'
    LOVE = 4, 'love', 'Love'

    _label = None

    def label(self, value):
        return '{}: {}'.format(self._label, value) if self._label else value

    @property
    def description(self):
        return '{}.{}, id={}, code={!r}: {}'.format(
            self.__class__.__name__, self._member_name, self.id,
            self.code, self.label(self.name))


class PLACE(OBJECT):
    _field_names = OBJECT._field_names + ('gis_location', 'continent', 'known_for', )
    _index_field_names = _field_names

    JERUSALEM = 5, 'jerusalem', 'Jerusalem', (31.77, 35.22), 'Asia', OBJECT.WAR
    GENEVA = 6, 'geneva', 'Geneva', (46.2, 6.15), 'Europe', OBJECT.PEACE
    AUSCHWITZ = 7, 'auschwitz', 'Auschwitz', (50.04, 19.18), 'Europe', OBJECT.HATE
    PARIS = 8, 'paris', 'Paris', (48.85, 2.35), 'Europe', OBJECT.LOVE

    _label = 'Where'

    @property
    def description(self):
        return '; '.join([
            super().description,
            'Location: {}, {}'.format(*self.gis_location),
            self.continent,
        ])


class THING(OBJECT):
    _field_names = OBJECT._field_names + ('is_organic',)

    METAL = 9, 'metal', 'Metal', False
    PLANT = 10, 'plant', 'Plant', True
    ROCK = 11, 'rock', 'Rock', False
    ANIMAL = 12, 'animal', 'Animal', True

    _label = 'What'

    @property
    def description(self):
        return '; '.join([
            super().description,
            'Organic' if self.is_organic else 'Inorganic',
        ])


class PERSON(OBJECT):
    _field_names = OBJECT._field_names + ('_parent1', '_parent2')

    PERSON_1 = 13, 'person_1', 'Person 1', None, None
    PERSON_2 = 14, 'person_2', 'Person 2', 'person_1', None
    PERSON_3 = 15, 'person_3', 'Person 3', None, 'person_2'
    PERSON_4 = 16, 'person_4', 'Person 4', 'person_1', 'person_3'
    PERSON_5 = 17, 'person_5', 'Person 5', 'person_1', 'person_2'
    PERSON_6 = 18, 'person_6', 'Person 6', 'person_3', 'person_4'
    PERSON_7 = 19, 'person_7', 'Person 7', 'person_5', 'person_6'
    PERSON_8 = 20, 'person_8', 'Person 8', 'person_5', 'person_6'

    _label = 'Who'

    @property
    def description(self):
        parents = self.parents
        children = self.children
        return '; '.join(chunk for chunk in (
            super().description,
            'Parent(s): {}'.format(', '.join(
                parent.name for parent in parents)) if parents else None,
            'Children: {}'.format(', '.join(
                child.name for child in self.children)) if children else None,
        ) if chunk)

    parent1 = property(
        lambda self: self.__class__.members.get(code=self._parent1, _return_none=True))
    parent2 = property(
        lambda self: self.__class__.members.get(code=self._parent2, _return_none=True))

    @property
    def parents(self):
        return list(person for person in (self.parent1, self.parent2) if person)

    @property
    def children(self):
        return list(person for person in self.__class__.members.all() if
                    person is not self and self in person.parents)


class TYPES(OBJECT):
    _field_names = OBJECT._field_names + ("type",)
    TYPE = 21, "type", "Type", type
    CLASS = 22, "class", "Class", OBJECT
    FUNCTION = 23, "function", "Function", len
    METHOD = 24, "method", "Method", OBJECT.members.filter


class MUTABLE(OBJECT):
    _field_names = OBJECT._field_names + ("obj",)
    LIST = 25, "list", "List", ['a', 'b', 'c']
    DICT = 26, "class", "Dict", {item: item for item in LIST[3]}
    NAMESPACE = 27, "namespace", "Namespace", SimpleNamespace(**DICT[3])


class StaticModelTests(TestCase):
    maxDiff = None
    # TODO: Increase test coverage

    def test_get(self):
        result = PLACE.members.get(continent='Asia', known_for=OBJECT.WAR)
        self.assertIs(result, PLACE.JERUSALEM)

    def test_get_non_existent(self):
        self.assertRaises(PLACE.DoesNotExist, PLACE.members.get, continent='Australia')

    def test_get_multiples(self):
        self.assertRaises(PLACE.MultipleObjectsReturned, PLACE.members.get, continent='Europe')

    def test_type_values(self):
        result = TYPES.members.get(type=OBJECT)
        self.assertIs(result, TYPES.CLASS)
        self.assertIs(result.type, OBJECT)

        result = result.type.members.get(code="function")
        self.assertIs(result, TYPES.FUNCTION)
        self.assertIs(result.type, len)

    def test_mutable_values(self):
        result = MUTABLE.members.get(obj=['a', 'b', 'c'])
        self.assertIs(result, MUTABLE.LIST)

    def test_filter(self):
        results = list(
            obj.name for obj in THING.members.filter(is_organic=True))
        self.assertEqual(results, [
            'Plant',
            'Animal',
        ])

    def test_values(self):
        places_east_of_geneva = [place for place in PLACE.members.all().values(
            'name', 'gis_location')
            if place['gis_location'][1] > PLACE.GENEVA.gis_location[1]]
        self.assertEqual(places_east_of_geneva, [{
            'name': 'Jerusalem',
            'gis_location': (31.77, 35.22)
        }, {
            'name': 'Auschwitz',
            'gis_location': (50.04, 19.18)
        }])

    def test_values_list(self):
        descriptions = OBJECT.members.all().values_list('description', flat=True)
        self.assertEqual(descriptions, [
            "OBJECT.WAR, id=1, code='war': War",
            "OBJECT.PEACE, id=2, code='peace': Peace",
            "OBJECT.HATE, id=3, code='hate': Hate",
            "OBJECT.LOVE, id=4, code='love': Love",
            "PLACE.JERUSALEM, id=5, code='jerusalem': Where: Jerusalem;"
            " Location: 31.77, 35.22; Asia",
            "PLACE.GENEVA, id=6, code='geneva': Where: Geneva;"
            " Location: 46.2, 6.15; Europe",
            "PLACE.AUSCHWITZ, id=7, code='auschwitz': Where: Auschwitz;"
            " Location: 50.04, 19.18; Europe",
            "PLACE.PARIS, id=8, code='paris': Where: Paris;"
            " Location: 48.85, 2.35; Europe",
            "THING.METAL, id=9, code='metal': What: Metal; Inorganic",
            "THING.PLANT, id=10, code='plant': What: Plant; Organic",
            "THING.ROCK, id=11, code='rock': What: Rock; Inorganic",
            "THING.ANIMAL, id=12, code='animal': What: Animal; Organic",
            "PERSON.PERSON_1, id=13, code='person_1': Who: Person 1;"
            " Children: Person 2, Person 4, Person 5",
            "PERSON.PERSON_2, id=14, code='person_2': Who: Person 2;"
            " Parent(s): Person 1; Children: Person 3, Person 5",
            "PERSON.PERSON_3, id=15, code='person_3': Who: Person 3;"
            " Parent(s): Person 2; Children: Person 4, Person 6",
            "PERSON.PERSON_4, id=16, code='person_4': Who: Person 4;"
            " Parent(s): Person 1, Person 3; Children: Person 6",
            "PERSON.PERSON_5, id=17, code='person_5': Who: Person 5;"
            " Parent(s): Person 1, Person 2;"
            " Children: Person 7, Person 8",
            "PERSON.PERSON_6, id=18, code='person_6': Who: Person 6;"
            " Parent(s): Person 3, Person 4;"
            " Children: Person 7, Person 8",
            "PERSON.PERSON_7, id=19, code='person_7': Who: Person 7;"
            " Parent(s): Person 5, Person 6",
            "PERSON.PERSON_8, id=20, code='person_8': Who: Person 8;"
            " Parent(s): Person 5, Person 6",
            "TYPES.TYPE, id=21, code='type': Type",
            "TYPES.CLASS, id=22, code='class': Class",
            "TYPES.FUNCTION, id=23, code='function': Function",
            "TYPES.METHOD, id=24, code='method': Method",
            "MUTABLE.LIST, id=25, code='list': List",
            "MUTABLE.DICT, id=26, code='class': Dict",
            "MUTABLE.NAMESPACE, id=27, code='namespace': Namespace",
        ])
