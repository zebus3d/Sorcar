import bpy
import mathutils
import numpy as np

from datetime import datetime

from bpy.props import PointerProperty, StringProperty, IntProperty, BoolProperty
from bpy.types import Node
from .._base.node_base import ScNode
from .._base.node_operator import ScObjectOperatorNode
from ...helper import remove_object, print_log


def my_pre_update(self, context):
    # if need lock any property, or
    # hide/show any property:
    if self.in_enable_kdtree:
        option = True
    else:
        option = False

    ## if need hide the property:
    # self.inputs["Precision"].prop_visible = option

    ## if need lock the property:
    # self.inputs["Precision"].prop_enabled = option

    # and now call the original sorcar update:
    self.update_value(context)


def add_material(obj, material_name, color=(0, 0, 0, 1)):
    material = bpy.data.materials.get(material_name)
    if material is None:
        material = bpy.data.materials.new(material_name)
    material.use_nodes = True
    principled_bsdf = material.node_tree.nodes['Principled BSDF']
    if principled_bsdf is not None:
        principled_bsdf.inputs[0].default_value = color
        principled_bsdf.inputs[5].default_value = 0 # Specular
        principled_bsdf.inputs[7].default_value = 1 # Roughness
    #obj.active_material = material
    #total_slots = len(obj.material_slots)
    obj.data.materials.append(material)
    #imat = obj.active_material_index
    #obj.material_slots[imat].material = material
    bpy.data.materials[material_name].diffuse_color = color
    bpy.data.materials[material_name].roughness = 0.3


def set_material_to_selection(obj, mat_name):
    materials = obj.data.materials[:]
    index = materials.index(bpy.data.materials[mat_name])
    bpy.context.object.active_material_index = index
    bpy.ops.object.material_slot_assign()


class ScVoronoiFractureKDTree(Node, ScObjectOperatorNode):
    bl_idname = "ScVoronoiFractureKDTree"
    bl_label = "Voronoi Fracture KDTree"

    in_obj: PointerProperty(type=bpy.types.Object, update=ScNode.update_value)
    prop_obj_array: StringProperty(default="[]")
    in_enable_kdtree: BoolProperty(
        default=False,
        description="This option makes it enable_kdtree (with homogeneous scattered input_points only)",
        update=my_pre_update
    )
    # in_precision: IntProperty(min=1, default=50, update=ScNode.update_value)

    def init(self, context):
        super().init(context)
        self.inputs.new("ScNodeSocketObject", "Center Points").init("in_obj", True)
        self.outputs.new("ScNodeSocketArray", "Chunks")
        self.inputs.new("ScNodeSocketBool", "Enable KDTree").init("in_enable_kdtree", True)
        # self.inputs.new("ScNodeSocketNumber", "Precision").init("in_precision", True)
        # self.inputs["Precision"].prop_enabled = False

    def error_condition(self):
        return (
                super().error_condition()
                or self.inputs["Center Points"].default_value is None
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
        # in_precision = self.inputs["Precision"].default_value
        input_points_obj = self.inputs["Center Points"].default_value
        enable_kdtree = self.inputs["Enable KDTree"].default_value

        input_points = np.array([(input_points_obj.matrix_world @ v.co) for v in input_points_obj.data.vertices])
        total_input_points = len(input_points)

        # KDTree:
        if enable_kdtree:
            kd = mathutils.kdtree.KDTree(total_input_points)
            for i, v in enumerate(input_points_obj.data.vertices):
                kd.insert(v.co, i)
            kd.balance()

        add_material(bpy.context.active_object, "outside_mat", (1, 1, 1, 1))
        add_material(bpy.context.active_object, "inside_mat", (0, 0, 0, 1))

        start = datetime.now()
        i = 0
        for from_point in input_points:

            self.focus_on_original_object()
            bpy.ops.object.duplicate()

            bpy.context.active_object.name = "chunk_" + str(i).zfill(len(str(total_input_points)))
            i += 1

            # KDTree
            if enable_kdtree:
                if total_input_points >= 66:
                    auto_precision = float(total_input_points) * float(41) / float(100)
                elif 66 > total_input_points > 15:
                    auto_precision = 40
                elif total_input_points <= 15:
                    auto_precision = total_input_points

                Nearinput_points = kd.find_n(from_point, int(auto_precision))
                #Nearinput_points = kd.find_n(from_point, int(in_precision))
            else:
                Nearinput_points = input_points

            bpy.ops.object.mode_set(mode='EDIT')

            for to_point in Nearinput_points:

                # KDTree:
                if enable_kdtree:
                    to_point = to_point[0]
                else:
                    to_point = mathutils.Vector((to_point[0], to_point[1], to_point[2]))

                # print("to_point: ", to_point)
                # print("from_point: ", mathutils.Vector((from_point[0], from_point[1], from_point[2])))
                from_point = mathutils.Vector((from_point[0], from_point[1], from_point[2]))
                if from_point != to_point:
                    # Calculate the Perpendicular Bisector Plane
                    
                    # old:
                    #aim = np.array([(vec1 - vec2) for (vec1, vec2) in zip(from_point, to_point)])
                    #voro_center = np.array([(vec1 + vec2) / 2 for (vec1, vec2) in zip(to_point, from_point)])

                    #vec_aim = mathutils.Vector((aim[0], aim[1], aim[2]))
                    ## vecPlaneAngle = mathutils.Vector((0, 0, 1))
                    ## vec = vecPlaneAngle.rotation_difference(vec_aim).to_euler()
                    ## vecPlaneAngle.rotate(vec)
                    #vec_aim.normalize()
                    
                    # new:
                    aim = mathutils.Vector(( from_point - to_point ))
                    voro_center = mathutils.Vector(( (to_point + from_point) / 2 ))
                    aim.normalize()

                    # Bullet Shatter
                    # print(bpy.context.active_object.name)
                    bpy.ops.mesh.select_all(action='SELECT')
                    bpy.ops.mesh.bisect(
                        plane_co=voro_center,
                        # plane_no=vecPlaneAngle,
                        plane_no=aim,
                        use_fill=True,
                        clear_outer=False,
                        clear_inner=True
                    )
                    set_material_to_selection(bpy.context.active_object, "inside_mat")
                    # for chunk put the origin in geometry center:
                    bpy.ops.object.mode_set(mode='OBJECT')
                    bpy.ops.object.origin_set(type='ORIGIN_GEOMETRY', center='MEDIAN')
                    bpy.ops.object.mode_set(mode='EDIT')

            temp = eval(self.prop_obj_array)
            temp.append(bpy.context.active_object)
            self.prop_obj_array = repr(temp)

        print("total time: ", datetime.now() - start)

        self.focus_on_original_object()
        bpy.context.active_object.name = "Original"
        bpy.context.active_object.hide_set(True)
        #bpy.ops.object.delete(use_global=False)

    def post_execute(self):
        out = super().post_execute()
        out["Chunks"] = self.prop_obj_array
        return out