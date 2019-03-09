# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8-80 compliant>

"""TODO

Notes:

    TODO

Background:

    TODO
"""

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi


class Arrows:
    """TODO

    Attributes:

        TODO
    """

    @staticmethod
    def read():
        """TODO

        Args:

            TODO
        """

        pass

    @staticmethod
    def write(collection, mdi_socket, mdi_skeletons, armature_objects):
        """TODO

        Args:

            TODO
        """

        if isinstance(mdi_socket, mdi.MDISocketFree):

            empty_object = bpy.data.objects.new("empty", None)
            collection.objects.link(empty_object)
            empty_object.name = mdi_socket.name
            empty_object.empty_display_type = 'ARROWS'
            empty_object.rotation_mode = 'QUATERNION'

            matrix = mathutils.Matrix.Identity(4)
            matrix.translation = mdi_socket.location
            matrix = matrix @ mdi_socket.orientation.to_4x4()
            empty_object.matrix_world = matrix

            # animate
            for num_frame, mdi_socket_free_in_frame in \
                enumerate(mdi_socket.animation.frames):

                    matrix = mathutils.Matrix.Identity(4)
                    matrix.translation = mdi_socket_free_in_frame.location
                    matrix = matrix @ \
                        mdi_socket_free_in_frame.orientation.to_4x4()
                    empty_object.matrix_world = matrix

                    empty_object.keyframe_insert('location', \
                                              frame=num_frame, \
                                              group='LocRot')
                    empty_object.keyframe_insert('rotation_quaternion', \
                                              frame=num_frame, \
                                              group='LocRot')

        elif isinstance(mdi_socket, mdi.MDISocketParentBone):

            armature_object = \
                armature_objects[mdi_socket.parent_skeleton]
            mdi_bones = \
                mdi_skeletons.skeleton_list[mdi_socket.parent_skeleton].bones
            parent_bone_name = mdi_bones.bone_list[mdi_socket.parent_bone].name

            empty_object = bpy.data.objects.new("empty", None)
            collection.objects.link(empty_object)
            empty_object.name = mdi_socket.name
            empty_object.empty_display_type = 'ARROWS'
            empty_object.rotation_mode = 'QUATERNION'

            empty_object.constraints.new(type="CHILD_OF")
            empty_object.constraints["Child Of"].target = armature_object
            empty_object.constraints["Child Of"].subtarget = parent_bone_name

            empty_object.constraints["Child Of"].use_location_x = True
            empty_object.constraints["Child Of"].use_location_y = True
            empty_object.constraints["Child Of"].use_location_z = True

            empty_object.constraints["Child Of"].use_rotation_x = True
            empty_object.constraints["Child Of"].use_rotation_y = True
            empty_object.constraints["Child Of"].use_rotation_z = True

            empty_object.constraints["Child Of"].use_scale_x = True
            empty_object.constraints["Child Of"].use_scale_y = True
            empty_object.constraints["Child Of"].use_scale_z = True

        elif isinstance(mdi_socket, mdi.MDISocketParentBoneOffset):

            armature_object = \
                armature_objects[mdi_socket.parent_skeleton]
            mdi_bones = \
                mdi_skeletons.skeleton_list[mdi_socket.parent_skeleton].bones
            parent_bone = mdi_bones.bone_list[mdi_socket.parent_bone]

            empty_object = bpy.data.objects.new("empty", None)
            collection.objects.link(empty_object)
            empty_object.name = mdi_socket.name
            empty_object.empty_display_type = 'ARROWS'
            empty_object.rotation_mode = 'QUATERNION'

            empty_object.constraints.new(type="CHILD_OF")
            empty_object.constraints["Child Of"].target = armature_object
            empty_object.constraints["Child Of"].subtarget = parent_bone.name

            empty_object.constraints["Child Of"].use_location_x = True
            empty_object.constraints["Child Of"].use_location_y = True
            empty_object.constraints["Child Of"].use_location_z = True

            empty_object.constraints["Child Of"].use_rotation_x = True
            empty_object.constraints["Child Of"].use_rotation_y = True
            empty_object.constraints["Child Of"].use_rotation_z = True

            empty_object.constraints["Child Of"].use_scale_x = True
            empty_object.constraints["Child Of"].use_scale_y = True
            empty_object.constraints["Child Of"].use_scale_z = True

            matrix = mathutils.Matrix.Identity(4)

            matrix.translation = parent_bone.orientation.transposed() @ (mdi_socket.location - parent_bone.location)

            orientation = parent_bone.orientation.transposed() @ mdi_socket.orientation

            empty_object.matrix_world = matrix @ orientation.to_4x4()

        return empty_object


