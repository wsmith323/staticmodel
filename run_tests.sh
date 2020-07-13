#!/usr/bin/env bash
set -e

python setup.py test

pip install 'django>=1.11,<2.0'
./manage.py test
