from django.db import models

from staticmodel import StaticModel
from staticmodel.django.models import (
    StaticModelCharField, StaticModelIntegerField,
    StaticModelTextField,
)


class String(StaticModel):
    _field_names = 'code', 'display'
    VALUE_1 = 'value_1', 'String Value 1'
    VALUE_2 = 'value_2', 'String Value 2'
    VALUE_3 = 'value_3', 'String Value 3'


class Integer(StaticModel):
    _field_names = 'value', 'display'
    VALUE_1 = 1, 'Int Value 1'
    VALUE_2 = 2, 'Int Value 2'
    VALUE_3 = 3, 'Int Value 3'


class TestModel(models.Model):
    name = models.CharField(max_length=20, unique=True)
    char = StaticModelCharField(static_model=String, value_field_name='code',
                                display_field_name='display', max_length=10, null=True, blank=True)
    text = StaticModelTextField(static_model=String, value_field_name='code',
                                display_field_name='display', null=True, blank=True)
    integer = StaticModelIntegerField(static_model=Integer, value_field_name='value',
                                      display_field_name='display', null=True, blank=True)
