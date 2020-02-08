from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

# For compile this:
# python3 setup.py build_ext --inplace

# Or if you dont like create this setup.py:
# you can compile with:
# sudo pip3 install easycython
# easycython voronoi.pyx

setup(
    name = 'voronoi',
    ext_modules = cythonize("voronoi.pyx", annotate=True),
    include_dirs=[numpy.get_include()]
)
