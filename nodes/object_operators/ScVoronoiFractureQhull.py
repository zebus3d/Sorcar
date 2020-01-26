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
    in_bf: BoolProperty(default=False, description="The brute force method is slower but works better (especially with low numbers of points)", update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketObject", "Center Points").init("in_obj", True)
        self.outputs.new("ScNodeSocketArray", "Chunks")
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

    def qhull_qvoronoi(self, points, objects):
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
            bpy.context.view_layer.objects.active = objects[bounding_pair[0]]
            # set facemap inner:
            bpy.context.active_object.face_maps.active_index = bpy.context.active_object.face_maps['inner'].index
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bisect(plane_co=voroCenter, plane_no=aim, use_fill=True, clear_outer=False, clear_inner=True)
            # assing to facemap inner:
            bpy.ops.object.face_map_assign()
            # select only facemap inner:
            bpy.ops.object.face_map_select()

            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.context.view_layer.objects.active = objects[bounding_pair[1]]
            # set facemap inner:
            bpy.context.active_object.face_maps.active_index = bpy.context.active_object.face_maps['inner'].index
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action='SELECT')
            bpy.ops.mesh.bisect(plane_co=voroCenter, plane_no=-aim, use_fill=True, clear_outer=False, clear_inner=True)
            # assing to facemap inner:
            bpy.ops.object.face_map_assign()
            # select only facemap inner:
            bpy.ops.object.face_map_select()
            p += 1

        bpy.ops.object.mode_set(mode='OBJECT')
        win.progress_end()

    def brute_force(self, input_points, objects):
        # with cython:
        voronoi.call_fracture_voronoi(input_points, objects)

    def functionality(self):
        points_obj = self.inputs["Center Points"].default_value
        obj = self.inputs["Object"].default_value
        bf = self.inputs["Brute Force"].default_value
        points = np.array([(points_obj.matrix_world @ v.co) for v in points_obj.data.vertices])
        objects = []
        total_points = len(points_obj.data.vertices)
        num_paddin = len(str(total_points))

        if bpy.context.active_object.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # add new facemap inner:
        bpy.ops.object.face_map_add()
        bpy.context.active_object.face_maps[-1].name = "inner"

        for i in range(total_points):
            # bpy.ops.object.duplicate()
            # objects.append(bpy.context.view_layer.objects.active)
            # Duplication most faster:
            new_obj = obj.copy()
            new_obj.name = "chunk_" + str(i).zfill(num_paddin)
            new_obj.data = obj.data.copy()
            bpy.context.collection.objects.link(new_obj)
            objects.append(new_obj)

        bpy.ops.object.select_all(action='DESELECT')
        obj.hide_set(True)

        # if len(objects) > 60:
        if bf:
            self.brute_force(points, objects)
        else:
            self.qhull_qvoronoi(points, objects)

        for i in range(len(objects)):
            temp = eval(self.prop_obj_array)
            temp.append(objects[i])
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
