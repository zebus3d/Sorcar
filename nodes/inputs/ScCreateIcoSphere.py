import bpy

from bpy.props import IntProperty, FloatProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_input import ScInputNode

class ScCreateIcoSphere(Node, ScInputNode):
    bl_idname = "ScCreateIcoSphere"
    bl_label = "Create Ico Sphere"

    in_uv: BoolProperty(default=True, update=ScNode.update_value)
    in_subdivision: IntProperty(default=2, min=1, max=10, update=ScNode.update_value)
    in_radius: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)
    breack_radius: BoolProperty(default=False, update=ScNode.update_value)
    in_size_x: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)
    in_size_y: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)
    in_size_z: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketBool", "Generate UVs").init("in_uv")
        self.inputs.new("ScNodeSocketNumber", "Subdivisions").init("in_subdivision", True)
        self.inputs.new("ScNodeSocketNumber", "Radius").init("in_radius", True)
        self.inputs.new("ScNodeSocketBool", "Breack Radius").init("breack_radius", True)
        self.inputs.new("ScNodeSocketNumber", "X").init("in_size_x", False)
        self.inputs.new("ScNodeSocketNumber", "Y").init("in_size_y", False)
        self.inputs.new("ScNodeSocketNumber", "Z").init("in_size_z", False)
    
    def error_condition(self):
        return (
            super().error_condition()
            or (self.inputs["Subdivisions"].default_value < 1 or self.inputs["Subdivisions"].default_value > 10)
            or self.inputs["Radius"].default_value < 0
        )
    
    def functionality(self):
        if self.inputs["Breack Radius"].default_value:
            self.inputs["Radius"].hide = True
            self.inputs["X"].hide = False
            self.inputs["Y"].hide = False
            self.inputs["Z"].hide = False
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions = int(self.inputs["Subdivisions"].default_value),
                radius = 1,
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
            bpy.ops.mesh.primitive_ico_sphere_add(
                subdivisions = int(self.inputs["Subdivisions"].default_value),
                radius = self.inputs["Radius"].default_value,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )