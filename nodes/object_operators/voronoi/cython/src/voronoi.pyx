#cython: language_level=2

import bpy
import cython
from mathutils import Vector

import numpy as np
cimport numpy as np

#ctypedef np.double_t DTYPE_t
#ctypedef np.float64_t DTYPE_t

cdef void fracture_voronoi(np.ndarray[np.float64_t, ndim=2] input_points, list objects, str selection):
    win = bpy.context.window_manager
    win.progress_begin(0, len(objects))

    cdef int total_points = len(input_points)
    cdef int i = 0

    for from_point in input_points:
        win.progress_update(i)

        bpy.context.view_layer.objects.active = objects[i]

        if not bpy.context.active_object.select_get():
            bpy.context.active_object.select_set(True)

        #bpy.context.active_object.name = "chunk_" + str(i).zfill(len(str(total_points)))

        if bpy.context.active_object.mode != 'EDIT':
            bpy.ops.object.mode_set(mode='EDIT')

        if selection == "True":
            # set facemap inner:
            bpy.context.active_object.face_maps.active_index = bpy.context.active_object.face_maps['inner'].index

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
                if selection == "True":
                    # assing facemap inner:
                    bpy.ops.object.face_map_assign()

        if selection == "True":
            # select facemap inner:
            bpy.ops.object.face_map_select()
        else:
            bpy.ops.mesh.select_all(action='DESELECT')

        i += 1

        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        bpy.ops.object.select_all(action='DESELECT')

    win.progress_end()

def call_fracture_voronoi(input_points, objects, selection):
    fracture_voronoi(input_points, objects, selection)