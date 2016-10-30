import doctest
import staticmodel


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocTestSuite(staticmodel))
    return tests
