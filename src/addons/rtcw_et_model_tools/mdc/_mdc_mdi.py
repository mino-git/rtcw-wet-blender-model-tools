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

import rtcw_et_model_tools.mdc._mdc as mdc_m
import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.mdi.util as mdi_util_m
import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


MAX_OFS = 127.0
XYZC_SCALE = 1.0 / 20
MAX_DIST = MAX_OFS * XYZC_SCALE # 6,35
MAX_COMPRESSION_DELTA = 0.1

def _calc_comp_frame_normals():
    """Calculates a list of 256 normals.

    Notes:

        This is an older version where latitude and longitude naming
        conventions were used instead of pitch and yaw.

        The method used here was reconstructed by the help of a publication of
        Wolfgang Prinz, see:
        "The MDC File Format - Wolfgang Prinz - May 2, 2004".
        The method produces the same list of precalculated normals as W:ET
        source code, see:
        https://github.com/id-Software/Enemy-Territory/blob/master/src/renderer/anorms256.h

    Background:

        There are a total of 256 normals. These normals are encoded into
        8-Bits. During runtime an index is used to reach the normal, if the
        frame is compressed.

        To calculate the normals the up-vector is rotated by a pitch value,
        then a yaw value. The pitch value is between 0 (up) and 180 (down). If
        we fix the pitch value, we can make a 360 turn of yaw values, so the
        normals are evenly distributed. Pitch values near 90 produce more
        normals compared to pitch values near 0 or 180. This is because when
        the normal is pointing mostly up or down, the yaw value won't change
        direction as much.

    Returns:

        normals (list<tuple[3]>[256]): list of precalculated normals for
            compressed frames.
    """

    timer = timer_m.Timer()
    reporter_m.debug("Calculating comp frame normals ...")

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

        lat = lat_lon[i][0]
        lon = lat_lon[i][1]

        normal = mdi_util_m.rotate_up_vector(lon, lat)
        normals.append(normal)

    time = timer.time()
    reporter_m.debug("Calculating comp frame normals DONE (time={})"
        .format(time))

    return normals


