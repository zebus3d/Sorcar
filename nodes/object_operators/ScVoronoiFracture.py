import bpy
import mathutils
import math

from bpy.props import PointerProperty, StringProperty
from bpy.types import Node
from math import degrees, pi
from .._base.node_base import ScNode
from .._base.node_operator import ScObjectOperatorNode
from ...helper import remove_object, print_log


"""
This is first implementation of fracture voronoi with Brute Force
"""


class ScVoronoiFracture(Node, ScObjectOperatorNode):
    bl_idname = "ScVoronoiFracture"
    bl_label = "Voronoi Fracture"

    in_obj: PointerProperty(type=bpy.types.Object, update=ScNode.update_value)
    prop_obj_array: StringProperty(default="[]")
    
    def init(self,context):
        super().init(context)
        self.inputs.new("ScNodeSocketObject", "Center Points").init("in_obj", True)
        self.outputs.new("ScNodeSocketArray", "Chunks")

    def error_condition(self):
        return(
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


    def functionality(self):        
        points_obj = self.inputs["Center Points"].default_value
        v = points_obj.data.vertices
        voroPoints = [(points_obj.matrix_world @ v.co) for v in points_obj.data.vertices]
      
        vecPlaneAngle = mathutils.Vector((0, 0, 1))

        obj = self.inputs["Object"].default_value
        

        for voroFrom in voroPoints:
            bpy.ops.object.mode_set(mode = 'OBJECT')
            bpy.ops.object.select_all(action='DESELECT')

            bpy.context.view_layer.objects.active = obj
            bpy.context.active_object.select_set(True)

            bpy.ops.object.duplicate()
            workingObj = bpy.context.view_layer.objects.active
        

            bpy.ops.object.mode_set(mode = 'EDIT')

            for voroTo in voroPoints:
                if voroFrom != voroTo:
                    # Calculate the Perpendicular Bisector Plane
                    aim = [(vec1 - vec2) for (vec1, vec2) in zip(voroFrom, voroTo)]
                    voroCenter = [(vec1 + vec2)/2 for (vec1, vec2) in zip(voroTo, voroFrom)]

                    vec_aim = mathutils.Vector(( aim[0], aim[1], aim[2] ))
                    vec = vecPlaneAngle.rotation_difference(vec_aim).to_euler()
                    vecPlaneAngle.rotate( vec )

                    avoroCenter = [voroCenter[0], voroCenter[1], voroCenter[2]]

                    # Bullet Shatter
                    print(bpy.context.active_object.name)
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.bisect(plane_co=avoroCenter, plane_no=vecPlaneAngle, use_fill=True, clear_outer=False, clear_inner=True)
            
            temp = eval(self.prop_obj_array)
            temp.append(bpy.context.active_object)
            self.prop_obj_array = repr(temp)

            bpy.ops.object.mode_set(mode = 'OBJECT')


    def post_execute(self):
        out = super().post_execute()
        out["Chunks"] = self.prop_obj_array
        return out
