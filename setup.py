'''
Created on Jul 31, 2017

@author: tommi
'''
from distutils.core import setup
from Cython.Build import cythonize

setup(
    name = 'Hand evaluator',
    ext_modules = cythonize("handeval.pyx")
)