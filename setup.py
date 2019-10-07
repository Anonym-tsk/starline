from __future__ import print_function
from setuptools import setup
import codecs
import os
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    return codecs.open(os.path.join(here, *parts), 'r').read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


long_description = read('README.rst')


setup(
    name='starline',

    version=find_version('starline', '__init__.py'),
    description='Unofficial python library for StarLine API',
    long_description=long_description,
    url='https://github.com/Anonym-tsk/starline/',
    license='Apache License 2.0',

    keywords='starline car security',

    author='Nikolay Vasilchuk',
    author_email='anonym.tsk@gmail.com',

    install_requires=[
        'aiohttp>=3.6.1'
    ],

    packages=['starline'],
    include_package_data=True,
    platforms='any',
    python_requires='>=3.5',

    classifiers=[
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
    ]
)
