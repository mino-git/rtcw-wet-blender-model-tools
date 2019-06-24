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


class MDIToModel:

    @staticmethod
    def _calc_md3_headers(md3_model, mdi_model):

        # md3_model.header
        ident = md3.MD3Header.ident
        version = md3.MD3Header.version
        name = mdi.to_c_string_padded(mdi_model.name, md3.MD3Header.name_len)
        flags = md3.MD3Header.flags
        num_frames = 0
        if md3_model.surfaces:
            if md3_model.surfaces[0].vertices:
                num_frames = len(md3_model.surfaces[0].vertices)
        elif md3_model.tags:
            num_frames = len(md3_model.tags)
        num_tags = 0
        if md3_model.tags and md3_model.tags[0]:
            num_tags = len(md3_model.tags[0])
        num_surfaces = len(md3_model.surfaces)
        num_skins = 0

        ofs_frame_infos = 0 + md3.MD3Header.format_size
        ofs_tags = ofs_frame_infos + num_frames * md3.MD3FrameInfo.format_size
        ofs_surfaces = ofs_tags + \
            num_frames * num_tags * md3.MD3FrameTag.format_size
        ofs_end = None  # calculated later

        md3_model.header = md3.MD3Header(ident, version, name, flags,
                                         num_frames, num_tags, num_surfaces,
                                         num_skins, ofs_frame_infos, ofs_tags,
                                         ofs_surfaces, ofs_end)

        surfaces_field_len = 0  # to calculate ofs_end

        # md3_surface.header
        for num_surface, md3_surface in enumerate(md3_model.surfaces):

            ident = md3.MD3SurfaceHeader.ident
            name = mdi_model.surfaces[num_surface].name
            name = mdi.to_c_string_padded(name, md3.MD3SurfaceHeader.name_len)
            flags = md3.MD3SurfaceHeader.flags
            num_frames = len(md3_surface.vertices)
            num_shaders = len(md3_surface.shaders)
            num_vertices = 0
            if md3_surface.vertices:
                num_vertices = len(md3_surface.vertices[0])
            num_triangles = len(md3_surface.triangles)
            ofs_triangles = 0 + md3.MD3SurfaceHeader.format_size
            ofs_shaders = ofs_triangles + \
                num_triangles * md3.MD3Triangle.format_size
            ofs_tex_coords = ofs_shaders + \
                num_shaders * md3.MD3Shader.format_size
            ofs_vertices = ofs_tex_coords + \
                num_vertices * md3.MD3TexCoords.format_size
            ofs_end = ofs_vertices + \
                num_frames * num_vertices * md3.MD3FrameVertex.format_size

            md3_surface.header = md3.MD3SurfaceHeader(ident, name, flags,
                                                      num_frames, num_shaders,
                                                      num_vertices,
                                                      num_triangles,
                                                      ofs_triangles,
                                                      ofs_shaders,
                                                      ofs_tex_coords,
                                                      ofs_vertices,
                                                      ofs_end)

            surfaces_field_len += ofs_end

        md3_model.header.ofs_end = ofs_surfaces + surfaces_field_len

    @staticmethod
    def _to_md3_frame_vertices(mdi_model, num_surface, num_frame):

        md3_frame_vertices = []

        mdi_surface = mdi_model.surfaces[num_surface]

        for mdi_morph_vertex in mdi_surface.vertices:

            location = mdi_morph_vertex.locations[num_frame]
            location = location / md3.MD3FrameVertex.location_scale
            location = (int(location[0]), int(location[1]), int(location[2]))

            normal = mdi_morph_vertex.normals[num_frame]
            normal = (0, 0)  # TODO

            md3_frame_vertex = md3.MD3FrameVertex(location, normal)
            md3_frame_vertices.append(md3_frame_vertex)

        return md3_frame_vertices

    @staticmethod
    def _to_md3_tex_coords(mdi_model, num_surface, num_tex_coords):

        mdi_surface = mdi_model.surfaces[num_surface]
        mdi_uv = mdi_surface.uv_map.uvs[num_tex_coords]

        u = mdi_uv.u
        v = 1 - mdi_uv.v
        md3_tex_coords = md3.MD3TexCoords((u, v))

        return md3_tex_coords

    @staticmethod
    def _to_md3_shader(mdi_model, num_surface, num_shader):

        mdi_surface = mdi_model.surfaces[num_surface]
        mdi_shader_path = mdi_surface.shader.paths[num_shader]

        name = mdi.to_c_string_padded(mdi_shader_path.path,
                                      md3.MD3Shader.name_len)
        shader_index = md3.MD3Shader.shader_index
        md3_shader = md3.MD3Shader(name, shader_index)

        return md3_shader

    @staticmethod
    def _to_md3_triangle(mdi_model, num_surface, num_triangle):

        mdi_triangle = mdi_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = mdi_triangle.indices[0]
        index_2 = mdi_triangle.indices[2]
        index_3 = mdi_triangle.indices[1]
        indices = (index_1, index_2, index_3)
        md3_triangle = md3.MD3Triangle(indices)

        return md3_triangle

    @staticmethod
    def _to_md3_surface(mdi_model, num_surface):
        """TODO
        """

        md3_surface = md3.MD3Surface()

        mdi_surface = mdi_model.surfaces[num_surface]

        # md3 triangles
        for num_triangle in range(len(mdi_surface.triangles)):

            md3_triangle = MDIToModel._to_md3_triangle(mdi_model,
                                                       num_surface,
                                                       num_triangle)
            md3_surface.triangles.append(md3_triangle)

        # md3 shaders
        for num_shader in range(len(mdi_surface.shader.paths)):

            md3_shader = MDIToModel._to_md3_shader(mdi_model,
                                                   num_surface,
                                                   num_shader)
            md3_surface.shaders.append(md3_shader)

        # md3 tex coords
        for num_tex_coords in range(len(mdi_surface.uv_map.uvs)):

            md3_tex_coords = MDIToModel._to_md3_tex_coords(mdi_model,
                                                           num_surface,
                                                           num_tex_coords)
            md3_surface.tex_coords.append(md3_tex_coords)

        # md3 frame vertices
        for mdi_morph_vertex in mdi_surface.vertices:

            for num_frame in range(len(mdi_morph_vertex.locations)):

                md3_frame_vertices = \
                    MDIToModel._to_md3_frame_vertices(mdi_model,
                                                      num_surface,
                                                      num_frame)
                md3_surface.vertices.append(md3_frame_vertices)

            break

        return md3_surface

    @staticmethod
    def _to_md3_frame_tags(mdi_model, num_frame):
        """TODO
        """

        md3_frame_tags = []

        for mdi_free_tag in mdi_model.tags:

            name = mdi.to_c_string_padded(mdi_free_tag.name,
                                          md3.MD3FrameTag.name_len)
            location = mdi_free_tag.locations[num_frame].to_tuple()
            orientation = \
                mdi.matrix_to_tuple(mdi_free_tag.orientations[num_frame])

            md3_frame_tag = md3.MD3FrameTag(name, location, orientation)
            md3_frame_tags.append(md3_frame_tag)

        return md3_frame_tags

    @staticmethod
    def _to_md3_frame_info(mdi_model, num_frame):
        """TODO
        """

        mdi_aabb = mdi_model.bounds.aabbs[num_frame]
        mdi_bounding_sphere = mdi_model.bounds.spheres[num_frame]

        min_bound = mdi_aabb.min_bound.to_tuple()
        max_bound = mdi_aabb.max_bound.to_tuple()
        local_origin = mdi_bounding_sphere.origin.to_tuple()
        radius = mdi_bounding_sphere.radius
        name = mdi.to_c_string_padded(md3.MD3FrameInfo.frame_name,
                                      md3.MD3FrameInfo.name_len)

        md3_frame_info = md3.MD3FrameInfo(min_bound, max_bound, local_origin,
                                          radius, name)

        return md3_frame_info

    @staticmethod
    def convert(mdi_model):
        """TODO
        """

        md3_model = md3.MD3()

        # type conversions
        for num_surface, mdi_surface in enumerate(mdi_model.surfaces):

            mdi_surface.uv_map_to_type(mdi.MDIUVMapBijective)
            mdi_surface.shader_to_type(mdi.MDIShaderPaths)
            mdi_surface.vertices_to_type(mdi.MDIMorphVertex, mdi_model)

        mdi_model.tags_to_type(mdi.MDIFreeTag)
        mdi_model.lod_to_type(mdi.MDIDiscreteLOD)

        # md3 frame infos
        for num_frame in range(len(mdi_model.bounds.aabbs)):

            md3_frame_info = MDIToModel._to_md3_frame_info(mdi_model,
                                                           num_frame)
            md3_model.frame_infos.append(md3_frame_info)

        # md3 frame tags
        for mdi_free_tag in mdi_model.tags:

            for num_frame in range(len(mdi_free_tag.locations)):

                md3_frame_tags = MDIToModel._to_md3_frame_tags(mdi_model,
                                                               num_frame)
                md3_model.tags.append(md3_frame_tags)

            break

        # md3 surfaces
        for num_surface in range(len(mdi_model.surfaces)):

            md3_surface = MDIToModel._to_md3_surface(mdi_model, num_surface)
            md3_model.surfaces.append(md3_surface)

        # headers
        MDIToModel._calc_md3_headers(md3_model, mdi_model)

        return md3_model


