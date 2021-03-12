from unittest.case import TestCase

from django.core.exceptions import ValidationError

from django_test_app.models import Integer, String, TestModel


class CharFieldTest(TestCase):
    def setUp(self):
        TestModel.objects.create(name='Test Object 1', char=String.VALUE_1)
        TestModel.objects.create(name='Test Object 2', char=String.VALUE_2.code)
        TestModel.objects.create(name='Test Null Object')

    def test_read(self):
        object1 = TestModel.objects.get(char=String.VALUE_1)
        object2 = TestModel.objects.get(char=String.VALUE_2.code)
        object3 = TestModel.objects.get(char__isnull=True)

        self.assertIs(object1.char, String.VALUE_1)
        self.assertIs(object2.char, String.VALUE_2)
        self.assertIsNone(object3.char)

    def test_write_model(self):
        object1 = TestModel.objects.get(char=String.VALUE_1)
        object2 = TestModel.objects.get(char=String.VALUE_2)

        object1.char = String.VALUE_3
        object1.save()
        object1.refresh_from_db()
        self.assertIs(object1.char, String.VALUE_3)

        object2.char = String.VALUE_1
        object2.save()
        object2.refresh_from_db()
        self.assertIs(object2.char, String.VALUE_1)

    def test_write_id(self):
        object1 = TestModel.objects.get(char=String.VALUE_1)
        object2 = TestModel.objects.get(char=String.VALUE_2)

        object1.char = String.VALUE_3.code
        object1.save()
        object1.refresh_from_db()
        self.assertIs(object1.char, String.VALUE_3)

        object2.char = String.VALUE_1.code
        object2.save()
        object2.refresh_from_db()
        self.assertIs(object2.char, String.VALUE_1)

    def test_clean(self):
        object1 = TestModel.objects.get(char=String.VALUE_1)

        object1.char = String.VALUE_2
        object1.full_clean()

        object1.char = String.VALUE_3.code
        object1.full_clean()

        object1.char = 'bad'
        self.assertRaises(ValidationError, object1.full_clean)

        object1.char = 1
        self.assertRaises(ValidationError, object1.full_clean)

    def tearDown(self):
        TestModel.objects.all().delete()


class TextFieldTest(TestCase):
    def setUp(self):
        TestModel.objects.create(name='Test Object 1', text=String.VALUE_1)
        TestModel.objects.create(name='Test Object 2', text=String.VALUE_2.code)
        TestModel.objects.create(name='Test Null Object')

    def test_read(self):
        object1 = TestModel.objects.get(text=String.VALUE_1)
        object2 = TestModel.objects.get(text=String.VALUE_2.code)
        object3 = TestModel.objects.get(text__isnull=True)

        self.assertIs(object1.text, String.VALUE_1)
        self.assertIs(object2.text, String.VALUE_2)
        self.assertIsNone(object3.text)

    def test_write_model(self):
        object1 = TestModel.objects.get(text=String.VALUE_1)
        object2 = TestModel.objects.get(text=String.VALUE_2)

        object1.text = String.VALUE_3
        object1.save()
        object1.refresh_from_db()
        self.assertIs(object1.text, String.VALUE_3)

        object2.text = String.VALUE_1
        object2.save()
        object2.refresh_from_db()
        self.assertIs(object2.text, String.VALUE_1)

    def test_write_id(self):
        object1 = TestModel.objects.get(text=String.VALUE_1)
        object2 = TestModel.objects.get(text=String.VALUE_2)

        object1.text = String.VALUE_3.code
        object1.save()
        object1.refresh_from_db()
        self.assertIs(object1.text, String.VALUE_3)

        object2.text = String.VALUE_1.code
        object2.save()
        object2.refresh_from_db()
        self.assertIs(object2.text, String.VALUE_1)

    def test_clean(self):
        object1 = TestModel.objects.get(text=String.VALUE_1)

        object1.text = String.VALUE_2
        object1.full_clean()

        object1.text = String.VALUE_3.code
        object1.full_clean()

        object1.text = 'bad'
        self.assertRaises(ValidationError, object1.full_clean)

        object1.text = 1
        self.assertRaises(ValidationError, object1.full_clean)

    def tearDown(self):
        TestModel.objects.all().delete()


class IntegerFieldTest(TestCase):
    def setUp(self):
        TestModel.objects.create(name='Test Object 1', integer=Integer.VALUE_1)
        TestModel.objects.create(name='Test Object 2', integer=Integer.VALUE_2.value)
        TestModel.objects.create(name='Test Null Object')

    def test_read(self):
        object1 = TestModel.objects.get(integer=Integer.VALUE_1)
        object2 = TestModel.objects.get(integer=Integer.VALUE_2.value)
        object3 = TestModel.objects.get(integer__isnull=True)
        
        self.assertIs(object1.integer, Integer.VALUE_1)
        self.assertIs(object2.integer, Integer.VALUE_2)
        self.assertIsNone(object3.integer)

    def test_write_model(self):
        object1 = TestModel.objects.get(integer=Integer.VALUE_1)
        object2 = TestModel.objects.get(integer=Integer.VALUE_2)

        object1.integer = Integer.VALUE_3
        object1.save()
        object1.refresh_from_db()
        self.assertIs(object1.integer, Integer.VALUE_3)

        object2.integer = Integer.VALUE_1
        object2.save()
        object2.refresh_from_db()
        self.assertIs(object2.integer, Integer.VALUE_1)

    def test_write_id(self):
        object1 = TestModel.objects.get(integer=Integer.VALUE_1)
        object2 = TestModel.objects.get(integer=Integer.VALUE_2)

        object1.integer = Integer.VALUE_3.value
        object1.save()
        object1.refresh_from_db()
        self.assertIs(object1.integer, Integer.VALUE_3)

        object2.integer = Integer.VALUE_1.value
        object2.save()
        object2.refresh_from_db()
        self.assertIs(object2.integer, Integer.VALUE_1)

    def test_clean(self):
        object1 = TestModel.objects.get(integer=Integer.VALUE_1)

        object1.integer = Integer.VALUE_2
        object1.full_clean()
        self.assertIs(object1.integer, Integer.VALUE_2)

        object1.integer = Integer.VALUE_3.value
        object1.full_clean()
        self.assertIs(object1.integer, Integer.VALUE_3)

        object1.integer = 'bad'
        self.assertRaises(ValidationError, object1.full_clean)

        object1.integer = 0
        self.assertRaises(ValidationError, object1.full_clean)

    def tearDown(self):
        TestModel.objects.all().delete()
