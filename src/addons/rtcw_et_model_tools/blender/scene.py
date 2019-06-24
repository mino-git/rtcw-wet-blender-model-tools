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

"""Reading and writing a blender scene.
"""

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi

def get_verts_from_bounds(min_bound, max_bound):

    vertices = []

    v0 = (min_bound[0], min_bound[1], min_bound[2])
    v1 = (min_bound[0], max_bound[1], min_bound[2])
    v2 = (min_bound[0], min_bound[1], max_bound[2])
    v3 = (min_bound[0], max_bound[1], max_bound[2])

    v4 = (max_bound[0], max_bound[1], max_bound[2])
    v5 = (max_bound[0], min_bound[1], max_bound[2])
    v6 = (max_bound[0], max_bound[1], min_bound[2])
    v7 = (max_bound[0], min_bound[1], min_bound[2])

    vertices.append(v0)
    vertices.append(v1)
    vertices.append(v2)
    vertices.append(v3)
    vertices.append(v4)
    vertices.append(v5)
    vertices.append(v6)
    vertices.append(v7)

    return vertices

def draw_bounding_volume(mdi_bounding_volume):

    min_bound = mdi_bounding_volume.aabbs[0].min_bound
    max_bound = mdi_bounding_volume.aabbs[0].max_bound

    vertices = get_verts_from_bounds(min_bound, max_bound)

    # faces
    faces = []

    f1 = (0, 1, 3, 2)
    f2 = (4, 5, 7, 6)

    f3 = (2, 3, 4, 5)
    f4 = (0, 1, 6, 7)

    f5 = (0, 2, 5, 7)
    f6 = (1, 3, 4, 6)

    faces.append(f1)
    faces.append(f2)
    faces.append(f3)
    faces.append(f4)
    faces.append(f5)
    faces.append(f6)

    name = "BoundingBox"
    mesh = bpy.data.meshes.new(name)
    mesh_object = bpy.data.objects.new(name, mesh)
    mesh_object.display_type = 'WIRE'

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.validate(verbose=True)

    active_collection = \
        bpy.context.view_layer.active_layer_collection.collection
    active_collection.objects.link(mesh_object)

    num_frames = len(mdi_bounding_volume.aabbs)

    for num_frame in range(num_frames):

        shape_key = mesh_object.shape_key_add(name="Frame", from_mix=False)

        min_bound = mdi_bounding_volume.aabbs[num_frame].min_bound
        max_bound = mdi_bounding_volume.aabbs[num_frame].max_bound
        vertices = get_verts_from_bounds(min_bound, max_bound)

        for num_vertex, vertex in enumerate(vertices):

            x = vertex[0]
            y = vertex[1]
            z = vertex[2]
            shape_key.data[num_vertex].co = (x, y, z)

    mesh_object.data.shape_keys.use_relative = False

    for num_frame in range(num_frames):

        mesh_object.data.shape_keys.eval_time = 10.0 * num_frame
        mesh_object.data.shape_keys. \
            keyframe_insert('eval_time', frame = num_frame)

    mesh_object.data.update()


class Arrow:
    """Arrows represent tags.
    """

    @staticmethod
    def read(arrow_object, armature_object):
        """Read arrow object to mdi.

        Args:

            arrow_object
            armature_object
        """

        if not arrow_object.type == 'EMPTY' or \
            not arrow_object.empty_display_type == 'ARROWS':
            return None  # TODO return type check

        mdi_tag = None

        is_free_tag = False
        is_bone_tag = False
        is_bone_tag_off = False

        matrix_identity = mathutils.Matrix.Identity(4)

        for constraint in arrow_object.constraints:

            if constraint.type == 'CHILD_OF' and \
                constraint.target == armature_object:

                # use_location_x
                # use_location_y
                # use_location_z
                # use_rotation_x
                # use_rotation_y
                # use_rotation_z
                # use_scale_x
                # use_scale_y
                # use_scale_z
                # TODO attempted to status message

                if arrow_object.matrix_basis == matrix_identity:
                    is_bone_tag = True
                else:
                    is_bone_tag_off = True

        if not (is_bone_tag or is_bone_tag_off):

            is_free_tag = True

        if is_free_tag:

            mdi_tag = mdi.MDIFreeTag()

            mdi_tag.name = arrow_object.name

            # check if fcurves available
            data_path_loc = 'location'
            data_path_rot = 'rotation_quaternion'

            action = arrow_object.animation_data.action

            fcurve_loc_x = action.fcurves.find(data_path_loc, index=0)
            fcurve_loc_y = action.fcurves.find(data_path_loc, index=1)
            fcurve_loc_z = action.fcurves.find(data_path_loc, index=2)

            fcurve_quaternion_w = \
                action.fcurves.find(data_path_rot, index=0)
            fcurve_quaternion_x = \
                action.fcurves.find(data_path_rot, index=1)
            fcurve_quaternion_y = \
                action.fcurves.find(data_path_rot, index=2)
            fcurve_quaternion_z = \
                action.fcurves.find(data_path_rot, index=3)

            frame_start = bpy.context.scene.frame_start
            frame_end = bpy.context.scene.frame_end

            for num_frame in range(frame_start, frame_end + 1):

                x = fcurve_loc_x.evaluate(num_frame)
                y = fcurve_loc_y.evaluate(num_frame)
                z = fcurve_loc_z.evaluate(num_frame)

                qw = fcurve_quaternion_w.evaluate(num_frame)
                qx = fcurve_quaternion_x.evaluate(num_frame)
                qy = fcurve_quaternion_y.evaluate(num_frame)
                qz = fcurve_quaternion_z.evaluate(num_frame)

                location = mathutils.Vector((x, y, z))
                orientation = mathutils.Quaternion((qw, qx, qy, qz))
                orientation = orientation.to_matrix()

                mdi_tag.locations.append(location)
                mdi_tag.orientations.append(orientation)

        if is_bone_tag:

            mdi_tag = mdi.MDIBoneTag()

            mdi_tag.name = arrow_object.name
            bone_name = arrow_object.constraints['Child Of'].subtarget
            mdi_tag.parent_bone = armature_object.data.bones.find(bone_name)

            mdi_tag.torso_weight = 0.0  # TODO

        if is_bone_tag_off:

            mdi_tag = mdi.MDIBoneTagOff()

            mdi_tag.name = arrow_object.name
            bone_name = arrow_object.constraints['Child Of'].subtarget
            mdi_tag.parent_bone = armature_object.data.bones.find(bone_name)

            mdi_tag.location = arrow_object.location
            mdi_tag.orientation = arrow_object.rotation_quaternion.to_matrix()

        return mdi_tag

    @staticmethod
    def write(mdi_model, num_tag, collection, armature_object = None):
        """Write mdi tag to scene.

        Args:

            mdi_model
            num_tag
            collection
            armature_object
        """

        mdi_tag = mdi_model.tags[num_tag]

        empty_object = None

        if isinstance(mdi_tag, mdi.MDIFreeTag):

            empty_object = bpy.data.objects.new("empty", None)
            collection.objects.link(empty_object)
            empty_object.name = mdi_tag.name
            empty_object.empty_display_type = 'ARROWS'
            empty_object.rotation_mode = 'QUATERNION'

            root_frame_location = mdi_tag.locations[mdi_model.root_frame]
            root_frame_orientation = mdi_tag.orientations[mdi_model.root_frame]

            matrix = mathutils.Matrix.Identity(4)
            matrix.translation = root_frame_location
            matrix = matrix @ root_frame_orientation.to_4x4()
            empty_object.matrix_world = matrix

            # animate
            for num_frame in range(len(mdi_tag.locations)):

                frame_location = mdi_tag.locations[num_frame]
                frame_orientation = mdi_tag.orientations[num_frame]

                matrix = mathutils.Matrix.Identity(4)
                matrix.translation = frame_location
                matrix = matrix @ frame_orientation.to_4x4()
                empty_object.matrix_world = matrix

                empty_object.keyframe_insert('location', \
                                            frame=num_frame, \
                                            group='LocRot')
                empty_object.keyframe_insert('rotation_quaternion', \
                                            frame=num_frame, \
                                            group='LocRot')

        elif isinstance(mdi_tag, mdi.MDIBoneTag):

            mdi_bones = mdi_model.skeleton.bones
            parent_bone_name = mdi_bones[mdi_tag.parent_bone].name

            empty_object = bpy.data.objects.new("empty", None)
            collection.objects.link(empty_object)
            empty_object.name = mdi_tag.name
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

            empty_object['Torso Weight'] = mdi_tag.torso_weight

        elif isinstance(mdi_tag, mdi.MDIBoneTagOff):

            mdi_bones = mdi_model.skeleton.bones
            mdi_parent_bone = mdi_bones[mdi_tag.parent_bone]

            empty_object = bpy.data.objects.new("empty", None)
            collection.objects.link(empty_object)
            empty_object.name = mdi_tag.name
            empty_object.empty_display_type = 'ARROWS'
            empty_object.rotation_mode = 'QUATERNION'

            empty_object.constraints.new(type="CHILD_OF")
            empty_object.constraints["Child Of"].target = armature_object
            empty_object.constraints["Child Of"].subtarget = mdi_parent_bone.name

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
            matrix.translation = mdi_tag.location
            orientation = mdi_tag.orientation
            empty_object.matrix_world = matrix @ orientation.to_4x4()

        else:

            pass

        return empty_object