class ModelToMDI:
    """TODO
    """

    @staticmethod
    def _to_mdi_bounds(md3_model):
        """TODO
        """

        mdi_bounds = mdi.MDIBoundingVolume()

        for md3_frame_info in md3_model.frame_infos:

            # aabb
            min_bound = mathutils.Vector(md3_frame_info.min_bound)
            max_bound = mathutils.Vector(md3_frame_info.max_bound)
            mdi_aabb = mdi.MDIAABB(min_bound, max_bound)
            mdi_bounds.aabbs.append(mdi_aabb)

            # sphere
            origin = mathutils.Vector(md3_frame_info.local_origin)
            radius = md3_frame_info.radius
            mdi_bounding_sphere = mdi.MDIBoundingSphere(origin, radius)
            mdi_bounds.spheres.append(mdi_bounding_sphere)

        return mdi_bounds

    @staticmethod
    def _to_mdi_tag(md3_model, num_tag):
        """TODO
        """

        mdi_tag = mdi.MDIFreeTag()

        # name
        mdi_tag.name = \
            mdi.from_c_string_padded(md3_model.tags[0][num_tag].name)

        for md3_frame_tags in md3_model.tags:

            md3_frame_tag = md3_frame_tags[num_tag]

            # location
            mdi_location = mathutils.Vector(md3_frame_tag.location)
            mdi_tag.locations.append(mdi_location)

            # orientation
            mdi_orientation = mdi.tuple_to_matrix(md3_frame_tag.orientation)
            mdi_tag.orientations.append(mdi_orientation)

        return mdi_tag

    @staticmethod
    def _to_mdi_uv_map(md3_model, num_surface):
        """TODO.
        """

        mdi_uv_map = mdi.MDIUVMapBijective()

        for md3_tex_coords in md3_model.surfaces[num_surface].tex_coords:

            u = md3_tex_coords.tex_coords[0]
            v = 1 - md3_tex_coords.tex_coords[1]

            mdi_uv = mdi.MDIUV(u, v)
            mdi_uv_map.uvs.append(mdi_uv)

        return mdi_uv_map

    @staticmethod
    def _to_mdi_shader(md3_model, num_surface):
        """TODO.
        """

        mdi_shader_paths = mdi.MDIShaderPaths()

        for md3_shader in md3_model.surfaces[num_surface].shaders:

            path = mdi.from_c_string_padded(md3_shader.name)
            mdi_shader_path = mdi.MDIShaderPath(path)
            mdi_shader_paths.paths.append(mdi_shader_path)

        return mdi_shader_paths

    @staticmethod
    def _to_mdi_triangle(md3_model, num_surface, num_triangle):
        """TODO
        """

        md3_triangle = md3_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = md3_triangle.indices[0]
        index_2 = md3_triangle.indices[2]
        index_3 = md3_triangle.indices[1]

        mdi_triangle = mdi.MDITriangle([index_1, index_2, index_3])
        return mdi_triangle

    @staticmethod
    def _to_mdi_morph_vertex(md3_model, num_surface, num_vertex):
        """TODO.
        """

        mdi_morph_vertex = mdi.MDIMorphVertex()

        for md3_frame_vertices in md3_model.surfaces[num_surface].vertices:

            md3_frame_vertex = md3_frame_vertices[num_vertex]

            # location
            x = md3_frame_vertex.location[0]
            y = md3_frame_vertex.location[1]
            z = md3_frame_vertex.location[2]

            x = x * md3.MD3FrameVertex.location_scale
            y = y * md3.MD3FrameVertex.location_scale
            z = z * md3.MD3FrameVertex.location_scale

            location = mathutils.Vector((x, y, z))
            mdi_morph_vertex.locations.append(location)

            # normal
            yaw = md3_frame_vertex.normal[1]
            pitch = md3_frame_vertex.normal[0]

            yaw = yaw * md3.MD3FrameVertex.normal_scale
            pitch = pitch * md3.MD3FrameVertex.normal_scale

            normal = mdi.angles_to_vector(yaw, pitch)
            mdi_morph_vertex.normals.append(normal)

        return mdi_morph_vertex

    @staticmethod
    def _to_mdi_surface(md3_model, num_surface):
        """TODO
        """

        mdi_surface = mdi.MDISurface()

        md3_surface = md3_model.surfaces[num_surface]

        # name
        mdi_surface.name = mdi.from_c_string_padded(md3_surface.header.name)

        # mdi vertices
        for md3_frame_vertices in md3_surface.vertices:

            for num_vertex in range(len(md3_frame_vertices)):

                mdi_morph_vertex = \
                    ModelToMDI._to_mdi_morph_vertex(md3_model,
                                                    num_surface,
                                                    num_vertex)
                mdi_surface.vertices.append(mdi_morph_vertex)

            break

        # mdi triangles
        for num_triangle in range(len(md3_surface.triangles)):

            mdi_triangle = \
                ModelToMDI._to_mdi_triangle(md3_model,
                                            num_surface,
                                            num_triangle)
            mdi_surface.triangles.append(mdi_triangle)

        # mdi shader
        mdi_surface.shader = ModelToMDI._to_mdi_shader(md3_model, num_surface)

        # mdi uv map
        mdi_surface.uv_map = ModelToMDI._to_mdi_uv_map(md3_model, num_surface)

        return mdi_surface

    @staticmethod
    def convert(md3_model, root_frame = 0):
        """TODO
        """

        mdi_model = mdi.MDI()

        mdi_model.name = mdi.from_c_string_padded(md3_model.header.name)
        mdi_model.root_frame = root_frame

        # mdi surfaces
        for num_surface in range(len(md3_model.surfaces)):

            mdi_surface = ModelToMDI._to_mdi_surface(md3_model, num_surface)
            mdi_model.surfaces.append(mdi_surface)

        # mdi skeleton
        # pass

        # mdi tags
        for md3_frame_tags in md3_model.tags:

            for num_tag in range(len(md3_frame_tags)):

                mdi_tag = ModelToMDI._to_mdi_tag(md3_model, num_tag)
                mdi_model.tags.append(mdi_tag)

            break

        # mdi bounding volume
        mdi_model.bounds = ModelToMDI._to_mdi_bounds(md3_model)

        # mdi lod
        mdi_model.lod = mdi.MDIDiscreteLOD()

        return mdi_model
