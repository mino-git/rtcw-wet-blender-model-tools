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


class MDIToModel:

    @staticmethod
    def _calc_mdmmdx_headers(mdx_model, mdm_model, mdi_model):
        """TODO
        """

        # mdx_model.header
        ident = mdx.MDXHeader.ident
        version = mdx.MDXHeader.version
        name = mdi.to_c_string_padded(mdi_model.skeleton.name,
                                      mdx.MDXHeader.name_len)
        num_frames = len(mdx_model.frames)
        num_bones = len(mdx_model.bone_infos)
        ofs_frames = 0 + mdx.MDXHeader.format_size
        ofs_bone_infos = ofs_frames + num_frames * \
            (mdx.MDXFrameInfo.format_size + \
            num_bones * mdx.MDXBoneFrameCompressed.format_size)
        torso_parent_bone = mdi_model.skeleton.torso_parent_bone
        ofs_end = ofs_bone_infos + num_bones * mdx.MDXBoneInfo.format_size

        mdx_model.header = mdx.MDXHeader(ident, version, name, num_frames,
                                         num_bones, ofs_frames, ofs_bone_infos,
                                         torso_parent_bone, ofs_end)

        # mdm_model.header
        ident = mdm.MDMHeader.ident
        version = mdm.MDMHeader.version
        name = mdi.to_c_string_padded(mdi_model.name, mdm.MDMHeader.name_len)
        lod_scale = mdi_model.lod.lod_scale
        lod_bias = mdi_model.lod.lod_bias
        num_surfaces = len(mdm_model.surfaces)
        ofs_surfaces = 0 + mdm.MDMHeader.format_size
        num_tags = len(mdm_model.tags)
        ofs_tags = None  # calculated later
        ofs_end = None  # calculated later

        mdm_model.header = mdm.MDMHeader(ident, version, name, lod_scale,
                                         lod_bias, num_surfaces, ofs_surfaces,
                                         num_tags, ofs_tags, ofs_end)

        # mdm_surface.header
        cur_ofs_header = -mdm.MDMHeader.format_size # used for ofs_header

        for num_surface, mdm_surface in enumerate(mdm_model.surfaces):

            # calc num weights first
            num_weights = 0
            for mdm_vertex in mdm_surface.vertices:
                num_weights = num_weights + len(mdm_vertex.weights)

            ident = mdm.MDMSurfaceHeader.ident
            name = mdi_model.surfaces[num_surface].name
            name = mdi.to_c_string_padded(name, mdm.MDMSurfaceHeader.name_len)
            path = mdi_model.surfaces[num_surface].shader.path
            shader = \
                mdi.to_c_string_padded(path,
                                       mdm.MDMSurfaceHeader.shader_name_len)
            shader_index = mdm.MDMSurfaceHeader.shader_index
            min_lod = mdi_model.lod.min_lods[num_surface]
            ofs_header = cur_ofs_header
            num_vertices = len(mdm_surface.vertices)
            ofs_vertices = 0 + mdm.MDMSurfaceHeader.format_size
            num_triangles = len(mdm_surface.triangles)
            ofs_triangles = ofs_vertices + \
                num_vertices * mdm.MDMVertex.format_size + \
                num_weights * mdm.MDMWeight.format_size
            ofs_collapse_map = ofs_triangles + \
                num_triangles * mdm.MDMTriangle.format_size
            num_bone_refs = len(mdm_surface.bone_refs.bone_refs)
            ofs_bone_refs = ofs_collapse_map + num_vertices * 4
            ofs_end = ofs_bone_refs + num_bone_refs * 4

            mdm_surface.header = \
                mdm.MDMSurfaceHeader(ident, name, shader, shader_index,
                                     min_lod, ofs_header, num_vertices,
                                     ofs_vertices, num_triangles,
                                     ofs_triangles, ofs_collapse_map,
                                     num_bone_refs, ofs_bone_refs, ofs_end)

            cur_ofs_header -= ofs_end

        # calc rest of the header
        surfaces_field_len = 0
        for mdm_surface in mdm_model.surfaces:
            surfaces_field_len += mdm_surface.header.ofs_end
        ofs_tags = ofs_surfaces + surfaces_field_len

        # calc num weights first
        bone_refs_field_len = 0
        for mdm_tag in mdm_model.tags:
            bone_refs_field_len = bone_refs_field_len + \
                                  len(mdm_tag.bone_refs.bone_refs)

        ofs_end = ofs_tags + \
            (num_tags * mdm.MDMTag.format_size + \
            bone_refs_field_len * 4)

        mdm_model.header.ofs_tags = ofs_tags
        mdm_model.header.ofs_end = ofs_end

    @staticmethod
    def _to_mdm_tag(mdi_model, num_tag):
        """TODO
        """

        mdi_bone_tag_off = mdi_model.tags[num_tag]

        name = mdi.to_c_string_padded(mdi_bone_tag_off.name,
                                      mdm.MDMTag.name_len)

        orientation = mdi.matrix_to_tuple(mdi_bone_tag_off.orientation)

        parent_bone = mdi_bone_tag_off.parent_bone

        location = mdi_bone_tag_off.location.to_tuple()

        # bone refs
        bone_refs = mdi_bone_tag_off.calc_bone_refs(mdi_model.skeleton)
        mdm_bone_refs = mdm.MDMBoneRefs(bone_refs)
        num_bone_refs = len(mdm_bone_refs.bone_refs)
        ofs_bone_refs = mdm.MDMTag.format_size
        ofs_end = ofs_bone_refs + num_bone_refs * 4

        mdm_tag = mdm.MDMTag(name, orientation, parent_bone, location,
                             num_bone_refs, ofs_bone_refs, ofs_end)
        mdm_tag.bone_refs = mdm.MDMBoneRefs(bone_refs)

        return mdm_tag

    @staticmethod
    def _to_mdm_bone_refs(mdi_model, num_surface):
        """TODO
        """

        mdi_surface = mdi_model.surfaces[num_surface]

        bone_refs = mdi_surface.calc_bone_refs(mdi_model.skeleton)
        mdm_bone_refs = mdm.MDMBoneRefs(bone_refs)

        return mdm_bone_refs

    @staticmethod
    def _to_mdm_collapse_map(mdi_model, num_surface):
        """TODO
        """

        # TODO check if present, if not calc

        collapse_map = mdi_model.lod.collapses[num_surface]

        mdm_collapse_map = mdm.MDMCollapseMap(collapse_map)

        return mdm_collapse_map

    @staticmethod
    def _to_mdm_triangle(mdi_model, num_surface, num_triangle):
        """TODO
        """

        mdi_triangle = mdi_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = mdi_triangle.indices[0]
        index_2 = mdi_triangle.indices[2]
        index_3 = mdi_triangle.indices[1]
        indices = (index_1, index_2, index_3)
        mdm_triangle = mdm.MDMTriangle(indices)

        return mdm_triangle

    @staticmethod
    def _to_mdm_weight(mdi_model, num_surface, num_vertex, num_weight):
        """TODO
        """

        mdi_rigged_vertex = \
            mdi_model.surfaces[num_surface].vertices[num_vertex]
        mdi_vertex_weight = mdi_rigged_vertex.weights[num_weight]

        bone_index = mdi_vertex_weight.parent_bone
        bone_weight = mdi_vertex_weight.weight_value
        location = mdi_vertex_weight.location.to_tuple()
        mdm_weight = mdm.MDMWeight(bone_index, bone_weight, location)

        return mdm_weight

    @staticmethod
    def _to_mdm_vertex(mdi_model, num_surface, num_vertex):
        """TODO
        """

        mdi_rigged_vertex = \
            mdi_model.surfaces[num_surface].vertices[num_vertex]
        mdi_uv_map = mdi_model.surfaces[num_surface].uv_map

        normal = mdi_rigged_vertex.normal.to_tuple()
        tex_coords = (mdi_uv_map.uvs[num_vertex].u,
                      1 - mdi_uv_map.uvs[num_vertex].v)
        num_weights = 0  # calculated later

        mdm_vertex = mdm.MDMVertex(normal, tex_coords, num_weights)

        # weights
        for num_weight in range(len(mdi_rigged_vertex.weights)):

            mdm_weight = \
                MDIToModel._to_mdm_weight(mdi_model, num_surface, num_vertex,
                                          num_weight)
            mdm_vertex.weights.append(mdm_weight)

        mdm_vertex.num_weights = len(mdm_vertex.weights)

        return mdm_vertex

    @staticmethod
    def _to_mdm_surface(mdi_model, num_surface):
        """TODO
        """

        mdm_surface = mdm.MDMSurface()

        mdi_surface = mdi_model.surfaces[num_surface]

        # mdm vertices
        for num_vertex in range(len(mdi_surface.vertices)):

            mdm_vertex = MDIToModel._to_mdm_vertex(mdi_model, num_surface,
                                                   num_vertex)
            mdm_surface.vertices.append(mdm_vertex)

        # mdm triangles
        for num_triangle in range(len(mdi_surface.triangles)):

            mdm_triangle = MDIToModel._to_mdm_triangle(mdi_model, num_surface,
                                                       num_triangle)
            mdm_surface.triangles.append(mdm_triangle)

        # mdm collapse map
        mdm_surface.collapse_map = \
            MDIToModel._to_mdm_collapse_map(mdi_model, num_surface)

        # mdm bone refs
        mdm_surface.bone_refs = \
            MDIToModel._to_mdm_bone_refs(mdi_model, num_surface)

        return mdm_surface

    @staticmethod
    def _to_mdx_bone_info(mdi_model, num_bone):
        """TODO
        """

        mdi_bone = mdi_model.skeleton.bones[num_bone]

        name = mdi.to_c_string_padded(mdi_bone.name, mdx.MDXBoneInfo.name_len)
        parent_bone = mdi_bone.parent_bone
        torso_weight = mdi_bone.torso_weight
        parent_dist = mdi_bone.parent_dist
        flags = mdx.MDXBoneInfo.flags_default_value

        mdx_bone_info = mdx.MDXBoneInfo(name, parent_bone, torso_weight,
                                        parent_dist, flags)

        return mdx_bone_info

    @staticmethod
    def _to_mdx_bone_frame_compressed(mdi_model, num_frame, num_bone):
        """TODO
        """

        mdi_bone = mdi_model.skeleton.bones[num_bone]

        # orientation
        orientation = mdi_bone.orientations[num_frame]

        yaw, pitch, roll = \
            mdi.matrix_to_angles(orientation)

        scale = mdx.MDXBoneFrameCompressed.orientation_scale
        yaw = int(yaw / scale)
        pitch = int(pitch / scale)
        roll = int(roll / scale)

        orientation = (pitch, yaw, roll,
                       mdx.MDXBoneFrameCompressed.angle_none_default)

        # location dir
        has_bone_parent = True
        if mdi_bone.parent_bone < 0:
            has_bone_parent = False

        yaw = 0
        pitch = 0

        if has_bone_parent:

            mdi_parent_bone = mdi_model.skeleton.bones[mdi_bone.parent_bone]

            location_diff = mdi_bone.locations[num_frame] - \
                mdi_parent_bone.locations[num_frame]
            yaw, pitch = mdi.vector_to_angles(location_diff.normalized())

            scale = mdx.MDXBoneFrameCompressed.location_dir_scale
            yaw = int(yaw / scale) << 4
            pitch = int(pitch / scale) << 4

        else:

            pass  # root bone always is 0, 0

        location_dir = (pitch, yaw)

        mdx_bone_frame_compressed = \
            mdx.MDXBoneFrameCompressed(orientation, location_dir)

        return mdx_bone_frame_compressed

    @staticmethod
    def _to_mdx_frame_info(mdi_model, num_frame):
        """TODO
        """

        mdi_aabb = mdi_model.bounds.aabbs[num_frame]
        mdi_bounding_sphere = mdi_model.bounds.spheres[num_frame]

        min_bound = mdi_aabb.min_bound.to_tuple()
        max_bound = mdi_aabb.max_bound.to_tuple()
        local_origin = mdi_bounding_sphere.origin.to_tuple()
        radius = mdi_bounding_sphere.radius
        root_bone_location = \
            mdi_model.skeleton.root_bone_locations[num_frame].to_tuple()

        mdx_frame_info = mdx.MDXFrameInfo(min_bound, max_bound, local_origin,
                                          radius, root_bone_location)

        return mdx_frame_info

    @staticmethod
    def _to_mdx_frame(mdi_model, num_frame):
        """TODO
        """

        mdx_frame = mdx.MDXFrame()

        mdx_frame.frame_info = MDIToModel._to_mdx_frame_info(mdi_model,
                                                             num_frame)

        for num_bone in range(len(mdi_model.skeleton.bones)):

            mdx_bone_frame_compressed = \
                MDIToModel._to_mdx_bone_frame_compressed(mdi_model, num_frame,
                                                         num_bone)
            mdx_frame.bone_frames_compressed.append(mdx_bone_frame_compressed)

        return mdx_frame

    @staticmethod
    def convert(mdi_model):

        mdx_model = mdx.MDX()
        mdm_model = mdm.MDM()

        # type conversions
        for num_surface, mdi_surface in enumerate(mdi_model.surfaces):

            mdi_surface.uv_map_to_type(mdi.MDIUVMapBijective)
            mdi_surface.shader_to_type(mdi.MDIShaderPath)
            mdi_surface.vertices_to_type(mdi.MDIRiggedVertex, mdi_model)

        mdi_model.tags_to_type(mdi.MDIBoneTagOff)
        mdi_model.lod_to_type(mdi.MDICollapseMap)

        # mdx frames
        for num_frame in range(len(mdi_model.bounds.aabbs)):

            mdx_frame = MDIToModel._to_mdx_frame(mdi_model, num_frame)
            mdx_model.frames.append(mdx_frame)

        # mdx bone infos
        for num_bone in range(len(mdi_model.skeleton.bones)):

            mdx_bone_info = MDIToModel._to_mdx_bone_info(mdi_model, num_bone)
            mdx_model.bone_infos.append(mdx_bone_info)

        # mdm surfaces
        for num_surface in range(len(mdi_model.surfaces)):

            mdm_surface = MDIToModel._to_mdm_surface(mdi_model, num_surface)
            mdm_model.surfaces.append(mdm_surface)

        # mdm tags
        for num_tag in range(len(mdi_model.tags)):

            mdm_tag = MDIToModel._to_mdm_tag(mdi_model, num_tag)
            mdm_model.tags.append(mdm_tag)

        # headers
        MDIToModel._calc_mdmmdx_headers(mdx_model, mdm_model, mdi_model)

        return (mdx_model, mdm_model)


