from unittest.case import TestCase
from types import SimpleNamespace

from rest_framework.serializers import ModelSerializer

from django_test_app.models import Integer, String, TestModel
from staticmodel.django.rest_framework.serializers import (
    StaticModelCharField,
    StaticModelIntegerField,
)


class TestModelSerializer(ModelSerializer):
    char = StaticModelCharField(
        static_model=String, static_model_expand=True, required=False, allow_null=True,
        allow_blank=True)
    text = StaticModelCharField(
        static_model=String, required=False, allow_null=True, allow_blank=True)
    integer = StaticModelIntegerField(static_model=Integer, required=False, allow_null=True)

    class Meta:
        model = TestModel
        fields = ['id', 'name', 'char', 'text', 'integer']


class SerializerFieldTest(TestCase):
    def setUp(self):
        TestModel.objects.create(
            id=1,
            name='Test Object 1',
            char=String.VALUE_1,
            text=String.VALUE_1,
            integer=Integer.VALUE_1,
        )
        TestModel.objects.create(
            id=2,
            name='Test Object 2',
        )

    def test_read(self):
        object1 = TestModel.objects.get(id=1)
        object2 = TestModel.objects.get(id=2)

        serializer = TestModelSerializer(object1)
        self.assertDictEqual(serializer.data, {
            'id': 1,
            'name': 'Test Object 1',
            'char': {'code': 'value_1', 'display': 'String Value 1'},
            'text': String.VALUE_1.code,
            'integer': Integer.VALUE_1.value,
        })

        serializer = TestModelSerializer(object2)
        self.assertDictEqual(serializer.data, {
            'id': 2,
            'name': 'Test Object 2',
            'char': None,
            'text': None,
            'integer': None,
        })

    def test_write(self):
        object1 = TestModel.objects.get(id=1)
        object2 = TestModel.objects.get(id=2)

        serializer = TestModelSerializer(object1, data={
            'id': 1,
            'name': 'Test Object 3',
            'char': String.VALUE_2.code,
            'text': {'code': 'value_2', 'display': 'String Value 2'},
            'integer': Integer.VALUE_2.value,
        })
        self.assertTrue(serializer.is_valid())
        validated_obj = SimpleNamespace(**serializer.validated_data)
        self.assertEqual(validated_obj.name, 'Test Object 3')
        self.assertIs(validated_obj.char, String.VALUE_2)
        self.assertIs(validated_obj.text, String.VALUE_2)
        self.assertIs(validated_obj.integer, Integer.VALUE_2)

        serializer.save()
        object1.refresh_from_db()
        self.assertEqual(object1.name, 'Test Object 3')
        self.assertIs(object1.char, String.VALUE_2)
        self.assertIs(object1.text, String.VALUE_2)
        self.assertIs(object1.integer, Integer.VALUE_2)

        serializer = TestModelSerializer(object2, data={
            'id': 2,
            'name': 'Test Object 4',
            'char': None,
            'text': None,
            'integer': None,
        })
        self.assertTrue(serializer.is_valid())
        validated_obj = SimpleNamespace(**serializer.validated_data)
        self.assertEqual(validated_obj.name, 'Test Object 4')
        self.assertIs(validated_obj.char, None)
        self.assertIs(validated_obj.text, None)
        self.assertIs(validated_obj.integer, None)

        serializer.save()
        object2.refresh_from_db()
        self.assertIs(object2.char, None)
        self.assertIs(object2.text, None)
        self.assertIs(object2.integer, None)

        serializer = TestModelSerializer(object2, data={
            'id': 2,
            'name': 'Test Object 5',
            'char': 'bad_char',
            'text': 'bad_text',
            'integer': 99,
        })
        self.assertFalse(serializer.is_valid())
        self.assertDictEqual(serializer.errors, {
            'char': ["Value 'bad_char' is invalid"],
            'integer': ['Value 99 is invalid'],
            'text': ["Value 'bad_text' is invalid"],
        })

    def tearDown(self):
        TestModel.objects.all().delete()
