import bpy

from bpy.props import EnumProperty, IntProperty, FloatProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_input import ScInputNode

class ScCreateTorus(Node, ScInputNode):
    bl_idname = "ScCreateTorus"
    bl_label = "Create Torus"

    in_uv: BoolProperty(default=True, update=ScNode.update_value)
    in_mode: EnumProperty(items=[("MAJOR_MINOR", "Major/Minor", ""), ("EXT_INT", "Exterior/Interior", "")], default="MAJOR_MINOR", update=ScNode.update_value)
    in_major_segment: IntProperty(default=48, min=3, max=256, update=ScNode.update_value)
    in_minor_segment: IntProperty(default=12, min=3, max=256, update=ScNode.update_value)
    in_major_radius: FloatProperty(default=1.0, min=0.01, max=100, update=ScNode.update_value)
    in_minor_radius: FloatProperty(default=0.25, min=0.01, max=100, update=ScNode.update_value)
    in_abs_major_radius: FloatProperty(default=1.25, min=0.01, max=100, update=ScNode.update_value)
    in_abs_minor_radius: FloatProperty(default=0.75, min=0.01, max=100, update=ScNode.update_value)
    breack_radius: BoolProperty(default=False, update=ScNode.update_value)
    in_size_x: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    in_size_y: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    in_size_z: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketBool", "Generate UVs").init("in_uv")
        self.inputs.new("ScNodeSocketNumber", "Major Segments").init("in_major_segment", True)
        self.inputs.new("ScNodeSocketNumber", "Minor Segments").init("in_minor_segment", True)
        self.inputs.new("ScNodeSocketString", "Torus Dimensions").init("in_mode")
        self.inputs.new("ScNodeSocketNumber", "Major Radius").init("in_major_radius", True)
        self.inputs.new("ScNodeSocketNumber", "Minor Radius").init("in_minor_radius", True)
        self.inputs.new("ScNodeSocketNumber", "Exterior Radius").init("in_abs_major_radius")
        self.inputs.new("ScNodeSocketNumber", "Interior Radius").init("in_abs_minor_radius")
        self.inputs.new("ScNodeSocketBool", "Breack Major Radius").init("breack_radius", True)
        self.inputs.new("ScNodeSocketNumber", "X").init("in_size_x", False)
        self.inputs.new("ScNodeSocketNumber", "Y").init("in_size_y", False)
        self.inputs.new("ScNodeSocketNumber", "Z").init("in_size_z", False)
    
    def error_condition(self):
        return (
            super().error_condition()
            or (not self.inputs["Torus Dimensions"].default_value in ["MAJOR_MINOR", "EXT_INT"])
            or (self.inputs["Major Segments"].default_value < 3 or self.inputs["Major Segments"].default_value > 256)
            or (self.inputs["Minor Segments"].default_value < 3 or self.inputs["Minor Segments"].default_value > 256)
            or (self.inputs["Major Radius"].default_value < 0 or self.inputs["Major Radius"].default_value > 100)
            or (self.inputs["Minor Radius"].default_value < 0 or self.inputs["Minor Radius"].default_value > 100)
            or (self.inputs["Exterior Radius"].default_value < 0 or self.inputs["Exterior Radius"].default_value > 100)
            or (self.inputs["Interior Radius"].default_value < 0 or self.inputs["Interior Radius"].default_value > 100)
        )
    
    def functionality(self):
        if self.inputs["Breack Major Radius"].default_value:
            self.inputs["Major Radius"].hide = True
            self.inputs["X"].hide = False
            self.inputs["Y"].hide = False
            self.inputs["Z"].hide = False
            bpy.ops.mesh.primitive_torus_add(
                major_segments = int(self.inputs["Major Segments"].default_value),
                minor_segments = int(self.inputs["Minor Segments"].default_value),
                mode = self.inputs["Torus Dimensions"].default_value,
                major_radius = self.inputs["Major Radius"].default_value,
                minor_radius = self.inputs["Minor Radius"].default_value,
                abso_major_rad = self.inputs["Exterior Radius"].default_value,
                abso_minor_rad = self.inputs["Interior Radius"].default_value,
                generate_uvs = self.inputs["Generate UVs"].default_value
            )
            bpy.context.active_object.scale.x = self.inputs["X"].default_value
            bpy.context.active_object.scale.y = self.inputs["Y"].default_value
            bpy.context.active_object.scale.z = self.inputs["Z"].default_value
        else:
            self.inputs["Major Radius"].hide = False
            self.inputs["X"].hide = True
            self.inputs["Y"].hide = True
            self.inputs["Z"].hide = True
            bpy.ops.mesh.primitive_torus_add(
                major_segments = int(self.inputs["Major Segments"].default_value),
                minor_segments = int(self.inputs["Minor Segments"].default_value),
                mode = self.inputs["Torus Dimensions"].default_value,
                major_radius = self.inputs["Major Radius"].default_value,
                minor_radius = self.inputs["Minor Radius"].default_value,
                abso_major_rad = self.inputs["Exterior Radius"].default_value,
                abso_minor_rad = self.inputs["Interior Radius"].default_value,
                generate_uvs = self.inputs["Generate UVs"].default_value
            )