#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='konsent',
      version='0.2',
      packages=find_packages(),
      include_package_data=True,
      entry_points={
          'console_scripts': [
              'konsent = konsent.__main__:main',
          ],
      }
 )