class Armature:
    """TODO

    Attributes:

        TODO
    """

    @staticmethod
    def _create_armature(collection, name):

        armature = bpy.data.armatures.new(name)
        armature_object = bpy.data.objects.new(name, armature)

        collection.objects.link(armature_object)

        return armature_object

    @staticmethod
    def _add_edit_bones(armature_object, mdi_bones):

        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='EDIT')

        for mdi_bone in mdi_bones.bone_list:

            edit_bone = armature_object.data.edit_bones.new(mdi_bone.name)

            edit_bone.head = (0, 0, 0)
            edit_bone.tail = (0, 1, 0)
            edit_bone.use_connect = False
            edit_bone.use_inherit_scale = True
            edit_bone.use_local_location = True
            edit_bone.use_inherit_rotation = True

            bind_pose_location = mdi_bone.location
            bind_pose_orientation = mdi_bone.orientation

            bind_pose_matrix = \
                mathutils.Matrix.Translation(bind_pose_location) @ \
                    bind_pose_orientation.to_4x4()
            edit_bone.matrix = bind_pose_matrix

            edit_bone['Torso Weight'] = mdi_bone.torso_weight

        # set parent-child-relationship
        for mdi_bone in mdi_bones.bone_list:

            if mdi_bone.parent_bone >= 0:

                mdi_bone_parent = mdi_bones.bone_list[mdi_bone.parent_bone]

                child = armature_object.data.edit_bones[mdi_bone.name]
                parent = armature_object.data.edit_bones[mdi_bone_parent.name]
                child.parent = parent

        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def _animate_bones(armature_object, mdi_bones):

        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='POSE')

        armature_object.animation_data_create()
        armature_object.animation_data.action = \
            bpy.data.actions.new(name=armature_object.name)

        for num_bone in range(0, len(mdi_bones.bone_list)):

            mdi_bone = mdi_bones.bone_list[num_bone]

            datapath_loc = 'pose.bones["{}"].location'.format(mdi_bone.name)
            datapath_rot = \
                'pose.bones["{}"].rotation_quaternion'.format(mdi_bone.name)

            pose_bone = armature_object.pose.bones[mdi_bone.name]
            pose_bone.rotation_mode = 'QUATERNION'

            action = armature_object.animation_data.action

            fcurve_loc_x = action.fcurves.new(data_path=datapath_loc,
                                              index=0,
                                              action_group=mdi_bone.name)
            fcurve_loc_y = action.fcurves.new(data_path=datapath_loc,
                                              index=1,
                                              action_group=mdi_bone.name)
            fcurve_loc_z = action.fcurves.new(data_path=datapath_loc,
                                              index=2,
                                              action_group=mdi_bone.name)

            fcurve_quaternion_w = action.fcurves.new(data_path=datapath_rot,
                                                     index=0,
                                                     action_group=mdi_bone.name)
            fcurve_quaternion_x = action.fcurves.new(data_path=datapath_rot,
                                                     index=1,
                                                     action_group=mdi_bone.name)
            fcurve_quaternion_y = action.fcurves.new(data_path=datapath_rot,
                                                     index=2,
                                                     action_group=mdi_bone.name)
            fcurve_quaternion_z = action.fcurves.new(data_path=datapath_rot,
                                                     index=3,
                                                     action_group=mdi_bone.name)

            frame_len = len(mdi_bone.animation.frames)
            # frame_len = 35

            fcurve_loc_x.keyframe_points.add(count=frame_len)
            fcurve_loc_z.keyframe_points.add(count=frame_len)
            fcurve_loc_y.keyframe_points.add(count=frame_len)

            fcurve_quaternion_w.keyframe_points.add(count=frame_len)
            fcurve_quaternion_x.keyframe_points.add(count=frame_len)
            fcurve_quaternion_z.keyframe_points.add(count=frame_len)
            fcurve_quaternion_y.keyframe_points.add(count=frame_len)

            # acutally animate now
            for num_frame in range(0, frame_len):

                z_cbl = mdi_bone.location
                z_cbo = mdi_bone.orientation
                z_cfl = mdi_bone.animation.frames[num_frame].location
                z_cfo = mdi_bone.animation.frames[num_frame].orientation

                if mdi_bone.parent_bone >= 0:

                    mdi_parent_bone = mdi_bones.bone_list[mdi_bone.parent_bone]

                    z_pbl = mdi_parent_bone.location
                    z_pbo = mdi_parent_bone.orientation
                    z_pfl = mdi_parent_bone.animation.frames[num_frame].location
                    z_pfo = mdi_parent_bone.animation.frames[num_frame].orientation

                    # cbl_dash
                    diff_loc = z_cbl - z_pbl
                    diff_rot = z_pfo @ z_pbo.transposed()
                    tmp = diff_rot @ diff_loc
                    cbl_dash = tmp + z_pfl

                    # cbo_dash
                    cbo_dash = z_pfo @ z_pbo.transposed() @ z_cbo

                    # location
                    location = cbo_dash.transposed() @ (z_cfl - cbl_dash)

                    # orientation
                    orientation = cbo_dash.transposed() @ z_cfo

                else:

                    orientation = z_cbo.transposed() @ z_cfo
                    location = z_cbo.transposed() @ (z_cfl - z_cbl)

                orientation = orientation.to_quaternion()

                fcurve_loc_x.keyframe_points[num_frame].co = \
                    num_frame, location.x
                fcurve_loc_y.keyframe_points[num_frame].co = \
                    num_frame, location.y
                fcurve_loc_z.keyframe_points[num_frame].co = \
                    num_frame, location.z

                fcurve_quaternion_w.keyframe_points[num_frame].co = \
                    num_frame, orientation.w
                fcurve_quaternion_x.keyframe_points[num_frame].co = \
                    num_frame, orientation.x
                fcurve_quaternion_y.keyframe_points[num_frame].co = \
                    num_frame, orientation.y
                fcurve_quaternion_z.keyframe_points[num_frame].co = \
                    num_frame, orientation.z

        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def _set_constraints(armature_object, mdi_bones):

        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='POSE')

        for mdi_bone in mdi_bones.bone_list:

            mdi_bone_parent_name = \
                mdi_bones.bone_list[mdi_bone.parent_bone].name

            if mdi_bone.parent_bone >= 0:

                pose_bone = armature_object.pose.bones[mdi_bone.name]

                pose_bone.constraints.new(type="LIMIT_DISTANCE")

                pose_bone.constraints["Limit Distance"].target = \
                    armature_object
                pose_bone.constraints["Limit Distance"].subtarget = \
                    armature_object.data.bones[mdi_bone_parent_name].name
                pose_bone.constraints["Limit Distance"].use_transform_limit \
                    = False
                pose_bone.constraints["Limit Distance"].limit_mode \
                    = "LIMITDIST_ONSURFACE"

        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def read():
        """TODO

        Args:

            TODO
        """

        pass

    @staticmethod
    def write(collection, mdi_skeleton):
        """TODO

        Args:

            TODO
        """

        armature_object = \
            Armature._create_armature(collection, mdi_skeleton.name)

        Armature._add_edit_bones(armature_object, mdi_skeleton.bones)

        Armature._animate_bones(armature_object, mdi_skeleton.bones)

        Armature._set_constraints(armature_object, mdi_skeleton.bones)

        return armature_object


class UVMap:
    """TODO

    Attributes:

        TODO
    """

    @staticmethod
    def read():
        """TODO

        Args:

            TODO
        """

        pass

    @staticmethod
    def write(mdi_uv_map, mesh_object):
        """TODO

        Args:

            TODO
        """

        # TODO handle surj/bij

        mesh_object.data.uv_layers.new(name="UVMap")

        for polygon in mesh_object.data.polygons:

            for loop_index in range(polygon.loop_start,
                                    polygon.loop_start + polygon.loop_total):

                vertex_index = mesh_object.data.loops[loop_index].vertex_index
                mesh_object.data.uv_layers['UVMap'].data[loop_index].uv = \
                    (mdi_uv_map.tex_coords_list[vertex_index].u,
                     mdi_uv_map.tex_coords_list[vertex_index].v)


# class Texture:

#     """TODO

#     Attributes:

#         TODO
#     """

#     @staticmethod
#     def read():
#         """TODO

#         Args:

#             TODO
#         """

#         pass

#     @staticmethod
#     def write():
#         """TODO

#         Args:

#             TODO
#         """

#         texture = bpy.data.textures.new('Texture', 'IMAGE')
#         texture_slot = material.texture_slots.create(0)
#         texture_slot.uv_layer = 'UVMap'
#         texture_slot.use = True
#         texture_slot.texture_coords = 'UV'
#         texture_slot.texture = texture