class ModelToMDI:

    @staticmethod
    def _to_mdi_lod(mdm_model, collapse_frame = None):
        """TODO
        """

        mdi_collapse_map = mdi.MDICollapseMap()

        mdi_collapse_map.collapse_frame = collapse_frame
        mdi_collapse_map.lod_scale = mdm_model.header.lod_scale
        mdi_collapse_map.lod_bias = mdm_model.header.lod_bias

        for mdm_surface in mdm_model.surfaces:

            mdi_collapse_map.min_lods.append(mdm_surface.header.min_lod)

            surface_mappings = []
            for mapping in mdm_surface.collapse_map.mappings:

                surface_mappings.append(mapping)

            mdi_collapse_map.collapses.append(surface_mappings)

        return mdi_collapse_map

    @staticmethod
    def _to_mdi_bounds(mdx_model):
        """TODO
        """

        mdi_bounds = mdi.MDIBoundingVolume()

        for mdx_frame in mdx_model.frames:

            mdx_frame_info = mdx_frame.frame_info

            # aabb
            min_bound = mathutils.Vector(mdx_frame_info.min_bound)
            max_bound = mathutils.Vector(mdx_frame_info.max_bound)
            mdi_aabb = mdi.MDIAABB(min_bound, max_bound)
            mdi_bounds.aabbs.append(mdi_aabb)

            # sphere
            origin = mathutils.Vector(mdx_frame_info.local_origin)
            radius = mdx_frame_info.radius
            mdi_bounding_sphere = mdi.MDIBoundingSphere(origin, radius)
            mdi_bounds.spheres.append(mdi_bounding_sphere)

        return mdi_bounds

    @staticmethod
    def _to_mdi_tag(mdm_model, num_tag, mdi_model):
        """TODO
        """

        mdi_bone_tag_off = mdi.MDIBoneTagOff()

        mdm_tag = mdm_model.tags[num_tag]

        mdi_bone_tag_off.name = mdi.from_c_string_padded(mdm_tag.name)
        mdi_bone_tag_off.parent_bone = mdm_tag.parent_bone

        # mdi_parent_bone = mdi_model.skeleton.bones[mdm_tag.parent_bone]

        # # location
        # mdi_bone_tag_off.location = \
        #     mdi_parent_bone.locations[mdi_model.root_frame] + \
        #     (mdi_parent_bone.orientations[mdi_model.root_frame] @ \
        #     mathutils.Vector(mdm_tag.location))

        # # orientation
        # orientation_offset = mdi.tuple_to_matrix(mdm_tag.orientation)
        # mdi_bone_tag_off.orientation = \
        #     mdi_parent_bone.orientations[mdi_model.root_frame] @ \
        #     orientation_offset

        mdi_bone_tag_off.location = mathutils.Vector(mdm_tag.location)

        mdi_bone_tag_off.orientation = mdi.tuple_to_matrix(mdm_tag.orientation)

        return mdi_bone_tag_off

    @staticmethod
    def _to_mdi_skeleton(mdx_model):
        """TODO
        """

        mdi_skeleton = mdi.MDISkeleton()

        mdi_skeleton.name = "mdx_skeleton"
        mdi_skeleton.torso_parent_bone = mdx_model.header.torso_parent_bone

        # root bone locations
        root_bone_locations = []
        for mdx_frame in mdx_model.frames:

            root_bone_location = \
                mathutils.Vector(mdx_frame.frame_info.root_bone_location)
            root_bone_locations.append(root_bone_location)

        mdi_skeleton.root_bone_locations = root_bone_locations

        # bones
        for num_bone, mdx_bone_info in enumerate(mdx_model.bone_infos):

            mdi_bone = mdi.MDIBone()

            mdi_bone.name = mdi.from_c_string_padded(mdx_bone_info.name)
            mdi_bone.parent_bone = mdx_bone_info.parent_bone
            mdi_bone.parent_dist = mdx_bone_info.parent_dist
            mdi_bone.torso_weight = mdx_bone_info.torso_weight

            # bone locations
            has_bone_parent = True
            if mdx_bone_info.parent_bone < 0:
                has_bone_parent = False

            if has_bone_parent:  # relies on already calculated mdi_bone_parent

                mdi_bone_parent = \
                    mdi_skeleton.bones[mdx_bone_info.parent_bone]

                for num_frame, mdx_frame in enumerate(mdx_model.frames):

                    # location_dir
                    mdx_bone_frame_compressed = \
                        mdx_frame.bone_frames_compressed[num_bone]

                    yaw = mdx_bone_frame_compressed.location_dir[1]
                    pitch = mdx_bone_frame_compressed.location_dir[0]

                    scale = mdx.MDXBoneFrameCompressed.location_dir_scale
                    yaw = (yaw >> 4) * scale  # TODO why bitshift?
                    pitch = (pitch >> 4) * scale

                    location_dir = mdi.angles_to_vector(yaw, pitch)
                    location_dir = mathutils.Vector(location_dir)

                    # parent_dist
                    parent_dist = mdx_bone_info.parent_dist

                    # parent_location
                    parent_location = mdi_bone_parent.locations[num_frame]

                    location = parent_location + (parent_dist * location_dir)

                    mdi_bone.locations.append(location)

            else:  # root bone

                for num_frame, mdx_frame in enumerate(mdx_model.frames):

                    mdx_frame_info = mdx_frame.frame_info

                    location = \
                        mathutils.Vector(mdx_frame_info.root_bone_location)
                    mdi_bone.locations.append(location)

            # bone orientations
            for num_frame, mdx_frame in enumerate(mdx_model.frames):

                mdx_bone_frame_compressed = \
                    mdx_frame.bone_frames_compressed[num_bone]

                yaw = mdx_bone_frame_compressed.orientation[1]
                pitch = mdx_bone_frame_compressed.orientation[0]
                roll = mdx_bone_frame_compressed.orientation[2]

                # short to float
                scale = mdx.MDXBoneFrameCompressed.orientation_scale

                yaw = yaw * scale
                pitch = pitch * scale
                roll = roll * scale

                # to matrix
                orientation = mdi.angles_to_matrix(yaw, pitch, roll)

                if mdx_model.bone_infos[num_bone].flags == 1:
                    orientation = orientation.transposed()

                mdi_bone.orientations.append(orientation)

            mdi_skeleton.bones.append(mdi_bone)

        return mdi_skeleton

    @staticmethod
    def _to_mdi_uv_map(mdm_model, num_surface):
        """TODO.
        """

        mdi_uv_map = mdi.MDIUVMapBijective()

        for mdm_vertex in mdm_model.surfaces[num_surface].vertices:

            u = mdm_vertex.tex_coords[0]
            v = 1 - mdm_vertex.tex_coords[1]

            mdi_uv = mdi.MDIUV(u, v)
            mdi_uv_map.uvs.append(mdi_uv)

        return mdi_uv_map

    @staticmethod
    def _to_mdi_shader(mdm_model, num_surface):
        """TODO.
        """

        mdi_shader_path = mdi.MDIShaderPath()

        path = mdm_model.surfaces[num_surface].header.shader
        mdi_shader_path.path = mdi.from_c_string_padded(path)

        return mdi_shader_path

    @staticmethod
    def _to_mdi_triangle(mdm_model, num_surface, num_triangle):
        """TODO
        """

        mdm_triangle = mdm_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = mdm_triangle.indices[0]
        index_2 = mdm_triangle.indices[2]
        index_3 = mdm_triangle.indices[1]

        mdi_triangle = mdi.MDITriangle([index_1, index_2, index_3])
        return mdi_triangle

    @staticmethod
    def _to_mdi_rigged_vertex(mdm_model, num_surface, num_vertex):
        """TODO.
        """

        mdi_rigged_vertex = mdi.MDIRiggedVertex()

        mdm_vertex = mdm_model.surfaces[num_surface].vertices[num_vertex]

        mdi_rigged_vertex.normal = mathutils.Vector(mdm_vertex.normal)

        for mdm_weight in mdm_vertex.weights:

            mdi_vertex_weight = mdi.MDIVertexWeight()

            mdi_vertex_weight.parent_bone = mdm_weight.bone_index
            mdi_vertex_weight.weight_value = mdm_weight.bone_weight
            mdi_vertex_weight.location = mathutils.Vector(mdm_weight.location)

            mdi_rigged_vertex.weights.append(mdi_vertex_weight)

        return mdi_rigged_vertex

    @staticmethod
    def _to_mdi_surface(mdm_model, num_surface):
        """TODO
        """

        mdi_surface = mdi.MDISurface()

        mdm_surface = mdm_model.surfaces[num_surface]

        # name
        mdi_surface.name = mdi.from_c_string_padded(mdm_surface.header.name)

        # mdi vertices
        for num_vertex in range(len(mdm_surface.vertices)):

            mdi_rigged_vertex = \
                ModelToMDI._to_mdi_rigged_vertex(mdm_model,
                                                 num_surface,
                                                 num_vertex)
            mdi_surface.vertices.append(mdi_rigged_vertex)

        # mdi triangles
        for num_triangle in range(len(mdm_surface.triangles)):

            mdi_triangle = \
                ModelToMDI._to_mdi_triangle(mdm_model,
                                            num_surface,
                                            num_triangle)
            mdi_surface.triangles.append(mdi_triangle)

        # mdi shader
        mdi_surface.shader = ModelToMDI._to_mdi_shader(mdm_model, num_surface)

        # mdi uv map
        mdi_surface.uv_map = ModelToMDI._to_mdi_uv_map(mdm_model, num_surface)

        return mdi_surface

    @staticmethod
    def convert(mdx_model, mdm_model, root_frame = 0):

        mdi_model = mdi.MDI()

        mdi_model.name = mdi.from_c_string_padded(mdm_model.header.name)
        mdi_model.root_frame = root_frame

        # mdi surfaces
        for num_surface in range(len(mdm_model.surfaces)):

            mdi_surface = ModelToMDI._to_mdi_surface(mdm_model, num_surface)
            mdi_model.surfaces.append(mdi_surface)

        # mdi skeleton
        mdi_model.skeleton = ModelToMDI._to_mdi_skeleton(mdx_model)

        # mdi tags
        for num_tag in range(len(mdm_model.tags)):

            mdi_tag = ModelToMDI._to_mdi_tag(mdm_model, num_tag, mdi_model)
            mdi_model.tags.append(mdi_tag)

        # mdi bounding volume
        mdi_model.bounds = ModelToMDI._to_mdi_bounds(mdx_model)

        # mdi lod
        mdi_model.lod = ModelToMDI._to_mdi_lod(mdm_model)

        return mdi_model
