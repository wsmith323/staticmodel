"""
******************
Django integration
******************

**Static Model** provides two custom Django model fields in the
``staticmodel.django.fields`` module:

 * ``StaticModelCharField`` (sub-class of ``django.db.models.CharField``)
 * ``StaticModelIntegerField`` (sub-class of ``django.db.models.IntegerField``)

Static model members are returned, and can be set, as the value of the
fields on a django model object.

Both fields take the following keyword arguments in addition to the
arguments taken by their respective sub-classes:

 * ``static_model``: The static model class associated with this field.
 * ``value_field_name``: The static model field name whose value will
   be stored in the database. Defaults to the first field name in
   ``static_model._field_names``.
 * ``display_field_name``: The static model field name whose value will
   be used as the display value in the ``choices`` passed to the parent
   field. Defaults to the value of ``value_field_name``.

When the model field is instantiated, it validates the values of
``value_field_name`` and ``display_field_name`` against
**every member** of the static model to insure the fields exist and
contain a value appropriate for the value of the field. This ensures
that error-causing inconsistencies are detected early during
development.
"""
