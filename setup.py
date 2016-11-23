import os

from setuptools import setup, find_packages

__version__ = "0.1.0"


def file_read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as flo:
        return flo.read()


setup(
    name="staticmodel",
    version=__version__,
    packages=find_packages(),
    install_requires=['six'],
    author="Warren A. Smith",
    author_email="warren@wandrsmith.net",
    description="Static Models.",
    long_description=file_read("README.md"),
    license="MIT",
    keywords="static constant model enum",
    url="https://github.com/wsmith323/staticmodel",
    test_suite="tests",
)
