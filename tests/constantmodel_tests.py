import doctest
import constantmodel


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(constantmodel))
    return tests
