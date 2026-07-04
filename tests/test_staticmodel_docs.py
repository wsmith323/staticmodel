import doctest
from pathlib import Path


README_PATH = Path(__file__).resolve().parent.parent / 'README.md'


def load_tests(loader, tests, ignore):
    tests.addTests(doctest.DocFileSuite(str(README_PATH), module_relative=False))
    return tests
