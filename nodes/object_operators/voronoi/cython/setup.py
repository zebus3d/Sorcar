from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

# For compile this:
# python3 setup.py build_ext --inplace

setup(
    name = 'voronoi',
    ext_modules = cythonize("voronoi.pyx", annotate=True),
    include_dirs=[numpy.get_include()]
)
