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

"""Converts between in-memory representations of MDC and MDI.
"""

import math

import mathutils

import rtcw_et_model_tools.mdc._mdc as mdc
import rtcw_et_model_tools.mdi.mdi as mdi
import rtcw_et_model_tools.mdi.mdi_util as mdi_util


class MDIToModel:

    @staticmethod
    def convert(mdi_model):

        mdc_model = None

        print("mdc_mdi.MDIToModel")

        return mdc_model


class ModelToMDI:


    @staticmethod
    def _calc_bounds(mdc_frame_infos, bind_frame):

        mdi_bounds = mdi.MDIBounds()

        mdi_bounds.animation = mdi.MDIBoundsAnimation()

        for num_frame, mdc_frame_info in enumerate(mdc_frame_infos):

            min_bound = mathutils.Vector(mdc_frame_info.min_bound)
            max_bound = mathutils.Vector(mdc_frame_info.max_bound)
            local_origin = mathutils.Vector(mdc_frame_info.local_origin)
            radius = mdc_frame_info.radius

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
    def _calc_sockets(mdc_tag_infos, mdc_tags, bind_frame):

        mdi_sockets = mdi.MDISockets()

        if len(mdc_tags) < 1:
            return mdi_sockets

        for mdc_tag_info in mdc_tag_infos:

            name = mdi_util.c_string_to_utf_8_string(mdc_tag_info.name)

            mdi_socket_free = mdi.MDISocketFree(name)
            mdi_sockets.socket_list.append(mdi_socket_free)

        for num_frame, mdc_frame_tags in enumerate(mdc_tags):

            for num_socket, mdc_frame_tag in enumerate(mdc_frame_tags):

                location_x = \
                    mdc_frame_tag.location[0] * mdc.MDCFrameTag.location_scale
                location_y = \
                    mdc_frame_tag.location[1] * mdc.MDCFrameTag.location_scale
                location_z = \
                    mdc_frame_tag.location[2] * mdc.MDCFrameTag.location_scale
                location = \
                    mathutils.Vector((location_x, location_y, location_z))

                yaw = mdc_frame_tag.orientation[1]
                pitch = mdc_frame_tag.orientation[0]
                roll = mdc_frame_tag.orientation[2]

                yaw = yaw * mdc.MDCFrameTag.orientation_scale
                pitch = pitch * mdc.MDCFrameTag.orientation_scale
                roll = roll * mdc.MDCFrameTag.orientation_scale

                orientation = mdi_util.euler_to_matrix(yaw, pitch, roll)

                mdi_socket = mdi_sockets.socket_list[num_socket]

                mdi_socket_free_in_frame = \
                    mdi.MDISocketFreeInFrame(location, orientation)
                mdi_socket.animation.frames.append(mdi_socket_free_in_frame)

                if num_frame == bind_frame:

                    mdi_socket.location = location
                    mdi_socket.orientation = orientation

        return mdi_sockets

    @staticmethod
    def _calc_surface(mdc_surface, mdc_frame_infos, bind_frame):

        def calc_compressed_normals():

            LAT_SCALE = 180 / 16
            SIGMA_WIDTH_DELTA = 4
            SIGMA_WIDTH_MAX = 32

            # build table containing rho-ranges and their medians
            table = []

            # lat=[90, 180]
            cur_sigma_width = SIGMA_WIDTH_MAX
            for i in range(7, 14):

                lower_bound = LAT_SCALE * i + (1/2) * LAT_SCALE
                upper_bound = LAT_SCALE * (i + 1) + (1/2) * LAT_SCALE
                median = LAT_SCALE * (i + 1)
                sigma_width = cur_sigma_width

                table.append((lower_bound, upper_bound, median, sigma_width))

                cur_sigma_width = cur_sigma_width - SIGMA_WIDTH_DELTA

            i = 14
            lower_bound = LAT_SCALE * i + (1/2) * LAT_SCALE
            upper_bound = 180
            median = LAT_SCALE * (i + 1)
            sigma_width = cur_sigma_width

            table.append((lower_bound, upper_bound, median, sigma_width))

            cur_sigma_width = cur_sigma_width - SIGMA_WIDTH_DELTA

            # lat=(90, 0]
            cur_sigma_width = SIGMA_WIDTH_MAX - SIGMA_WIDTH_DELTA
            for i in range(6, 0, -1):

                lower_bound = LAT_SCALE * i + (1/2) * LAT_SCALE
                upper_bound = LAT_SCALE * (i + 1) + (1/2) * LAT_SCALE
                median = LAT_SCALE * (i + 1)
                sigma_width = cur_sigma_width

                table.append((lower_bound, upper_bound, median, sigma_width))

                cur_sigma_width = cur_sigma_width - SIGMA_WIDTH_DELTA

            i = 0
            lower_bound = 0
            upper_bound = LAT_SCALE * (i + 1) + (1/2) * LAT_SCALE
            median = LAT_SCALE * (i + 1)
            sigma_width = cur_sigma_width

            table.append((lower_bound, upper_bound, median, sigma_width))

            cur_sigma_width = cur_sigma_width - SIGMA_WIDTH_DELTA

            # from table build normals
            lat_lon = []

            for i in range(0, len(table)):

                median = table[i][2]
                sigma_width = table[i][3]

                lat = median
                for j in range(0, sigma_width):
                    lon = (360/sigma_width) * j
                    lat_lon.append((lat, lon))

            normals = []

            for i in range(0, len(lat_lon)):

                lat = math.radians(lat_lon[i][0])
                lon = math.radians(lat_lon[i][1])

                x = math.cos(lon) *  math.sin(lat)
                y = math.sin(lon) *  math.sin(lat)
                z = math.cos(lat)

                normals.append((x, y, z))

            return normals

        def calc_vertex_location_base(mdc_base_frame_vertex):

            location_x = \
                mdc_base_frame_vertex.location[0] * \
                mdc.MDCBaseFrameVertex.location_scale
            location_y = \
                mdc_base_frame_vertex.location[1] * \
                mdc.MDCBaseFrameVertex.location_scale
            location_z = \
                mdc_base_frame_vertex.location[2] * \
                mdc.MDCBaseFrameVertex.location_scale

            location = mathutils.Vector((location_x, location_y, location_z))

            return location

        def calc_vertex_ln_comp(mdc_frame_info, mdc_base_frame_vertex,
                                mdc_comp_frame_vertex, compressed_normals):

            # location
            local_origin = mathutils.Vector(mdc_frame_info.local_origin)

            location_base = calc_vertex_location_base(mdc_base_frame_vertex)

            range_abs = 127.0

            offset_x = \
                (mdc_comp_frame_vertex.location_offset[0] - range_abs) * \
                mdc.MDCCompFrameVertex.location_scale
            offset_y = \
                (mdc_comp_frame_vertex.location_offset[1] - range_abs) * \
                mdc.MDCCompFrameVertex.location_scale
            offset_z = \
                (mdc_comp_frame_vertex.location_offset[2] - range_abs) * \
                mdc.MDCCompFrameVertex.location_scale
            location_offset = mathutils.Vector((offset_x, offset_y, offset_z))

            location = local_origin + location_base + location_offset

            normal = compressed_normals[mdc_comp_frame_vertex.normal]
            normal = mathutils.Vector(normal)

            return (location, normal)

        def calc_vertex_ln_base(mdc_base_frame_vertex):

            location = calc_vertex_location_base(mdc_base_frame_vertex)

            yaw = mdc_base_frame_vertex.normal[1] * \
                mdc.MDCBaseFrameVertex.normal_scale
            pitch = mdc_base_frame_vertex.normal[0] *\
                mdc.MDCBaseFrameVertex.normal_scale

            normal = mdi_util.angles_to_vector(yaw, pitch)

            return (location, normal)

        # TODO input check bind_frame

        mdi_surface = mdi.MDISurface()

        mdi_surface.name = \
            mdi_util.c_string_to_utf_8_string(mdc_surface.header.name)

        # vertex_list
        compressed_normals = calc_compressed_normals()

        num_vertices = len(mdc_surface.base_vertices[bind_frame])

        base_frame_index = mdc_surface.base_frame_indices.indices[bind_frame]
        comp_frame_index = mdc_surface.comp_frame_indices.indices[bind_frame]

        frame_is_compressed = False
        if comp_frame_index >= 0:
            frame_is_compressed = True

        if frame_is_compressed:

            for num_vertex in range(0, num_vertices):

                mdc_base_frame_vertex = \
                    mdc_surface.base_vertices[base_frame_index][num_vertex]
                mdc_comp_frame_vertex = \
                    mdc_surface.comp_vertices[comp_frame_index][num_vertex]
                mdc_frame_info = mdc_frame_infos[bind_frame]

                location, normal = calc_vertex_ln_comp(mdc_frame_info,
                                                       mdc_base_frame_vertex,
                                                       mdc_comp_frame_vertex,
                                                       compressed_normals)

                mdi_vertex = mdi.MDIVertex(location, normal)
                mdi_surface.geometry.vertices.vertex_list.append(mdi_vertex)

        else:

            for num_vertex in range(0, num_vertices):

                mdc_base_frame_vertex = \
                    mdc_surface.base_vertices[base_frame_index][num_vertex]

                location, normal = calc_vertex_ln_base(mdc_base_frame_vertex)

                mdi_vertex = mdi.MDIVertex(location, normal)
                mdi_surface.geometry.vertices.vertex_list.append(mdi_vertex)

        # vertex animation
        animation = mdi.MDIMorphVertices()
        mdi_surface.geometry.vertices.animation = animation

        num_frames = mdc_surface.header.num_base_frames + \
            mdc_surface.header.num_comp_frames
        for num_frame in range(0, num_frames):

            mdi_morph_vertices_in_frame = mdi.MDIMorphVerticesInFrame()
            animation.frame_list.append(mdi_morph_vertices_in_frame)

            base_frame_index = mdc_surface.base_frame_indices.indices[num_frame]
            comp_frame_index = mdc_surface.comp_frame_indices.indices[num_frame]

            frame_is_compressed = False
            if comp_frame_index >= 0:
                frame_is_compressed = True

            if frame_is_compressed:

                for num_vertex in range(0, num_vertices):

                    mdc_base_frame_vertex = \
                        mdc_surface.base_vertices[base_frame_index][num_vertex]
                    mdc_comp_frame_vertex = \
                        mdc_surface.comp_vertices[comp_frame_index][num_vertex]
                    mdc_frame_info = mdc_frame_infos[num_frame]

                    location, normal = calc_vertex_ln_comp(mdc_frame_info,
                                                        mdc_base_frame_vertex,
                                                        mdc_comp_frame_vertex,
                                                        compressed_normals)

                    morph_vertex_in_frame = \
                        mdi.MDIMorphVertexInFrame(location, normal)
                    mdi_morph_vertices_in_frame.vertex_list. \
                        append(morph_vertex_in_frame)

            else:

                for num_vertex in range(0, num_vertices):

                    mdc_base_frame_vertex = \
                        mdc_surface.base_vertices[base_frame_index][num_vertex]

                    location, normal = calc_vertex_ln_base(mdc_base_frame_vertex)

                    morph_vertex_in_frame = \
                        mdi.MDIMorphVertexInFrame(location, normal)
                    mdi_morph_vertices_in_frame.vertex_list. \
                        append(morph_vertex_in_frame)

        # triangles
        for mdc_triangle in mdc_surface.triangles:

            index_1 = mdc_triangle.indices[2]
            index_2 = mdc_triangle.indices[1]
            index_3 = mdc_triangle.indices[0]

            mdi_triangle = mdi.MDITriangle((index_1, index_2, index_3))
            mdi_surface.geometry.triangles.triangle_list.append(mdi_triangle)

        # shaders
        mdi_surface.color.shader_data = mdi.MDIShaderReferences()
        shader_reference_list = \
            mdi_surface.color.shader_data.shader_reference_list

        for mdc_shader in mdc_surface.shaders:

            reference = mdi_util.c_string_to_utf_8_string(mdc_shader.name)
            mdi_shader_reference = mdi.MDIShaderReference(reference)
            shader_reference_list.append(mdi_shader_reference)

        # uv_map
        mdi_surface.color.uv_map = mdi.MDIUVMapBijective()

        for mdc_tex_coords in mdc_surface.tex_coords:

            mdi_tex_coords = mdi.MDITexCoords(mdc_tex_coords.tex_coords[0],
                                              1 - mdc_tex_coords.tex_coords[1])
            mdi_surface.color.uv_map.tex_coords_list.append(mdi_tex_coords)

        # lod
        mdi_surface.lod = mdi.MDILODDiscrete()

        return mdi_surface

    @staticmethod
    def convert(mdc_model, bind_frame):

        mdi_model = mdi.MDI()

        mdi_model.name = \
            mdi_util.c_string_to_utf_8_string(mdc_model.header.name)

        # surfaces
        for mdc_surface in mdc_model.surfaces:

            mdi_surface = ModelToMDI._calc_surface(mdc_surface,
                                                   mdc_model.frame_infos,
                                                   bind_frame)
            mdi_model.surfaces.surface_list.append(mdi_surface)

        # sockets
        mdi_model.sockets = ModelToMDI._calc_sockets(mdc_model.tag_infos,
                                                     mdc_model.tags,
                                                     bind_frame)

        # bounds
        mdi_model.bounds = ModelToMDI._calc_bounds(mdc_model.frame_infos,
                                                   bind_frame)

        return mdi_model
