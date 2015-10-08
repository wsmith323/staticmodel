from decimal import Decimal
from unittest import TestCase

from constantmodel import ATTR_NAME, ConstantModel


class ConstantModelTests(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.constant_name = 'TESTNAME'
        cls.non_iterable_raw_value = Decimal('1234.56')
        cls.iterable_raw_value = ('testcode', 'Test Description')
        cls.attr_names = ('code', 'description')
        cls.instance1 = ConstantModel(raw_value=cls.non_iterable_raw_value)
        cls.instance2 = ConstantModel(
            raw_value=cls.non_iterable_raw_value, constant_name=cls.constant_name)
        cls.instance3 = ConstantModel(
            raw_value=cls.non_iterable_raw_value, attr_names=cls.attr_names)
        cls.instance4 = ConstantModel(raw_value=cls.iterable_raw_value)
        cls.instance5 = ConstantModel(
            raw_value=cls.iterable_raw_value, attr_names=cls.attr_names)

    def test_init(self):
        obj = self.instance1
        self.assertIs(self.non_iterable_raw_value, rv(obj))
        self.assertIsNone(cn(obj))
        for attr_name in self.attr_names:
            self.assertRaises(AttributeError, getattr, obj, attr_name)

        obj = self.instance2
        self.assertIs(self.non_iterable_raw_value, rv(obj))
        self.assertIs(self.constant_name, cn(obj))
        for attr_name in self.attr_names:
            self.assertRaises(AttributeError, getattr, obj, attr_name)

        obj = self.instance3
        self.assertIs(self.non_iterable_raw_value, rv(obj))
        self.assertIsNone(cn(obj))
        for attr_name in self.attr_names:
            self.assertRaises(AttributeError, getattr, obj, attr_name)

        obj = self.instance4
        self.assertIs(self.iterable_raw_value, rv(obj))
        self.assertIsNone(cn(obj))
        for attr_name in self.attr_names:
            self.assertRaises(AttributeError, getattr, obj, attr_name)

        obj = self.instance5
        self.assertIs(self.iterable_raw_value, rv(obj))
        self.assertIsNone(cn(obj))
        for index, attr_name in enumerate(self.attr_names):
            attr_value = self.iterable_raw_value[index]
            self.assertEqual(attr_value, getattr(obj, attr_name))


def cn(obj):
    return getattr(obj, ATTR_NAME.INSTANCE_VAR.CONSTANT_NAME)


def rv(obj):
    return getattr(obj, ATTR_NAME.INSTANCE_VAR.RAW_VALUE)