class UVMap:
    """UV map.

    Attributes:

        TODO
    """

    @staticmethod
    def read(mesh_object):
        """Read UV map.

        Args:

            TODO
        """

        if len(mesh_object.data.uv_layers) > 1:
            pass # TODO

        uv_layer = mesh_object.data.uv_layers.active

        if uv_layer == None:
            return None # TODO

        # read in all data into tmp_uvs
        tmp_uvs = []
        for _ in range(len(mesh_object.data.vertices)):
            tmp_uvs.append([])

        for polygon in mesh_object.data.polygons:

            for loop_index in polygon.loop_indices:

                loop = mesh_object.data.loops[loop_index]

                loop_index = uv_layer.data[loop.index]
                vertex_index = loop.vertex_index
                uv_coordinates = uv_layer.data[loop.index].uv

                tmp_uvs[vertex_index].append(uv_coordinates)

        # check if data is bijective
        uv_map_is_bijective = True
        for vertex_index, vertex_mappings in enumerate(tmp_uvs):

            if len(vertex_mappings) == 0:
                uv_map_is_bijective = False
                break

            sample_mapping = vertex_mappings[0]
            for mapping in vertex_mappings:
                if mapping != sample_mapping:
                    uv_map_is_bijective = False

        if uv_map_is_bijective:

            mdi_uv_map = mdi.MDIUVMapBijective()

            for uv in tmp_uvs:

                u = uv[0][0]
                v = uv[0][1]
                mdi_uv = mdi.MDIUV(u, v)
                mdi_uv_map.uvs.append(mdi_uv)

        else:

            mdi_uv_map = mdi.MDIUVMapSurjective()

        return mdi_uv_map

    @staticmethod
    def write(mdi_uv_map, mesh_object):
        """Write UV map.

        Args:

            mdi_uv_map
            mesh_object
        """

        if isinstance(mdi_uv_map, mdi.MDIUVMapSurjective):

            pass  # TODO

        elif isinstance(mdi_uv_map, mdi.MDIUVMapBijective):

            mesh_object.data.uv_layers.new(name="UVMap")

            for polygon in mesh_object.data.polygons:

                for loop_index in \
                    range(polygon.loop_start,
                          polygon.loop_start + polygon.loop_total):

                    vertex_index = \
                        mesh_object.data.loops[loop_index].vertex_index

                    mesh_object.data.uv_layers['UVMap'].data[loop_index].uv = \
                        (mdi_uv_map.uvs[vertex_index].u,
                         mdi_uv_map.uvs[vertex_index].v)

        else:

            pass  # TODO


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
    """Materials represent shaders.

    Attributes:

        TODO
    """

    @staticmethod
    def _add_material_name(name, mesh_object):

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
    def write(mdi_shader, mesh_object):
        """TODO

        Args:

            TODO
        """

        if isinstance(mdi_shader, mdi.MDIShaderPaths):

            for mdi_shader_path in mdi_shader.paths:

                name = mdi_shader_path.path
                Materials._add_material_name(name, mesh_object)

        elif isinstance(mdi_shader, mdi.MDIShaderPath):

            name = mdi_shader.path
            Materials._add_material_name(name, mesh_object)

        else:

            pass  # TODO

class Mesh:
    """Mesh.
    """

    # TODO
    # read_rigged_vertices
    # read_morph_vertices
    # write_morph_vertices
    # write_vertex_weights

    @staticmethod
    def _read_morph(mesh_object, root_frame = 0):

        mdi_surface = mdi.MDISurface()

        mdi_surface.name = mesh_object.name

        # vertices
        bpy.context.view_layer.objects.active = mesh_object
        bpy.ops.object.modifier_add(type='TRIANGULATE')

        shape_key = mesh_object.data.shape_keys

        # TODO if not absolute
        # TODO check retime
        # TODO check if its just a single frame

        # TODO bei data_block check if .frame == eval_1

        action = shape_key.animation_data.action
        data_path_eval_time = "eval_time"
        fcurve_eval_time = action.fcurves.find(data_path_eval_time)

        try:
            num_vertices = len(shape_key.key_blocks[0].data)
            for _ in range(num_vertices):
                mdi_morph_vertex = mdi.MDIMorphVertex()
                mdi_surface.vertices.append(mdi_morph_vertex)
        except:
            pass # TODO get them from the mesh since its not animated

        frame_start = bpy.context.scene.frame_start
        frame_end = bpy.context.scene.frame_end

        for num_frame in range(frame_start, frame_end + 1):

            eval_time_value = fcurve_eval_time.evaluate(num_frame)

            # calculate how much of shape key 1 is added to shape key 2
            eval_1 = eval_time_value - (eval_time_value % 10)
            eval_2 = eval_1 + 10

            matrix = mathutils.Matrix.Identity(2)
            matrix[0] = 1, 1
            matrix[1] = eval_1, eval_2
            v = mathutils.Vector((1, eval_time_value))
            percent_v1_v2 = matrix.inverted() @ v

            try:

                num_block_1 = int(eval_time_value / 10)
                num_block_2 = num_block_1 + 1

                key_block_1 = shape_key.key_blocks[num_block_1]
                key_block_2 = shape_key.key_blocks[num_block_2]

                for num_vertex in range(num_vertices):

                    # TODO normals
                    # TODO range check
                    # num_blocks = len(shape_key.key_blocks)
                    location_1 = key_block_1.data[num_vertex].co
                    location_2 = key_block_2.data[num_vertex].co

                    location = percent_v1_v2[0] * location_1 \
                             + percent_v1_v2[1] * location_2

                    mdi_surface.vertices[num_vertex].locations.append(location)

                    normal = mathutils.Vector((0, 0, 1))  # TODO
                    mdi_surface.vertices[num_vertex].normals.append(normal)

            except: # eval time can't go below 0, so just get the last entry

                key_block = shape_key.key_blocks[-1]

                for num_vertex in range(num_vertices):

                    location = key_block.data[num_vertex].co

                    mdi_surface.vertices[num_vertex].locations.append(location)

                    normal = mathutils.Vector((0, 0, 1))  # TODO
                    mdi_surface.vertices[num_vertex].normals.append(normal)

        # triangles
        for triangle in mesh_object.data.polygons:

            indices = []
            for index in triangle.vertices:
                indices.append(index)

            mdi_triangle = mdi.MDITriangle(indices)
            mdi_surface.triangles.append(mdi_triangle)

        # shader
        # TODO check if available
        # TODO find out if shader paths or path
        mdi_shader_path = \
            mdi.MDIShaderPath(mesh_object.data.materials[0].name)
        mdi_surface.shader = mdi_shader_path

        # uv map
        mdi_surface.uv_map = UVMap.read(mesh_object)

        mesh_object.modifiers.remove(mesh_object.modifiers.get("Triangulate"))

        return mdi_surface

    @staticmethod
    def _read_skeletal(mesh_object, armature_object, root_frame):

        mdi_surface = mdi.MDISurface()

        mdi_surface.name = mesh_object.name

        # vertices
        bpy.context.view_layer.objects.active = mesh_object
        bpy.ops.object.modifier_add(type='TRIANGULATE')

        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='EDIT')

        bind_pose_bones = \
            [edit_bone.matrix \
            for edit_bone in armature_object.data.edit_bones]

        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.view_layer.objects.active = mesh_object

        bind_pose_vertices = \
            [mesh_object.matrix_world @ vertex.co \
            for vertex in mesh_object.data.vertices]

        for vertex_index in range(0, len(mesh_object.data.vertices)):

            mdi_rigged_vertex = mdi.MDIRiggedVertex()

            normal = \
                mesh_object.matrix_world @ \
                mesh_object.data.vertices[vertex_index].normal
            mdi_rigged_vertex.normal = normal.normalized()

            for vertex_group in mesh_object.vertex_groups:

                bone_name = vertex_group.name

                weight_value = None
                try:
                    weight_value = \
                        mesh_object.vertex_groups[bone_name]. \
                        weight(vertex_index)
                except:
                    pass

                if weight_value != None:

                    bone_index = armature_object.data.bones.find(bone_name)

                    # location
                    loc, ori, _ = bind_pose_bones[bone_index].decompose()
                    bone_bind_pose_location = loc
                    bone_bind_pose_orientation = ori.to_matrix().to_3x3()

                    location = bone_bind_pose_orientation.transposed() @ \
                               (bind_pose_vertices[vertex_index] - \
                                bone_bind_pose_location)

                    mdi_weight = mdi.MDIVertexWeight(bone_index, weight_value,
                                                     location)
                    mdi_rigged_vertex.weights.append(mdi_weight)

            mdi_surface.vertices.append(mdi_rigged_vertex)

        # triangles
        for triangle in mesh_object.data.polygons:

            indices = []
            for index in triangle.vertices:
                indices.append(index)

            mdi_triangle = mdi.MDITriangle(indices)
            mdi_surface.triangles.append(mdi_triangle)

        # shader
        # TODO check if available
        # TODO find out if shader paths or path
        mdi_shader_path = \
            mdi.MDIShaderPath(mesh_object.data.materials[0].name)
        mdi_surface.shader = mdi_shader_path

        # uv map
        mdi_surface.uv_map = UVMap.read(mesh_object)

        mesh_object.modifiers.remove(mesh_object.modifiers.get("Triangulate"))

        return mdi_surface

    @staticmethod
    def _skin_vertices(mdi_rigged_vertices, mdi_skeleton, mesh_object,
                       armature_object):

        mdi_bones = mdi_skeleton.bones
        vertex_groups_dict = {mdi_bone.name: [] for mdi_bone in mdi_bones}

        for vertex_index, mdi_rigged_vertex in enumerate(mdi_rigged_vertices):

            for mdi_vertex_weight in mdi_rigged_vertex.weights:

                bone_name = mdi_bones[mdi_vertex_weight.parent_bone].name
                weights = (vertex_index, mdi_vertex_weight.weight_value)
                vertex_groups_dict[bone_name].append(weights)

        for bone_name, weights in vertex_groups_dict.items():

            vertex_group = mesh_object.vertex_groups.new(name = bone_name)

            for vertex_index, weight in weights:

                vertex_group.add([vertex_index], weight, 'REPLACE')

        modifier = mesh_object.modifiers.new('Armature', 'ARMATURE')
        modifier.object = armature_object
        modifier.use_bone_envelopes = False
        modifier.use_vertex_groups = True

    @staticmethod
    def _morph_vertices(mdi_morph_vertices, mesh_object, root_frame):

        for mdi_morph_vertex in mdi_morph_vertices:

            for num_frame in range(len(mdi_morph_vertex.locations)):

                shape_key = mesh_object.shape_key_add(name="Frame",
                                                      from_mix=False)

                for num_vertex, mdi_morph_vertex in \
                    enumerate(mdi_morph_vertices):

                    x = mdi_morph_vertex.locations[num_frame][0]
                    y = mdi_morph_vertex.locations[num_frame][1]
                    z = mdi_morph_vertex.locations[num_frame][2]
                    shape_key.data[num_vertex].co = (x, y, z)

            break

        if mesh_object.data.shape_keys:

            mesh_object.data.shape_keys.use_relative = False
            mesh_object.active_shape_key_index = root_frame

            num_frames = len(mdi_morph_vertices[0].locations)
            for num_frame in range(num_frames):

                mesh_object.data.shape_keys.eval_time = 10.0 * num_frame
                mesh_object.data.shape_keys. \
                    keyframe_insert('eval_time', frame = num_frame)

        mesh_object.data.update()

    @staticmethod
    def _create_mesh(mdi_model, num_surface, collection):

        mdi_surface = mdi_model.surfaces[num_surface]

        name = mdi_surface.name
        mesh = bpy.data.meshes.new(name)
        mesh_object = bpy.data.objects.new(name, mesh)

        mdi_vertices = mdi_surface.vertices
        mdi_triangles = mdi_surface.triangles

        root_frame = mdi_model.root_frame
        vertex_locations = []
        for mdi_vertex in mdi_vertices:

            if isinstance(mdi_vertex, mdi.MDIRiggedVertex):

                location, _ = \
                    mdi_vertex.calc_model_space_coords(mdi_model.skeleton,
                                                       root_frame)
                vertex_locations.append(location)

            elif isinstance(mdi_vertex, mdi.MDIMorphVertex):

                location = mdi_vertex.locations[root_frame]
                vertex_locations.append(location)

            else:

                vertex_locations = []
                break  # TODO

        triangles = [mdi_triangle.indices for mdi_triangle in mdi_triangles]

        mesh.from_pydata(vertex_locations, [], triangles)
        mesh.update()
        mesh.validate(verbose=True)

        collection.objects.link(mesh_object)

        return mesh_object

    @staticmethod
    def read(mesh_object, armature_object = None, root_frame = 0):
        """TODO

        Args:

            TODO
        """

        # find out what type of mesh it is (skeletal vs morph mesh)
        # mdi supports both at once, that means the vertex list can contain
        # both types, the method used here is different in that it supports
        # only 1 type in the vertex list => TODO find a better method

        # morph mesh
        if mesh_object.data.shape_keys:  # TODO

            mdi_surface = Mesh._read_morph(mesh_object, root_frame)

        # skeletal mesh
        else:

            mdi_surface = Mesh._read_skeletal(mesh_object, armature_object,
                                            root_frame)

        return mdi_surface

    @staticmethod
    def write(mdi_model, num_surface, collection, armature_object = None):
        """TODO

        Args:

            TODO
        """

        mdi_surface = mdi_model.surfaces[num_surface]

        # create vertices
        mesh_object = Mesh._create_mesh(mdi_model, num_surface, collection)

        # animate vertices
        mdi_first_vertex = None
        if  mdi_surface.vertices:
            mdi_first_vertex =  mdi_surface.vertices[0]

        if isinstance(mdi_first_vertex, mdi.MDIRiggedVertex):

            Mesh._skin_vertices(mdi_surface.vertices,
                                mdi_model.skeleton,
                                mesh_object,
                                armature_object)

        elif isinstance(mdi_first_vertex, mdi.MDIMorphVertex):

            Mesh._morph_vertices(mdi_surface.vertices,
                                 mesh_object,
                                 mdi_model.root_frame)

        else:

            pass  # TODO

        # shaders
        Materials.write(mdi_surface.shader, mesh_object)

        # uv map
        UVMap.write(mdi_surface.uv_map, mesh_object)

        return mesh_object


