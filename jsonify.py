from __future__ import print_function, unicode_literals

import json


def jsonify(obj):
    print('\n'.join(line.rstrip() for line in json.dumps(obj, indent=2).splitlines()))
