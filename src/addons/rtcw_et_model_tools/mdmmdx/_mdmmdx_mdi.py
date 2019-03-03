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

"""Converts between in-memory representations of MDM/MDX and MDI.
"""

import mathutils

import rtcw_et_model_tools.mdmmdx._mdm as mdm
import rtcw_et_model_tools.mdmmdx._mdx as mdx
import rtcw_et_model_tools.mdi.mdi as mdi
import rtcw_et_model_tools.mdi.mdi_util as mdi_util

from

class MDIToModel:

    @staticmethod
    def convert(mdi_model):

        mdx_model = None
        mdm_model = None

        return (mdx_model, mdm_model)


class ModelToMDI:

    @staticmethod
    def _calc_socket(mdm_tag, mdi_bone):

        def calc_orientation(mdm_tag, mdi_bone):

            forward_x = mdm_tag.orientation[0]
            forward_y = mdm_tag.orientation[1]
            forward_z = mdm_tag.orientation[2]

            left_x = mdm_tag.orientation[3]
            left_y = mdm_tag.orientation[4]
            left_z = mdm_tag.orientation[5]

            up_x = mdm_tag.orientation[6]
            up_y = mdm_tag.orientation[7]
            up_z = mdm_tag.orientation[8]

            orientation_offset = mathutils.Matrix.Identity(3)
            orientation_offset[0][0:3] = forward_x, left_x, up_x # first row
            orientation_offset[1][0:3] = forward_y, left_y, up_y # second row
            orientation_offset[2][0:3] = forward_z, left_z, up_z # third row

            orientation = orientation_offset.transposed() @ mdi_bone.orientation

            return orientation

        name = mdi_util.c_string_to_utf_8_string(mdm_tag.name)
        parent_skeleton = 0
        parent_bone = mdm_tag.parent_bone
        location = mathutils.Vector(mdm_tag.location)
        orientation = calc_orientation(mdm_tag, mdi_bone)

        mdi_socket = mdi.MDISocketParentBoneOffset(name, parent_skeleton,
                                                   parent_bone, location,
                                                   orientation)

        return mdi_socket

    @staticmethod
    def _calc_surface(mdm_surface, mdx_frames, mdi_skeleton,
                      bind_pose_frame = 0):

        def calc_vertex_weighted(mdm_vertex, mdi_skeleton):

            location_weighted = mathutils.Vector((0.0, 0.0, 0.0))
            orientation_weighted = mathutils.Matrix.Identity(3)

            for mdm_weight in mdm_vertex.weights:

                mdi_bone = mdi_skeleton.bones.bone_list[mdm_weight.bone_index]

                bone_weight = mdm_weight.bone_weight
                location = mathutils.Vector(mdm_weight.location)

                # to object space
                tmp = mdi_bone.orientation @ location
                object_space_coords = mdi_bone.location + tmp

                # weight it against bone
                object_space_coords_weighted = \
                    object_space_coords * bone_weight

                location_weighted += object_space_coords_weighted

                orientation_weighted += mdi_bone.orientation * bone_weight

            normal = mathutils.Vector(mdm_vertex.normal)
            normal_weighted = orientation_weighted @ normal

            return (location_weighted, normal_weighted)

        mdi_surface = mdi.MDISurface()

        mdi_surface.name = \
            mdi_util.c_string_to_utf_8_string(mdm_surface.header.name)

        # vertex_list
        for mdm_vertex in mdm_surface.vertices:

            location, normal = calc_vertex_weighted(mdm_vertex, mdi_skeleton)
            mdi_vertex = mdi.MDIVertex(location, normal)
            mdi_surface.geometry.vertices.vertex_list.append(mdi_vertex)

            mdi_rigged_vertex = mdi.MDIRiggedVertex(parent_skeleton = 0)
            mdi_vertex.animation = mdi_rigged_vertex

            for mdm_weight in mdm_vertex.weights:

                parent_bone = mdm_weight.bone_index
                weight = mdm_weight.bone_weight

                mdi_weight = mdi.MDIVertexWeight(parent_bone, weight)
                mdi_rigged_vertex.weights.append(mdi_weight)

        # triangles
        for mdm_triangle in mdm_surface.triangles:

            mdi_triangle = mdi.MDITriangle(mdm_triangle.indices)
            mdi_surface.geometry.triangles.triangle_list.append(mdi_triangle)

        # bounds
        mdi_surface.geometry.bounds = mdi.MDIBounds()
        mdi_bounds = mdi_surface.geometry.bounds
        mdi_bounds.animation = mdi.MDIBoundsAnimation()

        for num_frame, mdx_frame in enumerate(mdx_frames):

            mdx_frame_info = mdx_frame.frame_info

            min_bound = mathutils.Vector(mdx_frame_info.min_bound)
            max_bound = mathutils.Vector(mdx_frame_info.max_bound)
            local_origin = mathutils.Vector(mdx_frame_info.local_origin)
            radius = mdx_frame_info.radius

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
            mdi_util.c_string_to_utf_8_string(mdm_surface.header.shader)
        mdi_surface.color.shader_data = mdi.MDIShaderReference(reference)

        # uv_map
        mdi_surface.color.uv_map = mdi.MDIUVMapBijective()

        for mdm_vertex in mdm_surface.vertices:

            mdi_tex_coords = mdi.MDITexCoords(mdm_vertex.tex_coords[0],
                                              1 - mdm_vertex.tex_coords[1])
            mdi_surface.color.uv_map.tex_coords_list.append(mdi_tex_coords)

        # lod
        min_lod = mdm_surface.header.min_lod
        mappings = mdm_surface.collapse_map.mappings
        mdi_surface.lod = mdi.MDILODCollapseMap(min_lod, mappings)

        return mdi_surface

    @staticmethod
    def _calc_skeleton(mdx_model, bind_pose_frame = 0):

        def calc_bone_location(mdx_model, mdi_skeleton, num_bone, num_frame):

            if num_bone != 0:

                mdx_bone_info = mdx_model.bone_infos[num_bone]
                mdi_bone_parent = \
                    mdi_skeleton.bones.bone_list[mdx_bone_info.parent_bone]

                # location_dir
                mdx_bone_frame_compressed = \
                    mdx_model.frames[num_frame].bone_frames_compressed[num_bone]

                yaw = mdx_bone_frame_compressed.location_dir[1]
                pitch = mdx_bone_frame_compressed.location_dir[0]

                # quantization: angles in short to degrees in float
                location_dir_scale = \
                    mdx.MDXBoneFrameCompressed.location_dir_scale

                yaw = (yaw >> 4) * location_dir_scale  # TODO why bitshift?
                pitch = (pitch >> 4) * location_dir_scale

                # -
                location_dir = mdi_util.angles_to_vector(yaw, pitch)

                # parent_dist
                parent_dist = mdx_bone_info.parent_dist

                # parent_location
                parent_location = \
                    mdi_bone_parent.animation.frames[num_frame].location

            else:  # root bone

                # location_dir
                location_dir = mathutils.Vector((0, 0, 0))

                # parent_dist
                parent_dist = 0

                # parent_location
                mdx_frame_info = mdx_model.frames[num_frame].frame_info

                parent_location = \
                    mathutils.Vector(mdx_frame_info.root_bone_location)

            location = parent_location + (parent_dist * location_dir)

            return location

        def calc_bone_orientation(mdx_model, mdi_skeleton, num_bone,
                                  num_frame):

            mdx_bone_frame_compressed = \
                mdx_model.frames[num_frame].bone_frames_compressed[num_bone]

            yaw = mdx_bone_frame_compressed.orientation[1]
            pitch = mdx_bone_frame_compressed.orientation[0]
            roll = mdx_bone_frame_compressed.orientation[2]

            # quantization: angles in short to degrees in float
            orientation_scale = \
                mdx.MDXBoneFrameCompressed.orientation_scale

            yaw = yaw * orientation_scale
            pitch = pitch * orientation_scale
            roll = roll * orientation_scale

            # -
            orientation = mdi_util.euler_to_matrix(yaw, pitch, roll)

            return orientation

        mdi_skeleton = mdi.MDISkeleton()

        mdi_skeleton.name = \
            mdi_util.c_string_to_utf_8_string(mdx_model.header.name)

        mdi_skeleton.bones.torso_parent_bone = \
            mdx_model.header.torso_parent_bone

        # bone_list
        for num_bone, mdx_bone in enumerate(mdx_model.bone_infos):

            name = mdi_util.c_string_to_utf_8_string(mdx_bone.name)
            parent_bone = mdx_bone.parent_bone
            parent_dist = mdx_bone.parent_dist
            torso_weight = mdx_bone.torso_weight
            flags = mdx_bone.flags
            location = calc_bone_location(mdx_model, mdi_skeleton, num_bone,
                                          bind_pose_frame)
            orientation = calc_bone_orientation(mdx_model, mdi_skeleton,
                                                num_bone, bind_pose_frame)

            mdi_bone = mdi.MDIBone(name, parent_bone, parent_dist,
                                   torso_weight, flags, location, orientation)

            mdi_skeleton.bones.bone_list.append(mdi_bone)

            # animation
            for num_frame in range(0, len(mdx_model.frames)):

                location = calc_bone_location(mdx_model, mdi_skeleton,
                                              num_bone, num_frame)
                orientation = calc_bone_orientation(mdx_model, mdi_skeleton,
                                                    num_bone, num_frame)

                mdi_bone_in_frame = mdi.MDIBoneInFrame(location, orientation)
                mdi_bone.animation.frames.append(mdi_bone_in_frame)

        return mdi_skeleton

    @staticmethod
    def convert(mdx_model, mdm_model = None, bind_pose_frame = 0):

        mdi_model = mdi.MDI()

        if mdm_model is not None:
            mdi_model.name = \
                mdi_util.c_string_to_utf_8_string(mdm_model.header.name)
            mdi_model.lod_scale = mdm_model.header.lod_scale
            mdi_model.lod_bias = mdm_model.header.lod_bias

        # skeleton
        mdi_skeleton = ModelToMDI._calc_skeleton(mdx_model, bind_pose_frame)
        mdi_model.skeletons.skeleton_list.append(mdi_skeleton)

        if mdm_model is not None:

            # surfaces
            for mdm_surface in mdm_model.surfaces:

                mdi_surface = ModelToMDI._calc_surface(mdm_surface,
                                                       mdx_model.frames,
                                                       mdi_skeleton,
                                                       bind_pose_frame)
                mdi_model.surfaces.surface_list.append(mdi_surface)

            # sockets
            for mdm_tag in mdm_model.tags:

                mdi_bone = mdi_skeleton.bones.bone_list[mdm_tag.parent_bone]
                mdi_socket = ModelToMDI._calc_socket(mdm_tag, mdi_bone)
                mdi_model.sockets.socket_list.append(mdi_socket)

        return mdi_model