class Materials:
    """TODO

    Attributes:

        TODO
    """

    @staticmethod
    def _add_shader_reference(name, mesh_object):

        material = bpy.data.materials.new(name)
        mesh_object.data.materials.append(material)

    @staticmethod
    def read():
        """TODO

        Args:

            TODO
        """

        pass

    @staticmethod
    def write(mdi_shader_data, mesh_object):
        """TODO

        Args:

            TODO
        """

        if isinstance(mdi_shader_data, mdi.MDIShaderReference):

            name = mdi_shader_data.reference
            Materials._add_shader_reference(name, mesh_object)

        elif isinstance(mdi_shader_data, mdi.MDIShaderReferences):

            for mdi_shader_reference in mdi_shader_data.shader_reference_list:

                name = mdi_shader_reference.reference
                Materials._add_shader_reference(name, mesh_object)


class Mesh:
    """TODO

    Attributes:

        TODO
    """

    @staticmethod
    def _create_mesh(collection, mdi_surface):

        name = mdi_surface.name
        mesh = bpy.data.meshes.new(name)
        mesh_object = bpy.data.objects.new(name, mesh)

        mdi_vertices = mdi_surface.geometry.vertices.vertex_list
        mdi_triangles = mdi_surface.geometry.triangles.triangle_list
        vertices = [mdi_vertex.location for mdi_vertex in mdi_vertices]
        triangles = [mdi_triangle.indices for mdi_triangle in mdi_triangles]
        mesh.from_pydata(vertices, [], triangles)
        mesh.update()
        mesh.validate(verbose=True)

        collection.objects.link(mesh_object)

        return mesh_object

    @staticmethod
    def _skin_vertices(mdi_rigged_vertices, mdi_skeleton, mesh_object,
                       armature_object):

        bones = mdi_skeleton.bones.bone_list
        vertex_groups_dict = {bone.name: [] for bone in bones}

        for vertex_index, mdi_rigged_vertex in \
            enumerate(mdi_rigged_vertices.vertex_list):

            for mdi_vertex_weight in mdi_rigged_vertex.weights:

                bone_name = bones[mdi_vertex_weight.parent_bone].name
                vertex_groups_dict[bone_name].append((vertex_index,
                                                      mdi_vertex_weight.weight))

        for bone_name, weights in vertex_groups_dict.items():

            vertex_group = mesh_object.vertex_groups.new(name = bone_name)

            for vertex_index, weight in weights:

                vertex_group.add([vertex_index], weight, 'REPLACE')

        mod = mesh_object.modifiers.new('Armature', 'ARMATURE')
        mod.object = armature_object
        mod.use_bone_envelopes = False
        mod.use_vertex_groups = True

    @staticmethod
    def _morph_vertices(mdi_morph_vertices, mesh_object, bind_frame):

        for mdi_morph_vertices_in_frame in mdi_morph_vertices.frame_list:

            shape_key = mesh_object.shape_key_add(name = "Key", from_mix=False)

            for num_vertex, mdi_morph_vertex_in_frame in \
                enumerate(mdi_morph_vertices_in_frame.vertex_list):

                x = mdi_morph_vertex_in_frame.location[0]
                y = mdi_morph_vertex_in_frame.location[1]
                z = mdi_morph_vertex_in_frame.location[2]
                shape_key.data[num_vertex].co = (x, y, z)

        if mesh_object.data.shape_keys:

            mesh_object.data.shape_keys.use_relative = False
            mesh_object.active_shape_key_index = bind_frame

            for num_frame in range(len(mdi_morph_vertices.frame_list)):

                mesh_object.data.shape_keys.eval_time = 10.0 * num_frame
                mesh_object.data.shape_keys. \
                    keyframe_insert('eval_time', frame = num_frame)

        mesh_object.data.update()

    @staticmethod
    def read():
        """TODO

        Args:

            TODO
        """

        pass

    @staticmethod
    def write(collection, mdi_surface, mdi_skeletons, armature_objects,
              bind_frame):
        """TODO

        Args:

            TODO
        """

        # create
        mesh_object = Mesh._create_mesh(collection, mdi_surface)

        # animate
        mdi_vertices_animation = mdi_surface.geometry.vertices.animation

        if isinstance(mdi_vertices_animation, mdi.MDIRiggedVertices):

            armature_object = \
                armature_objects[mdi_vertices_animation.parent_skeleton]
            mdi_skeleton = mdi_skeletons. \
                skeleton_list[mdi_vertices_animation.parent_skeleton]

            Mesh._skin_vertices(mdi_vertices_animation, mdi_skeleton,
                                mesh_object, armature_object)

        elif isinstance(mdi_vertices_animation, mdi.MDIMorphVertices):

            Mesh._morph_vertices(mdi_vertices_animation, mesh_object,
                                 bind_frame)

        # shaders
        mdi_shader_data = mdi_surface.color.shader_data
        Materials.write(mdi_shader_data, mesh_object)

        # uv map
        mdi_uv_map = mdi_surface.color.uv_map
        UVMap.write(mdi_uv_map, mesh_object)

        return mesh_object


class Collection:
    """TODO

    Attributes:

        TODO
    """

    @staticmethod
    def read():
        """TODO

        Args:

            TODO
        """

        pass

    @staticmethod
    def write(mdi_model, bind_frame):
        """TODO

        Args:

            TODO
        """

        collection = bpy.data.collections.new(mdi_model.name)
        bpy.context.scene.collection.children.link(collection)

        armature_objects = []
        for mdi_skeleton in mdi_model.skeletons.skeleton_list:

            armature_object = Armature.write(collection, mdi_skeleton)
            armature_objects.append(armature_object)

        for mdi_surface in mdi_model.surfaces.surface_list:

            Mesh.write(collection, mdi_surface, mdi_model.skeletons,
                       armature_objects, bind_frame)

        for mdi_socket in mdi_model.sockets.socket_list:

            Arrows.write(collection, mdi_socket, mdi_model.skeletons,
                         armature_objects)


def read():

    mdi_model = None

    return mdi_model

def write(mdi_model, bind_frame):

    Collection.write(mdi_model, bind_frame)
