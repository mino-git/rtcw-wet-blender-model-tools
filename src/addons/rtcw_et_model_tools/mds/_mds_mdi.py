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

"""Converts between in-memory representations of MDS and MDI.
"""

import mathutils

from rtcw_et_model_tools.mds import _mds as mds
from rtcw_et_model_tools.mdi import mdi as mdi
from rtcw_et_model_tools.mdi import mdi_util as mdi_util


class MDIToModel:

    @staticmethod
    def convert(mdi_model):

        mds_model = None
        return mds_model


class ModelToMDI:

    @staticmethod
    def _calc_socket(mds_model, num_tag):

        mds_tag = mds_model.tags[num_tag]

        p_name = mdi_util.c_string_to_utf_8_string(mds_tag.name)
        p_parent_skeleton = 0
        p_parent_bone = mds_tag.parent_bone
        p_torso_weight = mds_tag.torso_weight

        mdi_socket = \
            mdi.MDISocketParentBone(name = p_name,
                                    parent_skeleton = p_parent_skeleton,
                                    parent_bone = p_parent_bone,
                                    torso_weight = p_torso_weight)

        return mdi_socket

    @staticmethod
    def _calc_surface(mds_model, num_surface, mdi_skeleton):

        def calc_vertex_ln(mds_vertex, mdi_skeleton, bind_pose_frame):

            location = mathutils.Vector((0.0, 0.0, 0.0))

            for num_weight in range(0, len(mds_vertex.weights)):

                mds_weight = mds_vertex.weights[num_weight]

                mdi_bone = mdi_skeleton.bones.bone_list[mds_weight.bone_index]
                bone_location = \
                    mdi_bone.animation.frames[bind_pose_frame].location
                bone_rotation = \
                    mdi_bone.animation.frames[bind_pose_frame].orientation
                bone_weight = mds_weight.bone_weight
                location_offset = mathutils.Vector(mds_weight.location_offset)

                # to object space
                tmp = bone_rotation @ location_offset
                object_space_coords = bone_location + tmp

                # weight it against bone
                object_space_coords_weighted = \
                    object_space_coords * bone_weight

                location = location + object_space_coords_weighted

            normal = mathutils.Vector((0, 0, 1))

            return (location, normal)

        bind_pose_frame = 32  # TODO

        mdi_surface = mdi.MDISurface()

        mds_surface = mds_model.surfaces[num_surface]

        mdi_surface.name = \
            mdi_util.c_string_to_utf_8_string(mds_surface.header.name)

        # vertices
        vertex_list = mdi_surface.geometry.vertices.vertex_list

        for num_vertex in range(0, len(mds_surface.vertices)):

            mds_vertex = mds_surface.vertices[num_vertex]

            p_location, p_normal = \
                calc_vertex_ln(mds_vertex, mdi_skeleton, bind_pose_frame)

            mdi_vertex = mdi.MDIVertex(location = p_location,
                                       normal = p_normal)

            vertex_list.append(mdi_vertex)

            mdi_rigged_vertex = mdi.MDIRiggedVertex(parent_skeleton = 0)
            mdi_vertex.animation = mdi_rigged_vertex

            for mds_weight in mds_vertex.weights:

                p_parent_bone = mds_weight.bone_index
                p_weight = mds_weight.bone_weight

                mdi_weight = \
                    mdi.MDIVertexWeight(parent_bone = p_parent_bone,
                                        weight = p_weight)
                mdi_rigged_vertex.weights.append(mdi_weight)

        # triangles
        triangle_list = mdi_surface.geometry.triangles.triangle_list

        for mds_triangle in mds_surface.triangles:

            mdi_triangle = mdi.MDITriangle(mds_triangle.indices)
            triangle_list.append(mdi_triangle)

        # bounds
        mdi_surface.geometry.bounds = mdi.MDIBounds()
        mdi_bounds = mdi_surface.geometry.bounds
        mdi_bounds.animation = mdi.MDIBoundsAnimation()

        for num_frame in range(0, len(mds_model.frames)):

            mds_frame_info = mds_model.frames[num_frame].frame_info

            p_min_bound = mathutils.Vector(mds_frame_info.min_bound)
            p_max_bound = mathutils.Vector(mds_frame_info.max_bound)
            p_local_origin = mathutils.Vector(mds_frame_info.local_origin)
            p_radius = mds_frame_info.radius

            mdi_bounds_in_frame = mdi.MDIBoundsInFrame(min_bound = p_min_bound,
                                                       max_bound = p_max_bound,
                                                       local_origin = p_local_origin,
                                                       radius = p_radius)
            mdi_bounds.animation.frames.append(mdi_bounds_in_frame)

            if num_frame == bind_pose_frame:

                mdi_bounds.min_bound = p_min_bound
                mdi_bounds.max_bound = p_max_bound
                mdi_bounds.local_origin = p_local_origin
                mdi_bounds.radius = p_radius

        # shaders
        reference = \
            mdi_util.c_string_to_utf_8_string(mds_surface.header.shader)
        mdi_surface.color.shader_data = mdi.MDIShaderReference(reference)

        # uv_map
        mdi_surface.color.uv_map = mdi.MDIUVMapBijective()

        for num_vertex in range(0, len(mds_surface.vertices)):

            mds_vertex = mds_surface.vertices[num_vertex]

            mdi_tex_coords = mdi.MDITexCoords(u = mds_vertex.tex_coords[0],
                                              v = 1 - mds_vertex.tex_coords[1])

            mdi_surface.color.uv_map.tex_coords_list.append(mdi_tex_coords)

        # lod
        p_min_lod = mds_surface.header.min_lod
        p_mappings = mds_surface.collapse_map.mappings
        mdi_surface.lod = \
            mdi.MDILODCollapseMap(min_lod = p_min_lod, mappings = p_mappings)

        return mdi_surface

    @staticmethod
    def _calc_skeleton(mds_model):

        def calc_bone_location(mds_model, mdi_skeleton, num_bone, num_frame):

            location = None

            if num_bone != 0:

                mds_bone_info = mds_model.bone_infos[num_bone]
                mdi_bone_parent = \
                    mdi_skeleton.bones.bone_list[mds_bone_info.parent_bone]

                # location_dir
                mds_bone_frame_compressed = \
                    mds_model.frames[num_frame].bone_frames_compressed[num_bone]

                yaw = mds_bone_frame_compressed.location_dir[1]
                pitch = mds_bone_frame_compressed.location_dir[0]

                location_dir = mdi_util.offAnglesToOffset(yaw, pitch)

                # parent_dist
                parent_dist = mds_bone_info.parent_dist

                # parent_location
                parent_location = \
                    mdi_bone_parent.animation.frames[num_frame].location

                location = parent_location + (parent_dist * location_dir)

            else:  # root bone

                mds_frame_info = mds_model.frames[num_frame].frame_info

                location = mathutils.Vector(mds_frame_info.root_bone_location)

            return location

        def calc_bone_orientation(mds_model, mdi_skeleton, num_bone,
                                  num_frame):

            mds_bone_frame_compressed = \
                mds_model.frames[num_frame].bone_frames_compressed[num_bone]

            yaw = mds_bone_frame_compressed.orientation[1]
            pitch = mds_bone_frame_compressed.orientation[0]
            roll = mds_bone_frame_compressed.orientation[2]

            orientation = mdi_util.anglesToMatrix(yaw, pitch, roll)

            return orientation

        bind_pose_frame = 32  # TODO

        mdi_skeleton = mdi.MDISkeleton()

        mdi_skeleton.name = "skeleton"

        mdi_skeleton.bones.torso_parent_bone = \
            mds_model.header.torso_parent_bone

        for num_bone in range(0, len(mds_model.bone_infos)):

            mds_bone = mds_model.bone_infos[num_bone]

            p_name = mdi_util.c_string_to_utf_8_string(mds_bone.name)
            p_parent_bone = mds_bone.parent_bone
            p_parent_dist = mds_bone.parent_dist
            p_torso_weight = mds_bone.torso_weight
            p_flags = mds_bone.flags
            p_location = calc_bone_location(mds_model, mdi_skeleton, num_bone,
                                            bind_pose_frame)
            p_orientation = calc_bone_orientation(mds_model, mdi_skeleton,
                                                  num_bone, bind_pose_frame)

            mdi_bone = mdi.MDIBone(name = p_name, parent_bone = p_parent_bone,
                                   parent_dist = p_parent_dist,
                                   torso_weight = p_torso_weight,
                                   flags = p_flags, location = p_location,
                                   orientation = p_orientation)

            mdi_skeleton.bones.bone_list.append(mdi_bone)

            # animation
            for num_frame in range(0, len(mds_model.frames)):

                p_location = \
                    calc_bone_location(mds_model, mdi_skeleton, num_bone,
                                          num_frame)
                p_orientation = \
                    calc_bone_orientation(mds_model, mdi_skeleton, num_bone,
                                          num_frame)

                mdi_bone_in_frame = \
                    mdi.MDIBoneInFrame(location = p_location,
                                       orientation = p_orientation)
                mdi_bone.animation.frames.append(mdi_bone_in_frame)

        return mdi_skeleton

    @staticmethod
    def convert(mds_model):

        mdi_model = mdi.MDI()

        mdi_model.name = \
            mdi_util.c_string_to_utf_8_string(mds_model.header.name)
        mdi_model.lod_scale = mds_model.header.lod_scale
        mdi_model.lod_bias = mds_model.header.lod_bias

        # skeleton
        mdi_skeleton = ModelToMDI._calc_skeleton(mds_model)
        mdi_model.skeletons.skeleton_list.append(mdi_skeleton)

        # surfaces
        for num_surface in range(0, len(mds_model.surfaces)):

            mdi_surface = \
                ModelToMDI._calc_surface(mds_model, num_surface, mdi_skeleton)
            mdi_model.surfaces.surface_list.append(mdi_surface)

        # sockets
        for num_tag in range(0, len(mds_model.tags)):

            mdi_socket = ModelToMDI._calc_socket(mds_model, num_tag)
            mdi_model.sockets.socket_list.append(mdi_socket)

        return mdi_model
