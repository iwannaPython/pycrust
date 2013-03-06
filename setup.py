#!/usr/bin/env python

try:
    from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
    from distutils.command.build_py import build_py

from distutils.core import setup

setup(
#    use_2to3        = True,
    cmdclass        = {'build_py': build_py},
    name            = "pycrust",
    version         = "1.0",
    description     = "A collection of add-ons for CherryPy",
    author          = "Michael Stella",
    author_email    = "pycrust@thismetalsky.org",
    license         = "BSD",
    packages        = ['pycrust'],
)

