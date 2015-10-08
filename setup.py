import os

from setuptools import setup, find_packages

__version__ = "0.1.0"


def file_read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as flo:
        return flo.read()


setup(
    name="constantmodel",
    version=__version__,
    packages=find_packages(),
    install_requires=[],
    author="Warren A. Smith",
    author_email="warren@wandrsmith.net",
    description="Constant classes with model features.",
    long_description=file_read("README.md"),
    license="MIT",
    keywords="constant model enum",
    url="https://github.com/wsmith323/constantmodel",
    test_suite="tests",
)
