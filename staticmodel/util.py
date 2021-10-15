import json


def format_kwargs(kwargs):
    return ', '.join('{}={!r}'.format(k, v) for k, v in kwargs.items())


def jsonify(obj):
    print('\n'.join(line.rstrip() for line in json.dumps(obj, indent=2).splitlines()))
