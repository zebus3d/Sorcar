import bpy
import numpy as np
import mathutils
import platform
import os, stat
from subprocess import run, PIPE
from .voronoi.cython import voronoi

from bpy.props import PointerProperty, StringProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_operator import ScObjectOperatorNode
from ...helper import remove_object, print_log

"""
This is the last implementation of fracture voronoi with qhull lib and Brute Force
"""

mute_node = False

architecture = platform.architecture()[0]
if architecture != '64bit':
    print("Invalid architecture, only support 64 bits systems!")
    mute_node = True


class ScVoronoiFractureQhull(Node, ScObjectOperatorNode):
    bl_idname = "ScVoronoiFractureQhull"
    bl_label = "Voronoi Fracture Qhull"

    in_obj: PointerProperty(type=bpy.types.Object, update=ScNode.update_value)
    prop_obj_array: StringProperty(default="[]")
    in_ifs: BoolProperty(default=False, description="Select the inner faces", update=ScNode.update_value)
    in_bf: BoolProperty(default=False, description="The brute force method is slower but works better (especially with low numbers of points)", update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketObject", "Center Points").init("in_obj", True)
        self.outputs.new("ScNodeSocketArray", "Chunks")
        self.inputs.new("ScNodeSocketBool", "Inner selection").init("in_ifs", True)
        self.inputs.new("ScNodeSocketBool", "Brute Force").init("in_bf", True)

    def error_condition(self):
        return (
                super().error_condition()
                or self.inputs["Object"].default_value is None
                or self.inputs["Center Points"].default_value is None
                or mute_node
        )

    def pre_execute(self):
        super().pre_execute()
        for obj in self.prop_obj_array[1:-1].split(', '):
            try:
                remove_object(eval(obj))
            except:
                print_log(self.name, None, "pre_execute", "Invalid object: " + obj)
        self.prop_obj_array = "[]"

    def qhull_qvoronoi(self, points, obj, total_chunks, selection):
        # qhull implementation:
        chunks = []
        num_paddin = len(str(total_chunks))

        if selection:
            # set facemap inner:
            bpy.context.active_object.face_maps.active_index = bpy.context.active_object.face_maps['inner'].index

        for i in range(total_chunks):
            new_obj = obj.copy()
            new_obj.name = "chunk_" + str(i+1).zfill(num_paddin)
            new_obj.data = obj.data.copy()
            bpy.context.collection.objects.link(new_obj)
            chunks.append(new_obj)
        
        # prepare input stdin:
        out_ponints = "3 rbox " + str(len(points)) + " D3\n" + str(len(points)) + "\n"
        for point in points:
            out_ponints = out_ponints + str(point[0]) + " " + str(point[1]) + " " + str(point[2]) + "\n"

        qvoronoi_abs_path = os.path.dirname(os.path.abspath(__file__))

        user_system = platform.system()
        if user_system == "Linux":
            my_file = qvoronoi_abs_path + '/voronoi/qhull/' + 'qvoronoi_lnx64'
            if not os.access(my_file, os.X_OK):
                os.chmod(my_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IXOTH | stat.S_IROTH)
            process = run([my_file, 'Fv'], stdout=PIPE, input=out_ponints, encoding='ascii')
        elif user_system == "Darwin":
            my_file = qvoronoi_abs_path + '/voronoi/qhull/' + 'qvoronoi_mac64'
            if not os.access(my_file, os.X_OK):
                os.chmod(my_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IXOTH | stat.S_IROTH)
            process = run([my_file, 'Fv'], stdout=PIPE, input=out_ponints, encoding='ascii')
        elif user_system == "Windows":
            my_file = qvoronoi_abs_path + '/voronoi/qhull/' + 'qvoronoi_win64.exe'
            if not os.access(my_file, os.X_OK):
                os.chmod(my_file, stat.S_IRWXU | stat.S_IRWXG | stat.S_IXOTH | stat.S_IROTH)
            process = run([my_file, 'Fv'], stdout=PIPE, input=out_ponints, encoding='ascii')
        else:
            print("Invalid System!")

        # print("process.returncode: ", process.returncode)
        # print("process.stout: ", process.stdout)

        qhull_out = process.stdout

        qhull_out = qhull_out.replace(" ", ",")
        qhull_out = qhull_out.split("\n")
        # remove first and last items:
        qhull_out = qhull_out[1:-1]

        # print(qhull_out)

        qh_splited = []
        for i in qhull_out:
            qh_splited.append(i.split(","))

        # print(qh_splited)

        qh_ints = []
        for i in qh_splited:
            # except first index:
            for j in i[1:3]:
                qh_ints.append(int(j))

        # print(qh_ints)

        # pairs:
        rp_pairs = []
        for item1, item2 in zip(qh_ints[0::2], qh_ints[1::2]):
            rp_pairs.append([int(item1), int(item2)])

        # print(rp_pairs)
        win = bpy.context.window_manager
        win.progress_begin(0, len(rp_pairs))

        p = 0
        for bounding_pair in rp_pairs:
            win.progress_update(p)

            voroCenter = (points[bounding_pair[0]] + points[bounding_pair[1]]) * 0.5
            aim = mathutils.Vector(points[bounding_pair[0]] - points[bounding_pair[1]])
            aim.normalize()

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = chunks[bounding_pair[0]]
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bisect(plane_co=voroCenter, plane_no=aim, use_fill=True, clear_outer=False, clear_inner=True)
            if selection:
                # assing to facemap inner:
                bpy.ops.object.face_map_assign()
                # select facemap inner:
                bpy.ops.object.face_map_select()
            else:
                bpy.ops.mesh.select_all(action='DESELECT')

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = chunks[bounding_pair[1]]
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bisect(plane_co=voroCenter, plane_no=-aim, use_fill=True, clear_outer=False, clear_inner=True)
            if selection:
                # assing to facemap inner:
                bpy.ops.object.face_map_assign()
                # select facemap inner:
                bpy.ops.object.face_map_select()
            else:
                bpy.ops.mesh.select_all(action='DESELECT')
            p += 1

        bpy.ops.object.mode_set(mode='OBJECT')
        win.progress_end()
        return chunks

    def brute_force(self, input_points, obj, total_chunks, selection):
        # with cython:
        chunks = voronoi.call_fracture_voronoi(input_points, obj, total_chunks, selection)
        return chunks

        # python brute force:
        # win = bpy.context.window_manager
        # win.progress_begin(0, total_chunks)
        #
        # chunks  = []
        # num_paddin = len(str(total_chunks))
        #
        # i = 0
        # for from_point in input_points:
        #
        #     bpy.context.view_layer.objects.active = obj
        #     new_obj = obj.copy()
        #     new_obj.name = "chunk_" + str(i + 1).zfill(num_paddin)
        #     new_obj.data = obj.data.copy()
        #     bpy.context.collection.objects.link(new_obj)
        #     chunks.append(new_obj)
        #     bpy.context.view_layer.objects.active = new_obj
        #
        #     if not bpy.context.active_object.select_get():
        #         bpy.context.active_object.select_set(True)
        #
        #     bpy.ops.object.mode_set(mode='EDIT')
        #
        #     for to_point in input_points:
        #
        #         from_point = mathutils.Vector((from_point[0], from_point[1], from_point[2]))
        #         to_point = mathutils.Vector((to_point[0], to_point[1], to_point[2]))
        #
        #         if from_point != to_point:
        #             # Calculate the Perpendicular Bisector Plane
        #
        #             voro_center = mathutils.Vector(((to_point + from_point) * 0.5))
        #             aim = mathutils.Vector((from_point - to_point))
        #             aim.normalize()
        #
        #             # Bullet Shatter
        #             bpy.ops.mesh.select_all(action='SELECT')
        #             bpy.ops.mesh.bisect(
        #                 plane_co=voro_center,
        #                 plane_no=aim,
        #                 use_fill=True,
        #                 clear_outer=False,
        #                 clear_inner=True
        #             )
        #
        #     if bpy.context.active_object.mode != 'OBJECT':
        #         bpy.ops.object.mode_set(mode='OBJECT')
        #
        #     bpy.ops.object.select_all(action='DESELECT')
        #
        #     win.progress_update(i)
        #     i += 1
        #
        # win.progress_end()
        # return chunks

    def functionality(self):
        points_obj = self.inputs["Center Points"].default_value
        obj = self.inputs["Object"].default_value
        selection = self.inputs["Inner selection"].default_value
        bf = self.inputs["Brute Force"].default_value
        points = np.array([(points_obj.matrix_world @ v.co) for v in points_obj.data.vertices])
        total_chunks = len(points_obj.data.vertices)

        if selection:
            # set to face mode:
            if bpy.context.active_object.mode != 'EDIT':
                bpy.ops.object.mode_set(mode='EDIT')
            #
            if not bpy.context.tool_settings.mesh_select_mode[2]:
                bpy.context.tool_settings.mesh_select_mode = (False, False, True)

        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        if selection:
            # add new facemap inner:
            bpy.ops.object.face_map_add()
            bpy.context.active_object.face_maps[-1].name = "inner"

        bpy.ops.object.select_all(action='DESELECT')
        # hide original object:
        obj.hide_set(True)


        if bf:
            chunks = self.brute_force(points, obj, total_chunks, str(selection))
        else:
            chunks = self.qhull_qvoronoi(points, obj, total_chunks, selection)

        for i in range(len(chunks)):
            temp = eval(self.prop_obj_array)
            temp.append(chunks[i])
            self.prop_obj_array = repr(temp)

        # optional (set color random in viewport):
        # my_areas = bpy.context.workspace.screens[0].areas
        # for area in my_areas:
        #     for space in area.spaces:
        #         if space.type == 'VIEW_3D':
        #             space.shading.color_type = 'RANDOM'

    def post_execute(self):
        out = super().post_execute()
        out["Chunks"] = self.prop_obj_array
        return out