class MDIToModel:
    """MDI to MDC conversion.
    """

    @staticmethod
    def _calc_mdc_headers(mdc_model, mdi_model):

        # mdc_model.header
        ident = mdc_m.MDCHeader.ident
        version = mdc_m.MDCHeader.version
        name = \
            mdi_util_m.to_c_string_padded(mdi_model.name,
                                          mdc_m.MDCHeader.name_len)
        flags = mdc_m.MDCHeader.flags
        num_frames = 0
        if mdc_model.surfaces:
            if mdc_model.surfaces[0].base_frame_indices.indices:
                num_frames = \
                    len(mdc_model.surfaces[0].base_frame_indices.indices)
        elif mdc_model.tags:
            num_frames = len(mdc_model.tags)
        num_tags = 0
        if mdc_model.tags and mdc_model.tags[0]:
            num_tags = len(mdc_model.tags[0])
        num_surfaces = len(mdc_model.surfaces)
        num_skins = 0

        ofs_frame_infos = 0 + mdc_m.MDCHeader.format_size
        ofs_tag_infos = ofs_frame_infos + \
            num_frames * mdc_m.MDCFrameInfo.format_size
        ofs_tags = ofs_tag_infos + num_tags * mdc_m.MDCTagInfo.format_size
        ofs_surfaces = ofs_tags + \
            num_frames * num_tags * mdc_m.MDCFrameTag.format_size
        ofs_end = None  # calculated later

        mdc_model.header = mdc_m.MDCHeader(ident, version, name, flags,
                                           num_frames, num_tags, num_surfaces,
                                           num_skins, ofs_frame_infos,
                                           ofs_tag_infos, ofs_tags,
                                           ofs_surfaces, ofs_end)

        surfaces_field_len = 0  # to calculate ofs_end

        # mdc_surface.header
        for num_surface, mdc_surface in enumerate(mdc_model.surfaces):

            ident = mdc_m.MDCSurfaceHeader.ident
            name = mdi_model.surfaces[num_surface].name
            name = \
                mdi_util_m.to_c_string_padded(name,
                                              mdc_m.MDCSurfaceHeader.name_len)
            flags = mdc_m.MDCSurfaceHeader.flags
            num_comp_frames = len(mdc_surface.comp_vertices)
            num_base_frames = len(mdc_surface.base_vertices)
            num_shaders = len(mdc_surface.shaders)
            num_vertices = 0
            if mdc_surface.base_vertices:
                num_vertices = len(mdc_surface.base_vertices[0])
            num_triangles = len(mdc_surface.triangles)
            ofs_triangles = 0 + mdc_m.MDCSurfaceHeader.format_size
            ofs_shaders = ofs_triangles + \
                num_triangles * mdc_m.MDCTriangle.format_size
            ofs_tex_coords = ofs_shaders + \
                num_shaders * mdc_m.MDCShader.format_size
            ofs_base_vertices = ofs_tex_coords + \
                num_vertices * mdc_m.MDCTexCoords.format_size
            ofs_comp_vertices = ofs_base_vertices + \
                num_base_frames * num_vertices * \
                mdc_m.MDCBaseFrameVertex.format_size
            ofs_base_frame_indices = ofs_comp_vertices + \
                num_comp_frames * num_vertices * \
                mdc_m.MDCCompFrameVertex.format_size
            ofs_comp_frame_indices = ofs_base_frame_indices + \
                num_frames * mdc_m.MDCBaseFrameIndices.format_size
            ofs_end = ofs_comp_frame_indices + \
                num_frames * mdc_m.MDCCompFrameIndices.format_size

            mdc_surface.header = \
                mdc_m.MDCSurfaceHeader(ident, name, flags, num_comp_frames,
                                       num_base_frames, num_shaders,
                                       num_vertices, num_triangles,
                                       ofs_triangles, ofs_shaders,
                                       ofs_tex_coords, ofs_base_vertices,
                                       ofs_comp_vertices,
                                       ofs_base_frame_indices,
                                       ofs_comp_frame_indices, ofs_end)
            surfaces_field_len += ofs_end

        mdc_model.header.ofs_end = ofs_surfaces + surfaces_field_len

    @staticmethod
    def _calc_frame_indices(mdi_model):

        timer = timer_m.Timer()
        reporter_m.debug("Calculating frame indices ...")

        # find max frame count of the surfaces
        num_frames = 0
        for mdi_surface in mdi_model.surfaces:

            if mdi_surface.vertices:

                first_morph_vertex = mdi_surface.vertices[0]
                if len(first_morph_vertex.locations) > num_frames:
                    num_frames = len(first_morph_vertex.locations)

        # determine which frame can be compressed
        is_frame_compressed = []
        last_base_frame = -1
        for num_frame in range(0, num_frames):

            base_frame_found = False

            if last_base_frame == -1:
                base_frame_found = True

            for mdi_surface in mdi_model.surfaces:

                if base_frame_found:
                    break

                for mdi_morph_vertex in mdi_surface.vertices:

                    base_frame_pos = \
                        mdi_morph_vertex.locations[last_base_frame]
                    cur_frame_pos = mdi_morph_vertex.locations[num_frame]

                    compressible = \
                        MDIToModel._can_compress_vertex(base_frame_pos,
                                                        cur_frame_pos)
                    if not compressible:
                        base_frame_found = True
                        break

            if base_frame_found:
                last_base_frame = num_frame
                is_frame_compressed.append(False)
            else:
                is_frame_compressed.append(True)

        # calculate indices
        base_frame_indices = []
        comp_frame_indices = []

        if len(is_frame_compressed) > 0:  # first frame
            base_frame_indices.append(0)
            comp_frame_indices.append(-1)

        base_index = 0
        comp_index = 0
        for num_frame in range(1, len(is_frame_compressed)):

            is_compressed = is_frame_compressed[num_frame]

            if is_compressed:

                base_frame_indices.append(base_index)
                comp_frame_indices.append(comp_index)
                comp_index += 1

            else:

                base_index += 1
                base_frame_indices.append(base_index)
                comp_frame_indices.append(-1)

        mdc_base_frame_indices = mdc_m.MDCBaseFrameIndices(base_frame_indices)
        mdc_comp_frame_indices = mdc_m.MDCCompFrameIndices(comp_frame_indices)

        # for debugging
        num_base_frames = 0
        for index in mdc_comp_frame_indices.indices:
            if index == -1:
                num_base_frames += 1
        time = timer.time()
        reporter_m.debug("Found {} base frames".format(num_base_frames))
        reporter_m.debug("Calculating frame indices DONE (time={})"
            .format(time))

        return (mdc_base_frame_indices, mdc_comp_frame_indices)

    @staticmethod
    def _decompress_vertex(location_offset,
                           normal = None,
                           comp_frame_normals = None):

        off_x = location_offset[0] - mdc_m.MDCCompFrameVertex.max_ofs
        off_y = location_offset[1] - mdc_m.MDCCompFrameVertex.max_ofs
        off_z = location_offset[2] - mdc_m.MDCCompFrameVertex.max_ofs

        off_x = off_x * mdc_m.MDCCompFrameVertex.location_scale
        off_y = off_y * mdc_m.MDCCompFrameVertex.location_scale
        off_z = off_z * mdc_m.MDCCompFrameVertex.location_scale

        uc_location_offset = mathutils.Vector((off_x, off_y, off_z))

        uc_normal = None
        if normal and comp_frame_normals:
            uc_normal = comp_frame_normals[normal]

        return (uc_location_offset, uc_normal)

    @staticmethod
    def _compress_vertex(base_frame_location, cur_frame_location,
                         normal = None, comp_frame_normals = None):

        # location offset
        off = cur_frame_location - base_frame_location

        location_scale = mdc_m.MDCCompFrameVertex.location_scale
        max_ofs = mdc_m.MDCCompFrameVertex.max_ofs

        off_x = off[0] + location_scale * 0.5  # rounding
        off_x = off_x / location_scale
        off_x = int(off_x + max_ofs)

        off_y = off[1] + location_scale * 0.5  # rounding
        off_y = off_y / location_scale
        off_y = int(off_y + max_ofs)

        off_z = off[2] + location_scale * 0.5  # rounding
        off_z = off_z / location_scale
        off_z = int(off_z + max_ofs)

        location_offset = (off_x, off_y, off_z)

        # normal
        compressed_normal = None
        if normal != None:

            best_normal = 0

            # find best z group
            z_group_start = 0
            best_diff = 999
            for i in range(0, len(comp_frame_normals)):

                diff = abs(normal[2] - comp_frame_normals[i][2])
                if diff < best_diff:
                    best_diff = diff
                    z_group_start = i

            # within z group find best normal
            z_group_val = comp_frame_normals[z_group_start][2]
            best_diff = -999
            for i in range(z_group_start, len(comp_frame_normals)):

                if comp_frame_normals[i][2] != z_group_val:
                    break

                diff = normal[0] * comp_frame_normals[i][0] + \
                       normal[1] * comp_frame_normals[i][1] + \
                       normal[2] * comp_frame_normals[i][2]

                if diff > best_diff:
                    best_diff = diff
                    best_normal = i

            compressed_normal = best_normal

        return (location_offset, compressed_normal)

    @staticmethod
    def _can_compress_vertex(base_frame_pos, cur_frame_pos):

        can_compress = True
        delta = cur_frame_pos - base_frame_pos
        for i in range(0, 3):
            if abs(delta[i]) > mdc_m.MDC.max_dist:
                can_compress = False

        return can_compress

    @staticmethod
    def _calc_vertices(mdi_model, num_surface, comp_frame_normals,
                       base_frame_indices, comp_frame_indices):

        mdi_surface = mdi_model.surfaces[num_surface]

        timer = timer_m.Timer()
        reporter_m.debug("Calculating MDC vertices: {} ..."
            .format(mdi_surface.name))

        mdc_base_vertices = []
        mdc_comp_vertices = []

        num_base_frame = 0

        for num_frame, comp_frame_index in \
            enumerate(comp_frame_indices.indices):

            frame_is_compressed = comp_frame_index != -1
            if frame_is_compressed:

                comp_frame_vertices = []

                for mdi_morph_vertex in mdi_surface.vertices:

                    cur_frame_location = mdi_morph_vertex.locations[num_frame]

                    base_frame_location = \
                        mdi_morph_vertex.locations[num_base_frame]

                    normal = mdi_morph_vertex.normals[num_frame]

                    location_offset, normal = \
                        MDIToModel._compress_vertex(base_frame_location,
                                                    cur_frame_location,
                                                    normal,
                                                    comp_frame_normals)

                    mdc_comp_frame_vertex = \
                        mdc_m.MDCCompFrameVertex(location_offset, normal)
                    comp_frame_vertices.append(mdc_comp_frame_vertex)

                mdc_comp_vertices.append(comp_frame_vertices)

            else:  # frame is not compressed

                num_base_frame = num_frame

                base_frame_vertices = []

                for mdi_morph_vertex in mdi_surface.vertices:

                    cur_frame_location = \
                        mdi_morph_vertex.locations \
                            [num_frame]

                    location_scale = mdc_m.MDCBaseFrameVertex.location_scale
                    x = int(cur_frame_location[0] / location_scale)
                    y = int(cur_frame_location[1] / location_scale)
                    z = int(cur_frame_location[2] / location_scale)
                    location = (x, y, z)

                    mdi_normal = mdi_morph_vertex.normals[num_frame]
                    yaw, pitch = mdi_util_m.angles_from_up_vector(mdi_normal)

                    if yaw < 0:
                        yaw = 360 + yaw

                    if pitch < 0:
                        pitch = 180 + pitch

                    yaw = int(yaw / mdc_m.MDCBaseFrameVertex.normal_scale)
                    pitch = int(pitch / mdc_m.MDCBaseFrameVertex.normal_scale)
                    normal = (yaw, pitch)

                    mdc_base_frame_vertex = \
                        mdc_m.MDCBaseFrameVertex(location, normal)
                    base_frame_vertices.append(mdc_base_frame_vertex)

                mdc_base_vertices.append(base_frame_vertices)

        time = timer.time()
        reporter_m.debug("Calculating MDC vertices DONE (time={})"
            .format(time))

        return (mdc_base_vertices, mdc_comp_vertices)

    @staticmethod
    def _to_mdc_tex_coords(mdi_model, num_surface, num_tex_coords):

        mdi_surface = mdi_model.surfaces[num_surface]
        mdi_uv = mdi_surface.uv_map.uvs[num_tex_coords]

        u = mdi_uv.u
        v = 1 - mdi_uv.v
        mdc_tex_coords = mdc_m.MDCTexCoords((u, v))

        return mdc_tex_coords

    @staticmethod
    def _to_mdc_shader(mdi_model, num_surface, num_shader):

        mdi_surface = mdi_model.surfaces[num_surface]
        mdi_shader_path = mdi_surface.shader.paths[num_shader]

        name = mdi_util_m.to_c_string_padded(mdi_shader_path.path,
                                             mdc_m.MDCShader.name_len)
        shader_index = mdc_m.MDCShader.shader_index
        mdc_shader = mdc_m.MDCShader(name, shader_index)

        return mdc_shader

    @staticmethod
    def _to_mdc_triangle(mdi_model, num_surface, num_triangle):

        mdi_triangle = mdi_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = mdi_triangle.indices[0]
        index_2 = mdi_triangle.indices[2]
        index_3 = mdi_triangle.indices[1]
        indices = (index_1, index_2, index_3)
        mdc_triangle = mdc_m.MDCTriangle(indices)

        return mdc_triangle

    @staticmethod
    def _to_mdc_surface(mdi_model, num_surface, comp_frame_normals,
                        base_frame_indices, comp_frame_indices):

        mdc_surface = mdc_m.MDCSurface()

        mdi_surface = mdi_model.surfaces[num_surface]

        # mdc triangles
        for num_triangle in range(len(mdi_surface.triangles)):

            mdc_triangle = MDIToModel._to_mdc_triangle(mdi_model,
                                                       num_surface,
                                                       num_triangle)
            mdc_surface.triangles.append(mdc_triangle)

        # mdc shaders
        for num_shader in range(len(mdi_surface.shader.paths)):

            mdc_shader = MDIToModel._to_mdc_shader(mdi_model,
                                                   num_surface,
                                                   num_shader)
            mdc_surface.shaders.append(mdc_shader)

        # mdc tex coords
        for num_tex_coords in range(len(mdi_surface.uv_map.uvs)):

            mdc_tex_coords = MDIToModel._to_mdc_tex_coords(mdi_model,
                                                           num_surface,
                                                           num_tex_coords)
            mdc_surface.tex_coords.append(mdc_tex_coords)

        # mdc frame vertices
        mdc_base_vertices, mdc_comp_vertices = \
            MDIToModel._calc_vertices(mdi_model,
                                      num_surface,
                                      comp_frame_normals,
                                      base_frame_indices,
                                      comp_frame_indices)
        mdc_surface.base_vertices = mdc_base_vertices
        mdc_surface.comp_vertices = mdc_comp_vertices

        # mdc frame indices
        mdc_surface.base_frame_indices = base_frame_indices
        mdc_surface.comp_frame_indices = comp_frame_indices

        return mdc_surface

    @staticmethod
    def _to_mdc_frame_tags(mdi_model, num_frame):

        mdc_frame_tags = []

        for mdi_free_tag in mdi_model.tags:

            location = mdi_free_tag.locations[num_frame]
            location = location / mdc_m.MDCFrameTag.location_scale
            location = (int(location[0] + 0.5),
                        int(location[1] + 0.5),
                        int(location[2] + 0.5))

            yaw, pitch, roll = mdi_util_m.matrix_to_angles \
                               (
                                   mdi_free_tag.orientations[num_frame]
                               )
            yaw = int(yaw / mdc_m.MDCFrameTag.orientation_scale)
            pitch = int(pitch / mdc_m.MDCFrameTag.orientation_scale)
            roll = int(roll / mdc_m.MDCFrameTag.orientation_scale)
            orientation = (pitch, yaw, roll)

            mdc_frame_tag = mdc_m.MDCFrameTag(location, orientation)
            mdc_frame_tags.append(mdc_frame_tag)

        return mdc_frame_tags

    @staticmethod
    def _to_mdc_tag_info(mdi_model, num_tag):

        name = mdi_model.tags[num_tag].name
        name = mdi_util_m.to_c_string_padded(name, mdc_m.MDCFrameInfo.name_len)
        mdc_tag_info = mdc_m.MDCTagInfo(name)

        return mdc_tag_info

    @staticmethod
    def _to_mdc_frame_info(mdi_model, num_frame):

        mdi_aabb = mdi_model.bounds.aabbs[num_frame]
        mdi_bounding_sphere = mdi_model.bounds.spheres[num_frame]

        min_bound = mdi_aabb.min_bound.to_tuple()
        max_bound = mdi_aabb.max_bound.to_tuple()
        local_origin = mdi_bounding_sphere.origin.to_tuple()
        radius = mdi_bounding_sphere.radius
        name = mdi_util_m.to_c_string_padded(mdc_m.MDCFrameInfo.frame_name,
                                             mdc_m.MDCFrameInfo.name_len)

        mdc_frame_info = mdc_m.MDCFrameInfo(min_bound, max_bound, local_origin,
                                          radius, name)

        return mdc_frame_info

    @staticmethod
    def convert(mdi_model):
        """Converts MDI to MDC.

        Args:

            mdi_model (MDI): MDI model.

        Returns:

            mdc_model (MDC): MDC model.
        """

        timer = timer_m.Timer()
        reporter_m.info("Converting MDI to MDC ...")

        mdc_model = mdc_m.MDC()

        # type conversions
        for num_surface, mdi_surface in enumerate(mdi_model.surfaces):

            mdi_surface.uv_map_to_type(mdi_m.MDIUVMapBijective)
            mdi_surface.shader_to_type(mdi_m.MDIShaderPaths)
            mdi_surface.vertices_to_type(mdi_m.MDIMorphVertex, mdi_model)

        mdi_model.tags_to_type(mdi_m.MDIFreeTag)
        mdi_model.lod_to_type(mdi_m.MDIDiscreteLOD)

        # mdc frame infos
        for num_frame in range(len(mdi_model.bounds.aabbs)):

            mdc_frame_info = MDIToModel._to_mdc_frame_info(mdi_model,
                                                           num_frame)
            mdc_model.frame_infos.append(mdc_frame_info)

        # mdc tag infos
        for num_tag in range(len(mdi_model.tags)):

            mdc_tag_info = MDIToModel._to_mdc_tag_info(mdi_model,
                                                       num_tag)
            mdc_model.tag_infos.append(mdc_tag_info)

        # mdc frame tags
        for mdi_free_tag in mdi_model.tags:

            for num_frame in range(len(mdi_free_tag.locations)):

                mdc_frame_tags = MDIToModel._to_mdc_frame_tags(mdi_model,
                                                               num_frame)
                mdc_model.tags.append(mdc_frame_tags)

            break

        # mdc surfaces
        comp_frame_normals = _calc_comp_frame_normals()
        base_frame_indices, comp_frame_indices = \
            MDIToModel._calc_frame_indices(mdi_model)

        for num_surface in range(len(mdi_model.surfaces)):

            mdc_surface = MDIToModel._to_mdc_surface(mdi_model,
                                                     num_surface,
                                                     comp_frame_normals,
                                                     base_frame_indices,
                                                     comp_frame_indices)
            mdc_model.surfaces.append(mdc_surface)

        # headers
        MDIToModel._calc_mdc_headers(mdc_model, mdi_model)

        time = timer.time()
        reporter_m.info("Converting MDI to MDC DONE (time={})".format(time))

        return mdc_model


class ModelToMDI:
    """MDC to MDI conversion.
    """

    @staticmethod
    def _to_mdi_bounds(mdc_model):

        mdi_bounds = mdi_m.MDIBoundingVolume()

        for mdc_frame_info in mdc_model.frame_infos:

            # aabb
            min_bound = mathutils.Vector(mdc_frame_info.min_bound)
            max_bound = mathutils.Vector(mdc_frame_info.max_bound)
            mdi_aabb = mdi_m.MDIAABB(min_bound, max_bound)
            mdi_bounds.aabbs.append(mdi_aabb)

            # sphere
            origin = mathutils.Vector(mdc_frame_info.local_origin)
            radius = mdc_frame_info.radius
            mdi_bounding_sphere = mdi_m.MDIBoundingSphere(origin, radius)
            mdi_bounds.spheres.append(mdi_bounding_sphere)

        return mdi_bounds

    @staticmethod
    def _to_mdi_tag(mdc_model, num_tag):

        mdi_tag = mdi_m.MDIFreeTag()

        # name
        name = mdc_model.tag_infos[num_tag].name
        mdi_tag.name = mdi_util_m.from_c_string_padded(name)

        for mdc_frame_tags in mdc_model.tags:

            mdc_frame_tag = mdc_frame_tags[num_tag]

            # location
            x = mdc_frame_tag.location[0] * mdc_m.MDCFrameTag.location_scale
            y = mdc_frame_tag.location[1] * mdc_m.MDCFrameTag.location_scale
            z = mdc_frame_tag.location[2] * mdc_m.MDCFrameTag.location_scale

            mdi_location = mathutils.Vector((x, y, z))
            mdi_tag.locations.append(mdi_location)

            # orientation
            yaw = mdc_frame_tag.orientation[1]
            pitch = mdc_frame_tag.orientation[0]
            roll = mdc_frame_tag.orientation[2]

            yaw = yaw * mdc_m.MDCFrameTag.orientation_scale
            pitch = pitch * mdc_m.MDCFrameTag.orientation_scale
            roll = roll * mdc_m.MDCFrameTag.orientation_scale

            mdi_orientation = mdi_util_m.angles_to_matrix(yaw, pitch, roll)
            mdi_orientation = mdi_orientation.transposed() # fix for issues #11 and #17

            mdi_tag.orientations.append(mdi_orientation)

        return mdi_tag

    @staticmethod
    def _to_mdi_uv_map(mdc_model, num_surface):

        mdi_uv_map = mdi_m.MDIUVMapBijective()

        for mdc_tex_coords in mdc_model.surfaces[num_surface].tex_coords:

            u = mdc_tex_coords.tex_coords[0]
            v = 1 - mdc_tex_coords.tex_coords[1]

            mdi_uv = mdi_m.MDIUV(u, v)
            mdi_uv_map.uvs.append(mdi_uv)

        return mdi_uv_map

    @staticmethod
    def _to_mdi_shader(mdc_model, num_surface):

        mdi_shader_paths = mdi_m.MDIShaderPaths()

        for mdc_shader in mdc_model.surfaces[num_surface].shaders:

            path = mdi_util_m.from_c_string_padded(mdc_shader.name)
            mdi_shader_path = mdi_m.MDIShaderPath(path)
            mdi_shader_paths.paths.append(mdi_shader_path)

        return mdi_shader_paths

    @staticmethod
    def _to_mdi_triangle(mdc_model, num_surface, num_triangle):

        mdc_triangle = mdc_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = mdc_triangle.indices[0]
        index_2 = mdc_triangle.indices[2]
        index_3 = mdc_triangle.indices[1]

        mdi_triangle = mdi_m.MDITriangle([index_1, index_2, index_3])
        return mdi_triangle

    @staticmethod
    def _to_mdi_morph_vertex(mdc_model, num_surface, num_vertex,
                             comp_frame_normals):

        mdi_morph_vertex = mdi_m.MDIMorphVertex()

        mdc_base_frame_vertices = mdc_model.surfaces[num_surface].base_vertices
        mdc_comp_frame_vertices = mdc_model.surfaces[num_surface].comp_vertices
        mdc_base_frame_indices = \
            mdc_model.surfaces[num_surface].base_frame_indices.indices
        mdc_comp_frame_indices = \
            mdc_model.surfaces[num_surface].comp_frame_indices.indices

        num_base_frame = 0

        for num_frame in range(len(mdc_base_frame_indices)):

            frame_is_compressed = mdc_comp_frame_indices[num_frame] != -1
            if frame_is_compressed:

                comp_frame_index = mdc_comp_frame_indices[num_frame]
                mdc_comp_frame_vertex = \
                    mdc_comp_frame_vertices[comp_frame_index][num_vertex]

                # location
                max_ofs = mdc_m.MDCCompFrameVertex.max_ofs
                off_x = mdc_comp_frame_vertex.location_offset[0] - max_ofs
                off_y = mdc_comp_frame_vertex.location_offset[1] - max_ofs
                off_z = mdc_comp_frame_vertex.location_offset[2] - max_ofs

                off_x = off_x * mdc_m.MDCCompFrameVertex.location_scale
                off_y = off_y * mdc_m.MDCCompFrameVertex.location_scale
                off_z = off_z * mdc_m.MDCCompFrameVertex.location_scale

                location_offset = mathutils.Vector((off_x, off_y, off_z))
                location_base = mdi_morph_vertex.locations[num_base_frame]
                location = location_base + location_offset

                # normal
                normal = comp_frame_normals[mdc_comp_frame_vertex.normal]
                normal = mathutils.Vector(normal)

            else:

                num_base_frame = num_frame

                base_frame_index = mdc_base_frame_indices[num_frame]
                mdc_base_frame_vertex = \
                    mdc_base_frame_vertices[base_frame_index][num_vertex]

                # location
                x = mdc_base_frame_vertex.location[0]
                y = mdc_base_frame_vertex.location[1]
                z = mdc_base_frame_vertex.location[2]

                x = x * mdc_m.MDCBaseFrameVertex.location_scale
                y = y * mdc_m.MDCBaseFrameVertex.location_scale
                z = z * mdc_m.MDCBaseFrameVertex.location_scale
                location = mathutils.Vector((x, y, z))

                # normal
                yaw = mdc_base_frame_vertex.normal[0]
                pitch = mdc_base_frame_vertex.normal[1]

                yaw = yaw * mdc_m.MDCBaseFrameVertex.normal_scale
                pitch = pitch * mdc_m.MDCBaseFrameVertex.normal_scale

                normal = mdi_util_m.rotate_up_vector(yaw, pitch)
                normal = mathutils.Vector(normal)

            mdi_morph_vertex.locations.append(location)
            mdi_morph_vertex.normals.append(normal)

        return mdi_morph_vertex

    @staticmethod
    def _to_mdi_surface(mdc_model, num_surface, comp_frame_normals):

        mdi_surface = mdi_m.MDISurface()

        mdc_surface = mdc_model.surfaces[num_surface]

        # name
        mdi_surface.name = \
            mdi_util_m.from_c_string_padded(mdc_surface.header.name)

        # mdi vertices
        for mdc_base_vertices in mdc_surface.base_vertices:

            for num_vertex in range(len(mdc_base_vertices)):

                mdi_morph_vertex = \
                    ModelToMDI._to_mdi_morph_vertex(mdc_model,
                                                    num_surface,
                                                    num_vertex,
                                                    comp_frame_normals)
                mdi_surface.vertices.append(mdi_morph_vertex)

            break

        # mdi triangles
        for num_triangle in range(len(mdc_surface.triangles)):

            mdi_triangle = \
                ModelToMDI._to_mdi_triangle(mdc_model,
                                            num_surface,
                                            num_triangle)
            mdi_surface.triangles.append(mdi_triangle)

        # mdi shader
        mdi_surface.shader = ModelToMDI._to_mdi_shader(mdc_model, num_surface)

        # mdi uv map
        mdi_surface.uv_map = ModelToMDI._to_mdi_uv_map(mdc_model, num_surface)

        return mdi_surface

    @staticmethod
    def convert(mdc_model, root_frame = 0):
        """Converts MDC to MDI.

        Args:

            mdc_model (MDC): MDC model.
            root_frame (int): frame of the model before animation pass.

        Returns:

            mdi_model (MDI): MDI model.
        """

        timer = timer_m.Timer()
        reporter_m.info("Converting MDC to MDI ...")

        mdi_model = mdi_m.MDI()

        mdi_model.name = mdi_util_m.from_c_string_padded(mdc_model.header.name)
        mdi_model.root_frame = root_frame

        # mdi surfaces
        comp_frame_normals = _calc_comp_frame_normals()

        for num_surface in range(len(mdc_model.surfaces)):

            mdi_surface = ModelToMDI._to_mdi_surface(mdc_model, num_surface,
                                                     comp_frame_normals)
            mdi_model.surfaces.append(mdi_surface)

        # mdi skeleton
        # pass

        # mdi tags
        for mdc_frame_tags in mdc_model.tags:

            for num_tag in range(len(mdc_frame_tags)):

                mdi_tag = ModelToMDI._to_mdi_tag(mdc_model, num_tag)
                mdi_model.tags.append(mdi_tag)

            break

        # mdi bounding volume
        mdi_model.bounds = ModelToMDI._to_mdi_bounds(mdc_model)

        # mdi lod
        mdi_model.lod = mdi_m.MDIDiscreteLOD()

        time = timer.time()
        reporter_m.info("Converting MDC to MDI DONE (time={})".format(time))

        return mdi_model
