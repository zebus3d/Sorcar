import bpy

from datetime import datetime
from .voronoi import voronoi

from bpy.props import PointerProperty, StringProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_operator import ScObjectOperatorNode
from ...helper import remove_object, print_log


class ScVoronoiFractureCython(Node, ScObjectOperatorNode):
    bl_idname = "ScVoronoiFractureCython"
    bl_label = "Voronoi Fracture Cython"

    in_obj: PointerProperty(type=bpy.types.Object, update=ScNode.update_value)
    prop_obj_array: StringProperty(default="[]")
    in_enable_kdtree: BoolProperty(
        default=False,
        description="This option makes it enable_kdtree (with homogeneous scattered points only)",
        update=ScNode.update_value
    )

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketObject", "Center Points").init("in_obj", True)
        self.outputs.new("ScNodeSocketArray", "Chunks")
        self.inputs.new("ScNodeSocketBool", "Enable KDTree").init("in_enable_kdtree", True)

    def error_condition(self):
        return (
                super().error_condition()
                or self.inputs["Center Points"].default_value == None
        )

    def pre_execute(self):
        super().pre_execute()
        for obj in self.prop_obj_array[1:-1].split(', '):
            try:
                remove_object(eval(obj))
            except:
                print_log(self.name, None, "pre_execute", "Invalid object: " + obj)
        self.prop_obj_array = "[]"

    def focus_on_original_object(self):
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.view_layer.objects.active = self.inputs["Object"].default_value
        bpy.context.active_object.select_set(True)

    def functionality(self):
        print(voronoi.__file__)
        input_points_obj = self.inputs["Center Points"].default_value
        enable_kdtree = self.inputs["Enable KDTree"].default_value
        obj = self.inputs["Object"].default_value

        input_points = [(input_points_obj.matrix_world @ v.co) for v in input_points_obj.data.vertices]

        start = datetime.now()
        voronoi.fracture_voronoi(input_points, obj.name, str(enable_kdtree), input_points_obj.name)
        print("total time: ", datetime.now() - start)

        temp = eval(self.prop_obj_array)
        for ob in bpy.data.objects:
            if ob.name.startswith("chunk_"):
                temp.append(ob)
        # temp.append(bpy.context.active_object)
        self.prop_obj_array = repr(temp)

        self.focus_on_original_object()
        # bpy.context.active_object.name = "Original"
        bpy.context.active_object.hide_set(True)
        # bpy.ops.object.delete(use_global=False)


    def post_execute(self):
        out = super().post_execute()
        out["Chunks"] = self.prop_obj_array
        return out
