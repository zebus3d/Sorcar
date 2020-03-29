import bpy

from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_input import ScInputNode

class ScCreateCylinder(Node, ScInputNode):
    bl_idname = "ScCreateCylinder"
    bl_label = "Create Cylinder"

    in_uv: BoolProperty(default=True, update=ScNode.update_value)
    in_type: EnumProperty(items=[("NOTHING", "Nothing", ""), ("NGON", "Ngon", ""), ("TRIFAN", "Triangle Fan", "")], default="NGON", update=ScNode.update_value)
    in_vertices: IntProperty(default=32, min=3, max=10000000, update=ScNode.update_value)
    in_radius: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)
    in_depth: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    breack_radius: BoolProperty(default=False, update=ScNode.update_value)
    in_size_x: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)
    in_size_y: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)
    in_size_z: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketBool", "Generate UVs").init("in_uv")
        self.inputs.new("ScNodeSocketString", "Cap Fill Type").init("in_type")
        self.inputs.new("ScNodeSocketNumber", "Vertices").init("in_vertices", True)
        self.inputs.new("ScNodeSocketNumber", "Radius").init("in_radius", True)
        self.inputs.new("ScNodeSocketNumber", "Depth").init("in_depth", True)
        self.inputs.new("ScNodeSocketBool", "Breack Radius").init("breack_radius", True)
        self.inputs.new("ScNodeSocketNumber", "X").init("in_size_x", False)
        self.inputs.new("ScNodeSocketNumber", "Y").init("in_size_y", False)
        self.inputs.new("ScNodeSocketNumber", "Z").init("in_size_z", False)
    
    def error_condition(self):
        return (
            super().error_condition()
            or (not self.inputs["Cap Fill Type"].default_value in ['NOTHING', 'NGON', 'TRIFAN'])
            or (self.inputs["Vertices"].default_value < 3 or self.inputs["Vertices"].default_value > 10000000)
            or self.inputs["Radius"].default_value < 0
            or self.inputs["Depth"].default_value < 0
        )
    
    def functionality(self):
        if self.inputs["Breack Radius"].default_value:
            self.inputs["Radius"].hide = True
            self.inputs["X"].hide = False
            self.inputs["Y"].hide = False
            self.inputs["Z"].hide = False
            bpy.ops.mesh.primitive_cylinder_add(
                vertices = int(self.inputs["Vertices"].default_value),
                radius = 1,
                depth = self.inputs["Depth"].default_value,
                end_fill_type = self.inputs["Cap Fill Type"].default_value,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )
            bpy.context.active_object.scale.x = self.inputs["X"].default_value
            bpy.context.active_object.scale.y = self.inputs["Y"].default_value
            bpy.context.active_object.scale.z = self.inputs["Z"].default_value
        else:
            self.inputs["Radius"].hide = False
            self.inputs["X"].hide = True
            self.inputs["Y"].hide = True
            self.inputs["Z"].hide = True
            bpy.ops.mesh.primitive_cylinder_add(
                vertices = int(self.inputs["Vertices"].default_value),
                radius = self.inputs["Radius"].default_value,
                depth = self.inputs["Depth"].default_value,
                end_fill_type = self.inputs["Cap Fill Type"].default_value,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )