# cython: language_level=3
import bpy
import cython
from mathutils import Vector
import numpy as np
cimport numpy as np

#from cython.parallel cimport prange

def fracture_voronoi(np.ndarray input_points, list objects):
    win = bpy.context.window_manager
    win.progress_begin(0, len(objects))

    cdef int total_points = len(input_points)

    cdef int i = 0
    cdef int p = 0

    for from_point in input_points:
        win.progress_update(p)

        bpy.context.view_layer.objects.active = objects[i]

        if not bpy.context.active_object.select_get():
            bpy.context.active_object.select_set(True)

        #bpy.context.active_object.name = "chunk_" + str(i).zfill(len(str(total_points)))
        i += 1

        bpy.ops.object.mode_set(mode='EDIT')

        for to_point in input_points:

            from_point = Vector((from_point[0], from_point[1], from_point[2]))
            to_point = Vector((to_point[0], to_point[1], to_point[2]))

            if from_point != to_point:
                # Calculate the Perpendicular Bisector Plane

                voro_center = Vector(( (to_point + from_point) * 0.5 ))
                aim = Vector(( from_point - to_point ))
                aim.normalize()

                # Bullet Shatter
                bpy.ops.mesh.select_all(action='SELECT')
                bpy.ops.mesh.bisect(
                    plane_co=voro_center,
                    plane_no=aim,
                    use_fill=True,
                    clear_outer=False,
                    clear_inner=True
                )
        p += 1

        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

    win.progress_end()