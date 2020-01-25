import bpy
import bmesh

from bpy.props import  FloatProperty, IntProperty, EnumProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_operator import ScObjectOperatorNode
from ...helper import remove_object

class ScPointScatter(Node, ScObjectOperatorNode):
    bl_idname = "ScPointScatter"
    bl_label = "Point Scatter"
    ob_ev = None
    in_number: IntProperty(min=1, default=100, update=ScNode.update_value)
    in_seed: IntProperty(min=0, max=10000, update=ScNode.update_value)
    in_source: EnumProperty(name="Source", items=[("FACE", "Face", ""), ("VOLUME", "Volume", "")], default="FACE", update=ScNode.update_value)
    in_distribution: EnumProperty(name="Distribution", items=[("JIT", "Jittered", ""), ("RAND", "Random", ""), ("GRID", "Grid", "")], default="RAND", update=ScNode.update_value)
    in_grid_resolution: IntProperty(min=0, default=10, update=ScNode.update_value)
    in_grid_random: FloatProperty(min=0.0, max=1.0, default=0.0, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.outputs.new("ScNodeSocketObject", "Point Scatter")
        self.inputs.new("ScNodeSocketNumber", "Number").init("in_number",True)
        self.inputs.new("ScNodeSocketNumber", "Seed").init("in_seed",True)
        self.inputs.new("ScNodeSocketString", "Source").init("in_source",True)
        self.inputs.new("ScNodeSocketString", "Distribution").init("in_distribution",True)
        self.inputs.new("ScNodeSocketNumber", "Grid Resolution").init("in_grid_resolution",True)
        self.inputs.new("ScNodeSocketNumber", "Grid Random").init("in_grid_random",True)

    def pre_execute(self):
        remove_object(self.outputs["Point Scatter"].default_value)
        super().pre_execute()
    
    def functionality(self):

        in_number = self.inputs["Number"].default_value
        in_seed = self.inputs["Seed"].default_value
        in_source = self.inputs["Source"].default_value
        in_distribution = self.inputs["Distribution"].default_value
        in_grid_resolution = self.inputs["Grid Resolution"].default_value
        in_grid_random = self.inputs["Grid Random"].default_value

        active_object = self.inputs["Object"].default_value

        name = "Vert"
        me = bpy.data.meshes.new(name + "_mesh")
        obj = bpy.data.objects.new(name, me)
        obj.location = bpy.context.scene.cursor.location
        me.from_pydata([(0,0,0)], [], [])
        me.update()
        bpy.context.collection.objects.link(obj)
        
        bpy.context.view_layer.objects.active = active_object
        active_object.modifiers.new("Vert_System", type='PARTICLE_SYSTEM')
        bpy.data.particles["Vert_System"].type = 'EMITTER'
        bpy.data.particles["Vert_System"].count = in_number
        active_object.particle_systems.active.seed = in_seed
        print(active_object.particle_systems.active.seed)
        bpy.data.particles["Vert_System"].render_type = 'OBJECT'
        bpy.data.particles["Vert_System"].instance_object = bpy.data.objects["Vert"]
        bpy.data.particles["Vert_System"].particle_size = 1
        bpy.data.particles["Vert_System"].frame_end = 1
        bpy.data.particles["Vert_System"].emit_from = in_source
        bpy.data.particles["Vert_System"].distribution = in_distribution
        bpy.data.particles["Vert_System"].grid_resolution = in_grid_resolution
        bpy.data.particles["Vert_System"].grid_random = in_grid_random

        context = bpy.context
        ob = context.object
        mwi = ob.matrix_world.inverted()
        dg = context.evaluated_depsgraph_get()
        bm = bmesh.new()

        for ob_inst in dg.object_instances:
            if ob_inst.parent and ob_inst.parent.original == ob:
                me = ob_inst.instance_object.data
                bm.from_mesh(me)
                # transform to match instance
                bmesh.ops.transform(bm,
                        matrix=mwi @ ob_inst.matrix_world,
                        verts=bm.verts[-len(me.vertices):]
                        )

        me = bpy.data.meshes.new("Point Scatter_me")
        bm.to_mesh(me)
        self.ob_ev = bpy.data.objects.new("Point Scatter", me) 
        self.ob_ev.matrix_world = ob.matrix_world
        context.collection.objects.link(self.ob_ev)

        bpy.data.objects.remove(bpy.data.objects["Vert"])
        bpy.ops.object.particle_system_remove()
        bpy.data.particles.remove(bpy.data.particles["Vert_System"], do_unlink=False, do_id_user=True, do_ui_user=True)
        bm.free()

    def post_execute(self):
        out = super().post_execute()
        out["Point Scatter"] = self.ob_ev
        return out
