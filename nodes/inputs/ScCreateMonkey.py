import bpy

from bpy.props import FloatProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_input import ScInputNode

class ScCreateMonkey(Node, ScInputNode):
    bl_idname = "ScCreateMonkey"
    bl_label = "Create Monkey (Suzanne)"

    in_uv: BoolProperty(default=True, update=ScNode.update_value)
    in_size: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    breack_size: BoolProperty(default=False, update=ScNode.update_value)
    in_size_x: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    in_size_y: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)
    in_size_z: FloatProperty(default=2.0, min=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketBool", "Generate UVs").init("in_uv")
        self.inputs.new("ScNodeSocketNumber", "Size").init("in_size", True)
        self.inputs.new("ScNodeSocketBool", "Breack Size").init("breack_size", True)
        self.inputs.new("ScNodeSocketNumber", "X").init("in_size_x", False)
        self.inputs.new("ScNodeSocketNumber", "Y").init("in_size_y", False)
        self.inputs.new("ScNodeSocketNumber", "Z").init("in_size_z", False)
    
    def error_condition(self):
        return (
            super().error_condition()
            or self.inputs["Size"].default_value <= 0
        )
    
    def functionality(self):
        if self.inputs["Breack Size"].default_value:
            self.inputs["Size"].hide = True
            self.inputs["X"].hide = False
            self.inputs["Y"].hide = False
            self.inputs["Z"].hide = False
            bpy.ops.mesh.primitive_monkey_add(
                size = 1,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )
            bpy.context.active_object.scale.x = self.inputs["X"].default_value
            bpy.context.active_object.scale.y = self.inputs["Y"].default_value
            bpy.context.active_object.scale.z = self.inputs["Z"].default_value
        else:
            self.inputs["Size"].hide = False
            self.inputs["X"].hide = True
            self.inputs["Y"].hide = True
            self.inputs["Z"].hide = True
            bpy.ops.mesh.primitive_monkey_add(
                size = self.inputs["Size"].default_value,
                calc_uvs = self.inputs["Generate UVs"].default_value
            )