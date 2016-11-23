"""
partialmethod for python2

Copied from https://gist.github.com/carymrobbins/8940382
"""
from functools import partial

import six

if six.PY2:
    class partialmethod(partial):
        def __get__(self, instance, owner):
            if instance is None:
                return self
            return partial(self.func, instance,
                           *(self.args or ()), **(self.keywords or {}))

else:
    from functools import partialmethod
