import bpy

from bpy.props import IntProperty, FloatProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_input import ScInputNode

class ScCreateGrid(Node, ScInputNode):
    bl_idname = "ScCreateGrid"
    bl_label = "Create Grid"

    in_uv: BoolProperty(default=True, update=ScNode.update_value)
    in_x: IntProperty(default=10, min=2, max=10000000, update=ScNode.update_value)
    in_y: IntProperty(default=10, min=2, max=10000000, update=ScNode.update_value)
    in_size: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    breack_size: BoolProperty(default=False, update=ScNode.update_value)
    in_size_x: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    in_size_y: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketBool", "Generate UVs").init("in_uv")
        self.inputs.new("ScNodeSocketNumber", "X Subdivisions").init("in_x", True)
        self.inputs.new("ScNodeSocketNumber", "Y Subdivisions").init("in_y", True)
        self.inputs.new("ScNodeSocketNumber", "Size").init("in_size", True)
        self.inputs.new("ScNodeSocketBool", "Breack Size").init("breack_size", True)
        self.inputs.new("ScNodeSocketNumber", "X").init("in_size_x", False)
        self.inputs.new("ScNodeSocketNumber", "Y").init("in_size_y", False)
    
    def error_condition(self):
        return (
            super().error_condition()
            or (self.inputs["X Subdivisions"].default_value < 2 or self.inputs["X Subdivisions"].default_value > 10000000)
            or (self.inputs["Y Subdivisions"].default_value < 2 or self.inputs["Y Subdivisions"].default_value > 10000000)
            or self.inputs["Size"].default_value <= 0
        )
    
    def functionality(self):
        if self.inputs["Breack Size"].default_value:
            self.inputs["Size"].hide = True
            self.inputs["X"].hide = False
            self.inputs["Y"].hide = False
            bpy.ops.mesh.primitive_grid_add(
                x_subdivisions = int(self.inputs["X Subdivisions"].default_value),
                y_subdivisions = int(self.inputs["Y Subdivisions"].default_value),
                size = 1,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )
            bpy.context.active_object.scale.x = self.inputs["X"].default_value
            bpy.context.active_object.scale.y = self.inputs["Y"].default_value
        else:
            self.inputs["Size"].hide = False
            self.inputs["X"].hide = True
            self.inputs["Y"].hide = True
            bpy.ops.mesh.primitive_grid_add(
                x_subdivisions = int(self.inputs["X Subdivisions"].default_value),
                y_subdivisions = int(self.inputs["Y Subdivisions"].default_value),
                size = self.inputs["Size"].default_value,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )