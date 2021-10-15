import os

from setuptools import setup, find_packages


def file_read(filename):
    filepath = os.path.join(os.path.dirname(__file__), filename)
    with open(filepath) as flo:
        return flo.read()


__version__ = file_read(os.path.join('staticmodel', 'VERSION.txt')).strip()


setup(
    name="staticmodel",
    version=__version__,
    packages=find_packages(exclude=['tests', 'docs']),
    include_package_data=True,
    author="Warren A. Smith",
    author_email="warren@wandrsmith.net",
    description="Static Models.",
    long_description=file_read("README.rst"),
    long_description_content_type='text/x-rst',
    license="MIT",
    keywords="static constant model enum django",
    url="https://github.com/wsmith323/staticmodel",
    classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 4 - Beta',

            # Indicate who your project is intended for
            'Intended Audience :: Developers',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here. In particular, ensure
            # that you indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
    ],
)
