'''
Created on Jul 31, 2017

@author: tommi
'''
from distutils.core import setup, Extension

setup(
    ext_modules=[Extension("handeval", ["handeval.c", "pcg/pcg_basic.c"])],
)