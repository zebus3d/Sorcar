#cython: language_level=2

import bpy
import cython
from mathutils import Vector

#import numpy as np
cimport numpy as np

#ctypedef np.double_t DTYPE_t
#ctypedef np.float64_t DTYPE_t

# this np.ndarray[np.float64_t, ndim=2] input_points is similar to this: np.float64_t[:,:] input_points

cdef list fracture_voronoi(np.ndarray[np.float64_t, ndim=2] input_points, object obj, int total_chunks, np.npy_bool selection):
#cdef list fracture_voronoi(np.float64_t[:,:] input_points, obj, int total_chunks, np.npy_bool selection):
    cdef list chunks  = []
    cdef str name_facemap = 'inner'
    cdef str edit_mode = 'EDIT'
    cdef str object_mode = 'OBJECT'
    cdef str a_select = 'SELECT'
    cdef str a_deselect = 'DESELECT'
    cdef str chunk_prefix = 'chunk_'
    cdef str str_total_chunks = str(total_chunks)
    cdef int num_paddin = len(str_total_chunks)
    cdef int i = 0
    cdef int p_begin = 0
    cdef np.ndarray[np.float64_t, ndim=1] from_point
    #cdef np.float64_t[:] from_point
    cdef np.ndarray[np.float64_t, ndim=1] to_point
    #cdef np.float64_t[:] to_point
    cdef np.npy_bool use_fill = True
    cdef np.npy_bool clear_outer = False
    cdef np.npy_bool clear_inner = True

    win = bpy.context.window_manager
    win.progress_begin(p_begin, total_chunks)

    if selection:
        # set facemap inner:
        bpy.context.active_object.face_maps.active_index = bpy.context.active_object.face_maps[name_facemap].index

    #print(type(input_points))
    for from_point in input_points:
        bpy.context.view_layer.objects.active = obj
        new_obj = obj.copy()
        new_obj.name = chunk_prefix + str(i + 1).zfill(num_paddin)
        new_obj.data = obj.data.copy()
        bpy.context.collection.objects.link(new_obj)
        chunks.append(new_obj)
        bpy.context.view_layer.objects.active = new_obj

        if not bpy.context.active_object.select_get():
            bpy.context.active_object.select_set(True)

        bpy.ops.object.mode_set(mode=edit_mode)

        for to_point in input_points:

            from_point_v3 = Vector((from_point[0], from_point[1], from_point[2]))
            to_point_v3 = Vector((to_point[0], to_point[1], to_point[2]))

            if from_point_v3 != to_point_v3:
                # Calculate the Perpendicular Bisector Plane
                voro_center = Vector(((to_point_v3 + from_point_v3) * 0.5))
                aim = Vector((from_point_v3 - to_point_v3))
                aim.normalize()

                # Bullet Shatter
                bpy.ops.mesh.select_all(action=a_select)
                bpy.ops.mesh.bisect(
                    plane_co=voro_center,
                    plane_no=aim,
                    use_fill=True,
                    clear_outer=False,
                    clear_inner=True
                )
                if selection:
                    # assing facemap inner:
                    bpy.ops.object.face_map_assign()

        if selection:
            # select facemap inner:
            bpy.ops.object.face_map_select()
        else:
            bpy.ops.mesh.select_all(action=a_deselect)

        if bpy.context.active_object.mode != object_mode:
            bpy.ops.object.mode_set(mode=object_mode)

        bpy.ops.object.select_all(action=a_deselect)

        win.progress_update(i)
        i += 1

    win.progress_end()
    return chunks

def call_fracture_voronoi(input_points, obj, total_chunks, selection):
    chunks = fracture_voronoi(input_points, obj, total_chunks, selection)
    return chunks