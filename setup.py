#!/usr/bin/env python

from distutils.core import setup

with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(name='kolasimagestorage',
      version='0.0.2',
      description='Abstraction layer for image storage',
      author='sergem',
      author_email='sbmatyunin@gmail.com',
      url='https://serge-m.github.io',
      install_requires=required,
      packages=['kolasimagestorage'],
     )


