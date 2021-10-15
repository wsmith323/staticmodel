Static Model release notes
===========================

1.0.0
=====
IMPORTANT: This version is not backwards compatible with code using 0.x.
           Attempts have been made below to specify potential breaking changes,
           but there may be others. You have been warned.
* All support for Python 2 has been removed.
* The django.fields module has been removed. Use django.models.fields instead.
* The members.filter() method now returns all members when called without
  criteria.
* Placeholders with a value of None are now inserted in results of
  members.values() and members.values_list() when specified fields do not exist
  on a member in the results.
* Django Rest Framework serializer fields now require DRF 3.x API.
* Django Rest Framework serializer fields can now serialize the entire static
  model member, and handle the corresponding mapping in a representation.
* A members.choices() method has been added as a shortcut for generating 2-item
  tuples from static model members.
* Documentation has been updated.

0.6.1
=====
* Add tests for Django Rest Framework serializer fields.
* Fix bugs in Django Rest Framework serializer fields.
* Add DRF version clarification to serializer module docstring.

0.6.0
=====
* Add support for model validation to django model fields.
* Move canonical location of Django model fields to staticmodel.django.models.
* Add Django Rest Framework serializer fields.
* Minor fixes to Django model docstring.

0.5.0
=====
* Remove misguided calling of callables during member indexing.
* Correct and simplify index key generation.
* Enable ignored tests.
* Increase test coverage.

0.4.1
=====
* Refactor test execution.

0.4.0
=====
 * Add new django field StaticModelTextField.
 * Add tests for django integration.
 * Fix bugs in django integration.
 * Fix minor bug in .members.get() error message.

0.3.3
=====
 * Fix pip install bug
 * Fix cross-platform install bug

0.3.2
=====
 * Minor refactoring and bug fixes
 * Documentation improvement

0.3.1
=====
 * Fix release notes.

0.3.0
=====
 * Add support for South migrations.

0.2.0
=====
 * BREAKING CHANGE: Move the values() and values_list() methods into
   the class of the object returned by all() and filter().


0.1.7
=====
 * Make version available from package.

0.1.6
=====
 * Fix bug in django field. Make .get_FIELD_display() work properly.

0.1.5
=====
 * Refactoring.
 * Bug fixes.

0.1.4
=====
 * Refactoring.
 * Bug fixes.

0.1.3
=====
 * Refactoring.
 * Bug fixes.

0.1.2
=====
 * Refactoring.
 * Bug fixes.

0.1.0
=====
 * Initial release.