class Armature:
    """Armature.
    """

    @staticmethod
    def _set_constraints(mdi_model, armature_object):
        """TODO
        """

        mdi_bones = mdi_model.skeleton.bones

        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='POSE')

        for mdi_bone in mdi_bones:

            mdi_bone_parent_name = mdi_bones[mdi_bone.parent_bone].name

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
    def _animate_bones(mdi_model, armature_object):
        """TODO
        """

        mdi_bones = mdi_model.skeleton.bones
        bind_pose_frame = mdi_model.root_frame

        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='POSE')

        armature_object.animation_data_create()
        armature_object.animation_data.action = \
            bpy.data.actions.new(name=armature_object.name)

        # prepare fcurves
        for mdi_bone in mdi_bones:

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

            frame_len = len(mdi_bone.locations)

            fcurve_loc_x.keyframe_points.add(count=frame_len)
            fcurve_loc_z.keyframe_points.add(count=frame_len)
            fcurve_loc_y.keyframe_points.add(count=frame_len)

            fcurve_quaternion_w.keyframe_points.add(count=frame_len)
            fcurve_quaternion_x.keyframe_points.add(count=frame_len)
            fcurve_quaternion_z.keyframe_points.add(count=frame_len)
            fcurve_quaternion_y.keyframe_points.add(count=frame_len)

            # animate
            for num_frame in range(0, frame_len):

                # c = child, p = parent
                # b = bind frame, f = current frame
                # l = location, o = orientation
                # _ms = model space, _ps = parent space
                cbl_ms = mdi_bone.locations[bind_pose_frame]
                cbo_ms = mdi_bone.orientations[bind_pose_frame]
                cfl_ms = mdi_bone.locations[num_frame]
                cfo_ms = mdi_bone.orientations[num_frame]

                if mdi_bone.parent_bone >= 0:

                    mdi_parent_bone = mdi_bones[mdi_bone.parent_bone]

                    pbl_ms = mdi_parent_bone.locations[bind_pose_frame]
                    pbo_ms = mdi_parent_bone.orientations[bind_pose_frame]
                    pfl_ms = mdi_parent_bone.locations[num_frame]
                    pfo_ms = mdi_parent_bone.orientations[num_frame]

                    # blenders bone animations (as we defined them in our
                    # settings) are relative to its bind pose space, the bind
                    # pose space is nested within parent space, so we need to
                    # transform our data which is given in model space

                    # express the childs bind pose in parent space
                    cbl_ps = pbo_ms.transposed() @ (cbl_ms - pbl_ms)
                    cbo_ps = pbo_ms.transposed() @ cbo_ms

                    # calculate the model space coordinates of the child in
                    # blenders bind pose
                    cbl_dash_ms = pfl_ms + pfo_ms @ cbl_ps
                    cbo_dash_ms = pfo_ms @ cbo_ps

                    # offset from blenders bind pose to our wished model space
                    # values
                    location_off = cbo_dash_ms.transposed() @ \
                        (cfl_ms - cbl_dash_ms)
                    orientation_off = cbo_dash_ms.transposed() @ cfo_ms

                else:

                    location_off = cbo_ms.transposed() @ (cfl_ms - cbl_ms)
                    orientation_off = cbo_ms.transposed() @ cfo_ms

                orientation_off = orientation_off.to_quaternion()

                fcurve_loc_x.keyframe_points[num_frame].co = \
                    num_frame, location_off.x
                fcurve_loc_y.keyframe_points[num_frame].co = \
                    num_frame, location_off.y
                fcurve_loc_z.keyframe_points[num_frame].co = \
                    num_frame, location_off.z

                fcurve_quaternion_w.keyframe_points[num_frame].co = \
                    num_frame, orientation_off.w
                fcurve_quaternion_x.keyframe_points[num_frame].co = \
                    num_frame, orientation_off.x
                fcurve_quaternion_y.keyframe_points[num_frame].co = \
                    num_frame, orientation_off.y
                fcurve_quaternion_z.keyframe_points[num_frame].co = \
                    num_frame, orientation_off.z

        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def _add_edit_bones(mdi_model, armature_object):
        """TODO
        """

        mdi_skeleton = mdi_model.skeleton
        bind_pose_frame = mdi_model.root_frame

        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='EDIT')

        for num_bone, mdi_bone in enumerate(mdi_skeleton.bones):

            edit_bone = armature_object.data.edit_bones.new(mdi_bone.name)

            edit_bone.head = (0, 0, 0)
            edit_bone.tail = (0, 1, 0)
            edit_bone.use_connect = False
            edit_bone.use_inherit_scale = True
            edit_bone.use_local_location = True
            edit_bone.use_inherit_rotation = True

            bind_pose_location = mdi_bone.locations[bind_pose_frame]
            bind_pose_orientation = mdi_bone.orientations[bind_pose_frame]

            bind_pose_matrix = \
                mathutils.Matrix.Translation(bind_pose_location) @ \
                    bind_pose_orientation.to_4x4()
            edit_bone.matrix = bind_pose_matrix

            edit_bone['Torso Weight'] = mdi_bone.torso_weight

            if num_bone == mdi_skeleton.torso_parent_bone:

                edit_bone['Torso Parent'] = True

        # set parent-child-relationship
        for mdi_bone in mdi_skeleton.bones:

            if mdi_bone.parent_bone >= 0:

                mdi_bone_parent = mdi_skeleton.bones[mdi_bone.parent_bone]

                child = armature_object.data.edit_bones[mdi_bone.name]
                parent = armature_object.data.edit_bones[mdi_bone_parent.name]
                child.parent = parent

        bpy.ops.object.mode_set(mode='OBJECT')

    @staticmethod
    def _create_armature(mdi_model, collection):
        """TODO
        """

        name = mdi_model.skeleton.name

        armature = bpy.data.armatures.new(name)
        armature_object = bpy.data.objects.new(name, armature)

        collection.objects.link(armature_object)

        return armature_object

    @staticmethod
    def read(armature_object):
        """TODO

        Args:

            TODO
        """

        if not armature_object:
            return None

        mdi_skeleton = mdi.MDISkeleton()

        mdi_skeleton.name = armature_object.name
        mdi_skeleton.torso_parent_bone = 0  # calculated later

        # bones
        bpy.context.view_layer.objects.active = \
            bpy.data.objects[armature_object.name]
        bpy.ops.object.mode_set(mode='EDIT')

        # extract and tmp store all bones bind pose locations and orientations
        # for faster access
        bind_pose_locations = []
        bind_pose_orientations = []
        for edit_bone in armature_object.data.edit_bones:

            bl_ms, bo_ms, _ = edit_bone.matrix.decompose()
            bo_ms = bo_ms.to_matrix()

            bind_pose_locations.append(bl_ms)
            bind_pose_orientations.append(bo_ms)

        # create the mdi bones
        frame_start = bpy.context.scene.frame_start
        frame_end = bpy.context.scene.frame_end

        for num_bone, edit_bone in enumerate(armature_object.data.edit_bones):

            cbl_ms = bind_pose_locations[num_bone]
            cbo_ms = bind_pose_orientations[num_bone]

            mdi_bone = mdi.MDIBone()

            mdi_bone.name = edit_bone.name

            parent_index = -1
            if edit_bone.parent:
                parent_index = \
                    armature_object.data.edit_bones.find(edit_bone.parent.name)
            mdi_bone.parent_bone = parent_index

            # parent_dist
            if parent_index >= 0:

                pbl_ms = bind_pose_locations[parent_index]
                mdi_bone.parent_dist = (cbl_ms - pbl_ms).length

            else:  # root bone

                cbl_ms = bind_pose_locations[num_bone]
                mdi_bone.parent_dist = cbl_ms.length

            # torso_weight
            torso_weight = 0.0
            try:
                torso_weight = edit_bone['Torso Weight']
            except:
                pass  # TODO print warning
            mdi_bone.torso_weight = torso_weight

            # sneak in check for torso parent
            try:
                _ = edit_bone['Torso Parent']
                mdi_skeleton.torso_parent_bone = num_bone
            except:
                pass  # TODO print warning

            # extract the location and orientation offsets from the fcurves
            data_path_loc = \
                'pose.bones["{}"].location'.format(mdi_bone.name)
            data_path_rot = \
                'pose.bones["{}"].rotation_quaternion'.format(mdi_bone.name)

            action = armature_object.animation_data.action

            fcurve_loc_x = action.fcurves.find(data_path_loc, index=0)
            fcurve_loc_y = action.fcurves.find(data_path_loc, index=1)
            fcurve_loc_z = action.fcurves.find(data_path_loc, index=2)

            fcurve_quaternion_w = \
                action.fcurves.find(data_path_rot, index=0)
            fcurve_quaternion_x = \
                action.fcurves.find(data_path_rot, index=1)
            fcurve_quaternion_y = \
                action.fcurves.find(data_path_rot, index=2)
            fcurve_quaternion_z = \
                action.fcurves.find(data_path_rot, index=3)

            tmp_loc_rots = []
            for num_frame in range(frame_start, frame_end + 1):

                x = fcurve_loc_x.evaluate(num_frame)
                y = fcurve_loc_y.evaluate(num_frame)
                z = fcurve_loc_z.evaluate(num_frame)

                qw = fcurve_quaternion_w.evaluate(num_frame)
                qx = fcurve_quaternion_x.evaluate(num_frame)
                qy = fcurve_quaternion_y.evaluate(num_frame)
                qz = fcurve_quaternion_z.evaluate(num_frame)

                location_off = mathutils.Vector((x, y, z))
                orientation_off = mathutils.Quaternion((qw, qx, qy, qz))
                orientation_off = orientation_off.to_matrix()

                tmp_loc_rots.append((location_off, orientation_off))

            # calculate locations and orientations based on extracted offsets
            if mdi_bone.parent_bone >= 0:

                # use already calculated parent for faster access
                mdi_parent_bone = mdi_skeleton.bones[mdi_bone.parent_bone]

                pbl_ms = bind_pose_locations[mdi_bone.parent_bone]
                pbo_ms = bind_pose_orientations[mdi_bone.parent_bone]

                for num_frame, tmp_loc_rot in enumerate(tmp_loc_rots):

                    location_off, orientation_off = tmp_loc_rot

                    pfl_ms = mdi_parent_bone.locations[num_frame]
                    pfo_ms = mdi_parent_bone.orientations[num_frame]

                    # express the childs bind pose in parent space
                    cbl_ps = pbo_ms.transposed() @ (cbl_ms - pbl_ms)
                    cbo_ps = pbo_ms.transposed() @ cbo_ms

                    # calculate the model space coordinates of the child in
                    # blenders bind pose
                    cbl_dash_ms = pfl_ms + pfo_ms @ cbl_ps
                    cbo_dash_ms = pfo_ms @ cbo_ps

                    # calculate model space values for frame
                    location = cbl_dash_ms + cbo_dash_ms @ location_off
                    orientation = cbo_dash_ms @ orientation_off

                    mdi_bone.locations.append(location)
                    mdi_bone.orientations.append(orientation)

            else:  # root bone

                for tmp_loc_rot in tmp_loc_rots:

                    location_off, orientation_off = tmp_loc_rot

                    location = cbl_ms + cbo_ms @ location_off
                    orientation = cbo_ms @ orientation_off

                    mdi_bone.locations.append(location)
                    mdi_bone.orientations.append(orientation)

            mdi_skeleton.bones.append(mdi_bone)

        bpy.ops.object.mode_set(mode='OBJECT')

        # root bone locations
        mdi_root_bone = mdi_skeleton.bones[0]
        for location in mdi_root_bone.locations:
            mdi_skeleton.root_bone_locations.append(location)

        return mdi_skeleton

    @staticmethod
    def write(mdi_model, collection):
        """TODO

        Args:

            TODO
        """

        if not mdi_model.skeleton:
            return None

        armature_object = Armature._create_armature(mdi_model, collection)

        Armature._add_edit_bones(mdi_model, armature_object)

        Armature._animate_bones(mdi_model, armature_object)

        Armature._set_constraints(mdi_model, armature_object)

        return armature_object


