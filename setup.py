#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(name='daemon-manager',
      version='0.1.4.c',
      description='Linux Daemon Manager',
      author='Du Jiong/Lodevil',
      author_email='londevil@gmail.com',
      url='https://github.com/lodevil/daemon-manager/',
      license='BSD',
      py_modules=['dm'],
      entry_points={
            'console_scripts': [
                'dm=dm:main',
            ],
        },
     )
