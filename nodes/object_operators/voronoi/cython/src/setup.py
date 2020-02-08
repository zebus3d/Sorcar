from distutils.core import setup, Extension
from Cython.Build import cythonize
import numpy

# For compile this:
# cd nodes/object_operators/voronoi/cython/src/
# python3 setup.py build_ext --inplace
# mv -i voronoi.cpython-37m-x86_64-linux-gnu.so ../voronoi.cpython-37m-x86_64-linux-gnu.so

# Or if you dont like create this setup.py:
# you can compile with:
# sudo pip3 install easycython
# easycython voronoi.pyx
# mv -i voronoi.cpython-37m-x86_64-linux-gnu.so ../voronoi.cpython-37m-x86_64-linux-gnu.so

setup(
    name = 'voronoi',
    ext_modules = cythonize("voronoi.pyx", annotate=True),
    include_dirs=[numpy.get_include()]
)