class Collection:
    """Collections represent a model.
    """

    @staticmethod
    def read(collapse_frame = 0):
        """TODO

        Args:

            TODO
        """

        mdi_model = mdi.MDI()

        active_collection = \
            bpy.context.view_layer.active_layer_collection.collection

        mdi_model.name = active_collection.name
        mdi_model.root_frame = 0  # TODO only used during import

        # collect all objects for export
        mesh_objects = []
        armature_objects = []
        arrow_objects = []
        for obj in active_collection.objects:

            if obj.type == 'MESH':
                mesh_objects.append(obj)

            elif obj.type == 'ARMATURE':
                armature_objects.append(obj)

            elif obj.type == 'EMPTY' and obj.empty_display_type == 'ARROWS':
                arrow_objects.append(obj)

        armature_object = None
        if armature_objects:

            if len(armature_objects) > 1:

                pass # TODO warning message

            armature_object = armature_objects[0]

        # mdi surfaces
        for mesh_object in mesh_objects:

            mdi_surface = Mesh.read(mesh_object, armature_object)

            if mdi_surface:
                mdi_model.surfaces.append(mdi_surface)

        # mdi skeleton
        mdi_model.skeleton = Armature.read(armature_object)

        # mdi tags
        for arrow_object in arrow_objects:

            mdi_tag = Arrow.read(arrow_object, armature_object)
            if mdi_tag:
                mdi_model.tags.append(mdi_tag)

        # mdi bounds
        mdi_model.bounds = mdi.MDIBoundingVolume.calc(mdi_model)

        # mdi lod
        mdi_model.lod = mdi.MDIDiscreteLOD()  # TODO

        return mdi_model

    @staticmethod
    def write(mdi_model):
        """TODO

        Args:

            TODO
        """

        collection = bpy.data.collections.new(mdi_model.name)
        bpy.context.scene.collection.children.link(collection)

        armature_object = Armature.write(mdi_model, collection)

        for num_surface in range(len(mdi_model.surfaces)):

            Mesh.write(mdi_model, num_surface, collection, armature_object)

        for num_tag in range(len(mdi_model.tags)):

            Arrow.write(mdi_model, num_tag, collection, armature_object)

        return collection


def test():

    pass

def read(collapse_frame = 0):

    # test()

    mdi_model = Collection.read(collapse_frame)

    # Collection.write(mdi_model)

    #draw_bounding_volume(mdi_model.bounds)

    return mdi_model

def write(mdi_model):

    collection = Collection.write(mdi_model)

    return collection
