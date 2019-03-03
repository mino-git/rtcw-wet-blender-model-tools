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
    def _calc_socket(mds_tag):

        name = mdi_util.c_string_to_utf_8_string(mds_tag.name)
        parent_skeleton = 0
        parent_bone = mds_tag.parent_bone
        torso_weight = mds_tag.torso_weight

        mdi_socket = mdi.MDISocketParentBone(name, parent_skeleton, parent_bone,
                                             torso_weight)

        return mdi_socket

    @staticmethod
    def _calc_surface(mds_surface, mds_frames, mdi_skeleton,
                      bind_pose_frame = 0):

        def calc_vertex_weighted(mdm_vertex, mdi_skeleton):

            location_weighted = mathutils.Vector((0.0, 0.0, 0.0))
            orientation_weighted = mathutils.Matrix.Identity(3)

            for mds_weight in mds_vertex.weights:

                mdi_bone = mdi_skeleton.bones.bone_list[mds_weight.bone_index]

                bone_weight = mds_weight.bone_weight
                location = mathutils.Vector(mds_weight.location)

                # to object space
                tmp = mdi_bone.orientation @ location
                object_space_coords = mdi_bone.location + tmp

                # weight it against bone
                object_space_coords_weighted = \
                    object_space_coords * bone_weight

                location_weighted += object_space_coords_weighted

                orientation_weighted += mdi_bone.orientation * bone_weight

            normal = mathutils.Vector(mds_vertex.normal)
            normal_weighted = orientation_weighted @ normal

            return (location_weighted, normal_weighted)

        mdi_surface = mdi.MDISurface()

        mdi_surface.name = \
            mdi_util.c_string_to_utf_8_string(mds_surface.header.name)

        # vertex_list
        for mds_vertex in mds_surface.vertices:

            location, normal = calc_vertex_weighted(mds_vertex, mdi_skeleton)
            mdi_vertex = mdi.MDIVertex(location, normal)
            mdi_surface.geometry.vertices.vertex_list.append(mdi_vertex)

            # animation
            mdi_rigged_vertex = mdi.MDIRiggedVertex(parent_skeleton = 0)
            mdi_vertex.animation = mdi_rigged_vertex

            for mds_weight in mds_vertex.weights:

                parent_bone = mds_weight.bone_index
                weight = mds_weight.bone_weight

                mdi_weight = mdi.MDIVertexWeight(parent_bone, weight)
                mdi_rigged_vertex.weights.append(mdi_weight)

        # triangles
        for mds_triangle in mds_surface.triangles:

            mdi_triangle = mdi.MDITriangle(mds_triangle.indices)
            mdi_surface.geometry.triangles.triangle_list.append(mdi_triangle)

        # bounds
        mdi_surface.geometry.bounds = mdi.MDIBounds()
        mdi_bounds = mdi_surface.geometry.bounds
        mdi_bounds.animation = mdi.MDIBoundsAnimation()

        for num_frame, mds_frame in enumerate(mds_frames):

            mds_frame_info = mds_frame.frame_info

            min_bound = mathutils.Vector(mds_frame_info.min_bound)
            max_bound = mathutils.Vector(mds_frame_info.max_bound)
            local_origin = mathutils.Vector(mds_frame_info.local_origin)
            radius = mds_frame_info.radius

            mdi_bounds_in_frame = mdi.MDIBoundsInFrame(min_bound, max_bound,
                                                       local_origin, radius)
            mdi_bounds.animation.frames.append(mdi_bounds_in_frame)

            if num_frame == bind_pose_frame:

                mdi_bounds.min_bound = min_bound
                mdi_bounds.max_bound = max_bound
                mdi_bounds.local_origin = local_origin
                mdi_bounds.radius = radius

        # shaders
        reference = \
            mdi_util.c_string_to_utf_8_string(mds_surface.header.shader)
        mdi_surface.color.shader_data = mdi.MDIShaderReference(reference)

        # uv_map
        mdi_surface.color.uv_map = mdi.MDIUVMapBijective()

        for num_vertex in range(0, len(mds_surface.vertices)):

            mds_vertex = mds_surface.vertices[num_vertex]

            mdi_tex_coords = mdi.MDITexCoords(mds_vertex.tex_coords[0],
                                              1 - mds_vertex.tex_coords[1])
            mdi_surface.color.uv_map.tex_coords_list.append(mdi_tex_coords)

        # lod
        min_lod = mds_surface.header.min_lod
        mappings = mds_surface.collapse_map.mappings
        mdi_surface.lod = mdi.MDILODCollapseMap(min_lod, mappings)

        return mdi_surface

    @staticmethod
    def _calc_skeleton(mds_model, bind_pose_frame = 0):

        def calc_bone_location(mds_model, mdi_skeleton, num_bone, num_frame):

            if num_bone != 0:

                mds_bone_info = mds_model.bone_infos[num_bone]
                mdi_bone_parent = \
                    mdi_skeleton.bones.bone_list[mds_bone_info.parent_bone]

                # location_dir
                mds_bone_frame_compressed = \
                    mds_model.frames[num_frame].bone_frames_compressed[num_bone]

                yaw = mds_bone_frame_compressed.location_dir[1]
                pitch = mds_bone_frame_compressed.location_dir[0]

                # quantization: angles in short to degrees in float
                location_dir_scale = \
                    mds.MDSBoneFrameCompressed.location_dir_scale

                yaw = (yaw >> 4) * location_dir_scale  # TODO why bitshift?
                pitch = (pitch >> 4) * location_dir_scale

                # -
                location_dir = mdi_util.angles_to_vector(yaw, pitch)

                # parent_dist
                parent_dist = mds_bone_info.parent_dist

                # parent_location
                parent_location = \
                    mdi_bone_parent.animation.frames[num_frame].location

            else:  # root bone

                # location_dir
                location_dir = mathutils.Vector((0, 0, 0))

                # parent_dist
                parent_dist = 0

                # parent_location
                mds_frame_info = mds_model.frames[num_frame].frame_info

                parent_location = \
                    mathutils.Vector(mds_frame_info.root_bone_location)

            location = parent_location + (parent_dist * location_dir)

            return location

        def calc_bone_orientation(mds_model, mdi_skeleton, num_bone,
                                  num_frame):

            mds_bone_frame_compressed = \
                mds_model.frames[num_frame].bone_frames_compressed[num_bone]

            yaw = mds_bone_frame_compressed.orientation[1]
            pitch = mds_bone_frame_compressed.orientation[0]
            roll = mds_bone_frame_compressed.orientation[2]

            # quantization: angles in short to degrees in float
            orientation_scale = \
                mds.MDSBoneFrameCompressed.orientation_scale

            yaw = yaw * orientation_scale
            pitch = pitch * orientation_scale
            roll = roll * orientation_scale

            # -
            orientation = mdi_util.euler_to_matrix(yaw, pitch, roll)

            return orientation

        mdi_skeleton = mdi.MDISkeleton()

        mdi_skeleton.bones.torso_parent_bone = \
            mds_model.header.torso_parent_bone

        # bone_list
        for num_bone, mds_bone in enumerate(mds_model.bone_infos):

            name = mdi_util.c_string_to_utf_8_string(mds_bone.name)
            parent_bone = mds_bone.parent_bone
            parent_dist = mds_bone.parent_dist
            torso_weight = mds_bone.torso_weight
            flags = mds_bone.flags
            location = calc_bone_location(mds_model, mdi_skeleton, num_bone,
                                          bind_pose_frame)
            orientation = calc_bone_orientation(mds_model, mdi_skeleton,
                                                num_bone, bind_pose_frame)

            mdi_bone = mdi.MDIBone(name, parent_bone, parent_dist,
                                   torso_weight, flags, location, orientation)

            mdi_skeleton.bones.bone_list.append(mdi_bone)

            # animation
            for num_frame in range(0, len(mds_model.frames)):

                location = calc_bone_location(mds_model, mdi_skeleton,
                                              num_bone, num_frame)
                orientation = calc_bone_orientation(mds_model, mdi_skeleton,
                                                    num_bone, num_frame)

                mdi_bone_in_frame = mdi.MDIBoneInFrame(location, orientation)
                mdi_bone.animation.frames.append(mdi_bone_in_frame)

        return mdi_skeleton

    @staticmethod
    def convert(mds_model, bind_pose_frame = 0):

        mdi_model = mdi.MDI()

        mdi_model.name = \
            mdi_util.c_string_to_utf_8_string(mds_model.header.name)
        mdi_model.lod_scale = mds_model.header.lod_scale
        mdi_model.lod_bias = mds_model.header.lod_bias

        # skeleton
        mdi_skeleton = ModelToMDI._calc_skeleton(mds_model, bind_pose_frame)
        mdi_model.skeletons.skeleton_list.append(mdi_skeleton)

        # surfaces
        for mds_surface in mds_model.surfaces:

            mdi_surface = ModelToMDI._calc_surface(mds_surface,
                                                   mds_model.frames,
                                                   mdi_skeleton,
                                                   bind_pose_frame)
            mdi_model.surfaces.surface_list.append(mdi_surface)

        # sockets
        for mds_tag in mds_model.tags:

            mdi_socket = ModelToMDI._calc_socket(mds_tag)
            mdi_model.sockets.socket_list.append(mdi_socket)

        return mdi_model
