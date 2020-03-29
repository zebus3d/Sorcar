import bpy

from bpy.props import IntProperty, FloatProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_input import ScInputNode

class ScCreateUvSphere(Node, ScInputNode):
    bl_idname = "ScCreateUvSphere"
    bl_label = "Create UV Sphere"

    in_uv: BoolProperty(default=True, update=ScNode.update_value)
    in_segment: IntProperty(default=32, min=3, max=10000000, update=ScNode.update_value)
    in_ring: IntProperty(default=16, min=3, max=10000000, update=ScNode.update_value)
    in_radius: FloatProperty(default=1.0, min=0.0, update=ScNode.update_value)
    breack_radius: BoolProperty(default=False, update=ScNode.update_value)
    in_size_x: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    in_size_y: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    in_size_z: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketBool", "Generate UVs").init("in_uv")
        self.inputs.new("ScNodeSocketNumber", "Segments").init("in_segment", True)
        self.inputs.new("ScNodeSocketNumber", "Rings").init("in_ring", True)
        self.inputs.new("ScNodeSocketNumber", "Radius").init("in_radius", True)
        self.inputs.new("ScNodeSocketBool", "Breack Radius").init("breack_radius", True)
        self.inputs.new("ScNodeSocketNumber", "X").init("in_size_x", False)
        self.inputs.new("ScNodeSocketNumber", "Y").init("in_size_y", False)
        self.inputs.new("ScNodeSocketNumber", "Z").init("in_size_z", False)
    
    def error_condition(self):
        return (
            super().error_condition()
            or (self.inputs["Segments"].default_value < 3 or self.inputs["Segments"].default_value > 10000000)
            or (self.inputs["Rings"].default_value < 3 or self.inputs["Rings"].default_value > 10000000)
            or self.inputs["Radius"].default_value < 0
        )
    
    def functionality(self):
        if self.inputs["Breack Radius"].default_value:
            self.inputs["Radius"].hide = True
            self.inputs["X"].hide = False
            self.inputs["Y"].hide = False
            self.inputs["Z"].hide = False
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments = int(self.inputs["Segments"].default_value),
                ring_count = int(self.inputs["Rings"].default_value),
                radius = self.inputs["Radius"].default_value,
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
            bpy.ops.mesh.primitive_uv_sphere_add(
                segments = int(self.inputs["Segments"].default_value),
                ring_count = int(self.inputs["Rings"].default_value),
                radius = self.inputs["Radius"].default_value,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )