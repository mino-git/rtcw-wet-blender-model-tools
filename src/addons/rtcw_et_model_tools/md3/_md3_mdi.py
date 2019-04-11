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

"""Converts between in-memory representations of MD3 and MDI.
"""

import mathutils

import rtcw_et_model_tools.md3._md3 as md3
import rtcw_et_model_tools.mdi.mdi as mdi
import rtcw_et_model_tools.mdi.mdi_util as mdi_util


class MDIToModel:

    @staticmethod
    def convert(mdi_model):

        md3_model = None

        return md3_model


class ModelToMDI:

    @staticmethod
    def _calc_bounds(md3_frame_infos, bind_frame):

        mdi_bounds = mdi.MDIBounds()

        mdi_bounds.animation = mdi.MDIBoundsAnimation()

        for num_frame, md3_frame_info in enumerate(md3_frame_infos):

            min_bound = mathutils.Vector(md3_frame_info.min_bound)
            max_bound = mathutils.Vector(md3_frame_info.max_bound)
            local_origin = mathutils.Vector(md3_frame_info.local_origin)
            radius = md3_frame_info.radius

            mdi_bounds_in_frame = mdi.MDIBoundsInFrame(min_bound, max_bound,
                                                       local_origin, radius)
            mdi_bounds.animation.frames.append(mdi_bounds_in_frame)

            if num_frame == bind_frame:

                mdi_bounds.min_bound = min_bound
                mdi_bounds.max_bound = max_bound
                mdi_bounds.local_origin = local_origin
                mdi_bounds.radius = radius

        return mdi_bounds

    @staticmethod
    def _calc_sockets(md3_tags, bind_frame):

        mdi_sockets = mdi.MDISockets()

        if len(md3_tags) < 1:
            return mdi_sockets

        md3_frame_tags = md3_tags[bind_frame]
        for md3_frame_tag in md3_frame_tags:

            name = mdi_util.c_string_to_utf_8_string(md3_frame_tag.name)

            mdi_socket_free = mdi.MDISocketFree(name)
            mdi_sockets.socket_list.append(mdi_socket_free)

        for num_frame, md3_frame_tags in enumerate(md3_tags):

            for num_socket, md3_frame_tag in enumerate(md3_frame_tags):

                location = mathutils.Vector(md3_frame_tag.location)

                forward_x = md3_frame_tag.orientation[0]
                forward_y = md3_frame_tag.orientation[1]
                forward_z = md3_frame_tag.orientation[2]

                left_x = md3_frame_tag.orientation[3]
                left_y = md3_frame_tag.orientation[4]
                left_z = md3_frame_tag.orientation[5]

                up_x = md3_frame_tag.orientation[6]
                up_y = md3_frame_tag.orientation[7]
                up_z = md3_frame_tag.orientation[8]

                orientation = mathutils.Matrix().Identity(3)
                orientation[0][0:3] = forward_x, left_x, up_x # first row
                orientation[1][0:3] = forward_y, left_y, up_y # second row
                orientation[2][0:3] = forward_z, left_z, up_z # third row

                mdi_socket = mdi_sockets.socket_list[num_socket]

                mdi_socket_free_in_frame = \
                    mdi.MDISocketFreeInFrame(location, orientation)
                mdi_socket.animation.frames.append(mdi_socket_free_in_frame)

                if num_frame == bind_frame:

                    mdi_socket.location = location
                    mdi_socket.orientation = orientation

        return mdi_sockets

    @staticmethod
    def _calc_surface(md3_surface, bind_frame):

        def calc_vertex_ln(md3_frame_vertex):

            location_x = \
                md3_frame_vertex.location[0] * \
                md3.MD3FrameVertex.location_scale
            location_y = \
                md3_frame_vertex.location[1] * \
                md3.MD3FrameVertex.location_scale
            location_z = \
                md3_frame_vertex.location[2] * \
                md3.MD3FrameVertex.location_scale

            location = mathutils.Vector((location_x, location_y, location_z))

            yaw = md3_frame_vertex.normal[1] * \
                md3.MD3FrameVertex.normal_scale
            pitch = md3_frame_vertex.normal[0] * \
                md3.MD3FrameVertex.normal_scale

            normal = mdi_util.angles_to_vector(yaw, pitch)

            return (location, normal)

        mdi_surface = mdi.MDISurface()

        mdi_surface.name = \
            mdi_util.c_string_to_utf_8_string(md3_surface.header.name)

        # vertex_list
        for num_vertex in range(0, len(md3_surface.vertices[bind_frame])):

            md3_frame_vertex = md3_surface.vertices[bind_frame][num_vertex]

            location, normal = calc_vertex_ln(md3_frame_vertex)

            mdi_vertex = mdi.MDIVertex(location, normal)
            mdi_surface.geometry.vertices.vertex_list.append(mdi_vertex)

        # vertex animation
        animation = mdi.MDIMorphVertices()
        mdi_surface.geometry.vertices.animation = animation

        for num_frame in range(0, len(md3_surface.vertices)):

            mdi_morph_vertices_in_frame = mdi.MDIMorphVerticesInFrame()
            animation.frame_list.append(mdi_morph_vertices_in_frame)

            for num_vertex in range(0, len(md3_surface.vertices[bind_frame])):

                md3_frame_vertex = md3_surface.vertices[num_frame][num_vertex]

                location, normal = calc_vertex_ln(md3_frame_vertex)

                morph_vertex_in_frame = \
                    mdi.MDIMorphVertexInFrame(location, normal)
                mdi_morph_vertices_in_frame.vertex_list. \
                    append(morph_vertex_in_frame)

        # triangles
        for md3_triangle in md3_surface.triangles:

            index_1 = md3_triangle.indices[2]
            index_2 = md3_triangle.indices[1]
            index_3 = md3_triangle.indices[0]

            mdi_triangle = mdi.MDITriangle((index_1, index_2, index_3))
            mdi_surface.geometry.triangles.triangle_list.append(mdi_triangle)

        # shaders
        mdi_surface.color.shader_data = mdi.MDIShaderReferences()
        shader_reference_list = \
            mdi_surface.color.shader_data.shader_reference_list

        for md3_shader in md3_surface.shaders:

            reference = mdi_util.c_string_to_utf_8_string(md3_shader.name)
            mdi_shader_reference = mdi.MDIShaderReference(reference)
            shader_reference_list.append(mdi_shader_reference)

        # uv_map
        mdi_surface.color.uv_map = mdi.MDIUVMapBijective()

        for md3_tex_coords in md3_surface.tex_coords:

            mdi_tex_coords = mdi.MDITexCoords(md3_tex_coords.tex_coords[0],
                                              1 - md3_tex_coords.tex_coords[1])
            mdi_surface.color.uv_map.tex_coords_list.append(mdi_tex_coords)

        # lod
        mdi_surface.lod = mdi.MDILODDiscrete()

        return mdi_surface

    @staticmethod
    def convert(md3_model, bind_frame):

        mdi_model = mdi.MDI()

        mdi_model.name = \
            mdi_util.c_string_to_utf_8_string(md3_model.header.name)

        # surfaces
        for md3_surface in md3_model.surfaces:

            mdi_surface = ModelToMDI._calc_surface(md3_surface,
                                                   bind_frame)
            mdi_model.surfaces.surface_list.append(mdi_surface)

        # sockets
        mdi_model.sockets = ModelToMDI._calc_sockets(md3_model.tags,
                                                     bind_frame)

        # bounds
        mdi_model.bounds = ModelToMDI._calc_bounds(md3_model.frame_infos,
                                                   bind_frame)

        return mdi_model
