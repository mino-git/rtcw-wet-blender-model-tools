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

import rtcw_et_model_tools.mds._mds as mds_m
import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.mdi.util as mdi_util_m
import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


class MDIToModel:
    """MDI to MDS conversion.
    """

    @staticmethod
    def _calc_mds_headers(mds_model, mdi_model):

        # mds_model.header
        ident = mds_m.MDSHeader.ident
        version = mds_m.MDSHeader.version
        name = \
            mdi_util_m.to_c_string_padded(mdi_model.name,
                                          mds_m.MDSHeader.name_len)
        lod_scale = mdi_model.lod.lod_scale
        lod_bias = mdi_model.lod.lod_bias
        num_frames = len(mds_model.frames)
        num_bones = len(mds_model.bone_infos)

        ofs_frames = 0 + mds_m.MDSHeader.format_size
        ofs_bone_infos = ofs_frames + num_frames * \
            (mds_m.MDSFrameInfo.format_size + \
            num_bones * mds_m.MDSBoneFrameCompressed.format_size)
        torso_parent_bone = mdi_model.skeleton.torso_parent_bone
        num_surfaces = len(mds_model.surfaces)
        ofs_surfaces = ofs_bone_infos + num_bones * mds_m.MDSBoneInfo.format_size
        num_tags = len(mds_model.tags)
        ofs_tags = None  # calculated later
        ofs_end = None  # calculated later

        mds_model.header = mds_m.MDSHeader(ident, version, name, lod_scale,
                                           lod_bias, num_frames, num_bones,
                                           ofs_frames, ofs_bone_infos,
                                           torso_parent_bone, num_surfaces,
                                           ofs_surfaces, num_tags, ofs_tags,
                                           ofs_end)

        cur_ofs_header = -mds_model.header.ofs_surfaces # used for ofs_header

        # mds_surface.header
        for num_surface, mds_surface in enumerate(mds_model.surfaces):

            # calc num weights first
            num_weights = 0
            for mds_vertex in mds_surface.vertices:
                num_weights = num_weights + len(mds_vertex.weights)

            ident = mds_m.MDSSurfaceHeader.ident
            name = mdi_model.surfaces[num_surface].name
            name = \
                mdi_util_m.to_c_string_padded(name,
                                              mds_m.MDSSurfaceHeader.name_len)
            path = mdi_model.surfaces[num_surface].shader.path
            shader = \
                mdi_util_m.to_c_string_padded(path,
                                        mds_m.MDSSurfaceHeader.shader_name_len)
            shader_index = mds_m.MDSSurfaceHeader.shader_index
            min_lod = mdi_model.lod.min_lods[num_surface]
            ofs_header = cur_ofs_header
            num_vertices = len(mds_surface.vertices)
            ofs_vertices = 0 + mds_m.MDSSurfaceHeader.format_size
            num_triangles = len(mds_surface.triangles)
            ofs_triangles = ofs_vertices + \
                num_vertices * mds_m.MDSVertex.format_size + \
                num_weights * mds_m.MDSWeight.format_size
            ofs_collapse_map = ofs_triangles + \
                num_triangles * mds_m.MDSTriangle.format_size
            num_bone_refs = len(mds_surface.bone_refs.bone_refs)
            ofs_bone_refs = ofs_collapse_map + num_vertices * 4
            ofs_end = ofs_bone_refs + num_bone_refs * 4

            mds_surface.header = \
                mds_m.MDSSurfaceHeader(ident, name, shader, shader_index,
                                       min_lod, ofs_header, num_vertices,
                                       ofs_vertices, num_triangles,
                                       ofs_triangles, ofs_collapse_map,
                                       num_bone_refs, ofs_bone_refs, ofs_end)

            cur_ofs_header -= ofs_end

        # calc rest of the header
        surfaces_field_len = 0
        for mds_surface in mds_model.surfaces:
            surfaces_field_len += mds_surface.header.ofs_end
        ofs_tags = ofs_surfaces + surfaces_field_len
        ofs_end = ofs_tags + num_tags * mds_m.MDSTag.format_size

        mds_model.header.ofs_tags = ofs_tags
        mds_model.header.ofs_end = ofs_end

    @staticmethod
    def _to_mds_tag(mdi_model, num_tag):

        mdi_bone_tag = mdi_model.tags[num_tag]

        name = \
            mdi_util_m.to_c_string_padded(mdi_bone_tag.name,
                                          mds_m.MDSTag.name_len)

        if mdi_bone_tag.torso_weight is None:
            torso_weight = 0.0
            reporter_m.warning("'Torso Weight' property not set on tag '{}'."
                               " Defaulting to '{}'."
                               .format(mdi_bone_tag.name, torso_weight))
        else:
            torso_weight = mdi_bone_tag.torso_weight

        parent_bone = mdi_bone_tag.parent_bone

        mds_tag = mds_m.MDSTag(name, torso_weight, parent_bone)

        return mds_tag

    @staticmethod
    def _to_mds_bone_refs(mdi_model, num_surface):

        mdi_surface = mdi_model.surfaces[num_surface]

        bone_refs = mdi_surface.calc_bone_refs(mdi_model.skeleton)
        mds_bone_refs = mds_m.MDSBoneRefs(bone_refs)

        return mds_bone_refs

    @staticmethod
    def _to_mds_collapse_map(mdi_model, num_surface):

        collapse_map = mdi_model.lod.collapses[num_surface]

        mds_collapse_map = mds_m.MDSCollapseMap(collapse_map)

        return mds_collapse_map

    @staticmethod
    def _to_mds_triangle(mdi_model, num_surface, num_triangle):

        mdi_triangle = mdi_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = mdi_triangle.indices[0]
        index_2 = mdi_triangle.indices[2]
        index_3 = mdi_triangle.indices[1]
        indices = (index_1, index_2, index_3)
        mds_triangle = mds_m.MDSTriangle(indices)

        return mds_triangle

    @staticmethod
    def _to_mds_weight(mdi_model, num_surface, num_vertex, num_weight):

        mdi_rigged_vertex = \
            mdi_model.surfaces[num_surface].vertices[num_vertex]
        mdi_vertex_weight = mdi_rigged_vertex.weights[num_weight]

        bone_index = mdi_vertex_weight.parent_bone
        bone_weight = mdi_vertex_weight.weight_value
        location = mdi_vertex_weight.location.to_tuple()
        mds_weight = mds_m.MDSWeight(bone_index, bone_weight, location)

        return mds_weight

    @staticmethod
    def _to_mds_vertex(mdi_model, num_surface, num_vertex):

        mdi_rigged_vertex = \
            mdi_model.surfaces[num_surface].vertices[num_vertex]
        mdi_uv_map = mdi_model.surfaces[num_surface].uv_map

        normal = mdi_rigged_vertex.normal.to_tuple()
        tex_coords = (mdi_uv_map.uvs[num_vertex].u,
                      1 - mdi_uv_map.uvs[num_vertex].v)
        fixed_parent = mds_m.MDSVertex.fixed_parent_default
        fixed_dist = mds_m.MDSVertex.fixed_dist_default
        num_weights = 0  # calculated later

        mds_vertex = mds_m.MDSVertex(normal, tex_coords, num_weights,
                                     fixed_parent, fixed_dist)

        # weights
        for num_weight in range(len(mdi_rigged_vertex.weights)):

            mds_weight = \
                MDIToModel._to_mds_weight(mdi_model, num_surface, num_vertex,
                                          num_weight)
            mds_vertex.weights.append(mds_weight)

        mds_vertex.num_weights = len(mds_vertex.weights)

        return mds_vertex

    @staticmethod
    def _to_mds_surface(mdi_model, num_surface):

        mds_surface = mds_m.MDSSurface()

        mdi_surface = mdi_model.surfaces[num_surface]

        # mds vertices
        for num_vertex in range(len(mdi_surface.vertices)):

            mds_vertex = MDIToModel._to_mds_vertex(mdi_model, num_surface,
                                                   num_vertex)
            mds_surface.vertices.append(mds_vertex)

        # mds triangles
        for num_triangle in range(len(mdi_surface.triangles)):

            mds_triangle = MDIToModel._to_mds_triangle(mdi_model, num_surface,
                                                       num_triangle)
            mds_surface.triangles.append(mds_triangle)

        # mds collapse map
        mds_surface.collapse_map = \
            MDIToModel._to_mds_collapse_map(mdi_model, num_surface)

        # mds bone refs
        mds_surface.bone_refs = \
            MDIToModel._to_mds_bone_refs(mdi_model, num_surface)

        return mds_surface

    @staticmethod
    def _to_mds_bone_info(mdi_model, num_bone):

        mdi_bone = mdi_model.skeleton.bones[num_bone]

        name = \
            mdi_util_m.to_c_string_padded(mdi_bone.name,
                                          mds_m.MDSBoneInfo.name_len)
        parent_bone = mdi_bone.parent_bone

        if mdi_bone.torso_weight is None:
            torso_weight = 0.0
            reporter_m.warning("'Torso Weight' property not set on bone '{}'."
                               " Defaulting to '{}'."
                               .format(mdi_bone.name, torso_weight))
        else:
            torso_weight = mdi_bone.torso_weight

        parent_dist = mdi_bone.parent_dist
        
        if mdi_bone.name.startswith("tag_"):
            flags = mds_m.MDSBoneInfo.bone_flag_tag
        else:
            flags = mds_m.MDSBoneInfo.flags_default_value            

        mds_bone_info = mds_m.MDSBoneInfo(name, parent_bone, torso_weight,
                                          parent_dist, flags)

        return mds_bone_info

    @staticmethod
    def _to_mds_bone_frame_compressed(mdi_model, num_frame, num_bone):

        mdi_bone = mdi_model.skeleton.bones[num_bone]

        # orientation
        orientation = mdi_bone.orientations[num_frame]

        if mdi_bone.name.startswith("tag_"): # TODO add flag tag to mdi?
            orientation = orientation.transposed()

        yaw, pitch, roll = mdi_util_m.matrix_to_angles(orientation)

        scale = mds_m.MDSBoneFrameCompressed.orientation_scale
        yaw = int(yaw / scale)
        pitch = int(pitch / scale)
        roll = int(roll / scale)

        orientation = (pitch, yaw, roll,
                       mds_m.MDSBoneFrameCompressed.angle_none_default)

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
            yaw, pitch = mdi_util_m.angles_from_forward_vector \
                         (
                            location_diff.normalized()
                         )

            scale = mds_m.MDSBoneFrameCompressed.location_dir_scale
            yaw = int(yaw / scale) << 4
            pitch = int(pitch / scale) << 4

        else:

            pass  # root bone always is 0, 0

        location_dir = (yaw, pitch)

        mds_bone_frame_compressed = \
            mds_m.MDSBoneFrameCompressed(orientation, location_dir)

        return mds_bone_frame_compressed

    @staticmethod
    def _to_mds_frame_info(mdi_model, num_frame):

        mdi_aabb = mdi_model.bounds.aabbs[num_frame]
        mdi_bounding_sphere = mdi_model.bounds.spheres[num_frame]

        min_bound = mdi_aabb.min_bound.to_tuple()
        max_bound = mdi_aabb.max_bound.to_tuple()
        local_origin = mdi_bounding_sphere.origin.to_tuple()
        radius = mdi_bounding_sphere.radius
        root_bone_location = \
            mdi_model.skeleton.bones[0].locations[num_frame].to_tuple()

        mds_frame_info = mds_m.MDSFrameInfo(min_bound, max_bound, local_origin,
                                            radius, root_bone_location)

        return mds_frame_info

    @staticmethod
    def _to_mds_frame(mdi_model, num_frame):

        mds_frame = mds_m.MDSFrame()

        mds_frame.frame_info = MDIToModel._to_mds_frame_info(mdi_model,
                                                             num_frame)

        for num_bone in range(len(mdi_model.skeleton.bones)):

            mds_bone_frame_compressed = \
                MDIToModel._to_mds_bone_frame_compressed(mdi_model, num_frame,
                                                         num_bone)
            mds_frame.bone_frames_compressed.append(mds_bone_frame_compressed)

        return mds_frame

    @staticmethod
    def convert(mdi_model, collapse_frame):
        """Converts MDI to MDS.

        Args:

            mdi_model (MDI): MDI model.

        Returns:

            mds_model (MDS): MDS model.
        """

        timer = timer_m.Timer()
        reporter_m.info("Converting MDI to MDS ...")

        mds_model = mds_m.MDS()

        # type conversions
        for num_surface, mdi_surface in enumerate(mdi_model.surfaces):

            mdi_surface.uv_map_to_type(mdi_m.MDIUVMapBijective)
            mdi_surface.shader_to_type(mdi_m.MDIShaderPath)
            mdi_surface.vertices_to_type(mdi_m.MDIRiggedVertex, mdi_model)

        mdi_model.tags_to_type(mdi_m.MDIBoneTag)
        mdi_model.lod_to_type(mdi_m.MDICollapseMap, collapse_frame)

        # mds frames
        for num_frame in range(len(mdi_model.bounds.aabbs)):

            mds_frame = MDIToModel._to_mds_frame(mdi_model, num_frame)
            mds_model.frames.append(mds_frame)

        # mds bone infos
        for num_bone in range(len(mdi_model.skeleton.bones)):

            mds_bone_info = MDIToModel._to_mds_bone_info(mdi_model, num_bone)
            mds_model.bone_infos.append(mds_bone_info)

        # mds surfaces
        for num_surface in range(len(mdi_model.surfaces)):

            mds_surface = MDIToModel._to_mds_surface(mdi_model, num_surface)
            mds_model.surfaces.append(mds_surface)

        # mds tags
        for num_tag in range(len(mdi_model.tags)):

            mds_tag = MDIToModel._to_mds_tag(mdi_model, num_tag)
            mds_model.tags.append(mds_tag)

        # headers
        MDIToModel._calc_mds_headers(mds_model, mdi_model)

        time = timer.time()
        reporter_m.info("Converting MDI to MDS DONE (time={})".format(time))

        return mds_model


class ModelToMDI:
    """MDS to MDI conversion.
    """

    @staticmethod
    def _to_mdi_lod(mds_model, collapse_frame = None):

        mdi_collapse_map = mdi_m.MDICollapseMap()

        mdi_collapse_map.collapse_frame = collapse_frame
        mdi_collapse_map.lod_scale = mds_model.header.lod_scale
        mdi_collapse_map.lod_bias = mds_model.header.lod_bias

        for mds_surface in mds_model.surfaces:

            mdi_collapse_map.min_lods.append(mds_surface.header.min_lod)

            mappings = []
            for mapping in mds_surface.collapse_map.mappings:

                mappings.append(mapping)

            mdi_collapse_map.collapses.append(mappings)

        return mdi_collapse_map

    @staticmethod
    def _to_mdi_bounds(mds_model):

        mdi_bounds = mdi_m.MDIBoundingVolume()

        for mds_frame in mds_model.frames:

            mds_frame_info = mds_frame.frame_info

            # aabb
            min_bound = mathutils.Vector(mds_frame_info.min_bound)
            max_bound = mathutils.Vector(mds_frame_info.max_bound)
            mdi_aabb = mdi_m.MDIAABB(min_bound, max_bound)
            mdi_bounds.aabbs.append(mdi_aabb)

            # sphere
            origin = mathutils.Vector(mds_frame_info.local_origin)
            radius = mds_frame_info.radius
            mdi_bounding_sphere = mdi_m.MDIBoundingSphere(origin, radius)
            mdi_bounds.spheres.append(mdi_bounding_sphere)

        return mdi_bounds

    @staticmethod
    def _to_mdi_tag(mds_model, num_tag):

        mdi_bone_tag = mdi_m.MDIBoneTag()

        mds_tag = mds_model.tags[num_tag]

        mdi_bone_tag.name = mdi_util_m.from_c_string_padded(mds_tag.name)
        mdi_bone_tag.parent_bone = mds_tag.parent_bone
        mdi_bone_tag.torso_weight = mds_tag.torso_weight

        return mdi_bone_tag

    @staticmethod
    def _to_mdi_skeleton(mds_model):

        mdi_skeleton = mdi_m.MDISkeleton()

        mdi_skeleton.name = "mds_skeleton"
        mdi_skeleton.torso_parent_bone = mds_model.header.torso_parent_bone

        # bones
        for num_bone, mds_bone_info in enumerate(mds_model.bone_infos):

            mdi_bone = mdi_m.MDIBone()

            mdi_bone.name = mdi_util_m.from_c_string_padded(mds_bone_info.name)
            mdi_bone.parent_bone = mds_bone_info.parent_bone
            mdi_bone.parent_dist = mds_bone_info.parent_dist
            mdi_bone.torso_weight = mds_bone_info.torso_weight

            # bone locations
            has_bone_parent = True
            if mds_bone_info.parent_bone < 0:
                has_bone_parent = False

            if has_bone_parent:  # relies on already calculated mdi_bone_parent

                mdi_bone_parent = \
                    mdi_skeleton.bones[mds_bone_info.parent_bone]

                for num_frame, mds_frame in enumerate(mds_model.frames):

                    # location_dir
                    mds_bone_frame_compressed = \
                        mds_frame.bone_frames_compressed[num_bone]

                    yaw = mds_bone_frame_compressed.location_dir[0]
                    pitch = mds_bone_frame_compressed.location_dir[1]

                    scale = mds_m.MDSBoneFrameCompressed.location_dir_scale
                    yaw = (yaw >> 4) * scale  # TODO why bitshift?
                    pitch = (pitch >> 4) * scale

                    location_dir = mdi_util_m.rotate_forward_vector(yaw, pitch)
                    location_dir = mathutils.Vector(location_dir)

                    # parent_dist
                    parent_dist = mds_bone_info.parent_dist

                    # parent_location
                    parent_location = mdi_bone_parent.locations[num_frame]

                    location = parent_location + (parent_dist * location_dir)

                    mdi_bone.locations.append(location)

            else:  # root bone

                for num_frame, mds_frame in enumerate(mds_model.frames):

                    mds_frame_info = mds_frame.frame_info

                    location = \
                        mathutils.Vector(mds_frame_info.root_bone_location)
                    mdi_bone.locations.append(location)

            # bone orientations
            for num_frame, mds_frame in enumerate(mds_model.frames):

                mds_bone_frame_compressed = \
                    mds_frame.bone_frames_compressed[num_bone]

                yaw = mds_bone_frame_compressed.orientation[1]
                pitch = mds_bone_frame_compressed.orientation[0]
                roll = mds_bone_frame_compressed.orientation[2]

                # short to float
                scale = mds_m.MDSBoneFrameCompressed.orientation_scale

                yaw = yaw * scale
                pitch = pitch * scale
                roll = roll * scale

                # to matrix
                orientation = mdi_util_m.angles_to_matrix(yaw, pitch, roll)

                if mds_model.bone_infos[num_bone].flags == 1:  # TODO explain
                    orientation = orientation.transposed()

                mdi_bone.orientations.append(orientation)

            mdi_skeleton.bones.append(mdi_bone)

        return mdi_skeleton

    @staticmethod
    def _to_mdi_uv_map(mds_model, num_surface):

        mdi_uv_map = mdi_m.MDIUVMapBijective()

        for mds_vertex in mds_model.surfaces[num_surface].vertices:

            u = mds_vertex.tex_coords[0]
            v = 1 - mds_vertex.tex_coords[1]

            mdi_uv = mdi_m.MDIUV(u, v)
            mdi_uv_map.uvs.append(mdi_uv)

        return mdi_uv_map

    @staticmethod
    def _to_mdi_shader(mds_model, num_surface):

        mdi_shader_path = mdi_m.MDIShaderPath()

        path = mds_model.surfaces[num_surface].header.shader
        mdi_shader_path.path = mdi_util_m.from_c_string_padded(path)

        return mdi_shader_path

    @staticmethod
    def _to_mdi_triangle(mds_model, num_surface, num_triangle):

        mds_triangle = mds_model.surfaces[num_surface].triangles[num_triangle]

        index_1 = mds_triangle.indices[0]
        index_2 = mds_triangle.indices[2]
        index_3 = mds_triangle.indices[1]

        mdi_triangle = mdi_m.MDITriangle([index_1, index_2, index_3])
        return mdi_triangle

    @staticmethod
    def _to_mdi_rigged_vertex(mds_model, num_surface, num_vertex):

        mdi_rigged_vertex = mdi_m.MDIRiggedVertex()

        mds_vertex = mds_model.surfaces[num_surface].vertices[num_vertex]

        mdi_rigged_vertex.normal = mathutils.Vector(mds_vertex.normal)

        for mds_weight in mds_vertex.weights:

            mdi_vertex_weight = mdi_m.MDIVertexWeight()

            mdi_vertex_weight.parent_bone = mds_weight.bone_index
            mdi_vertex_weight.weight_value = mds_weight.bone_weight
            mdi_vertex_weight.location = mathutils.Vector(mds_weight.location)

            mdi_rigged_vertex.weights.append(mdi_vertex_weight)

        return mdi_rigged_vertex

    @staticmethod
    def _to_mdi_surface(mds_model, num_surface):

        mdi_surface = mdi_m.MDISurface()

        mds_surface = mds_model.surfaces[num_surface]

        # name
        mdi_surface.name = \
            mdi_util_m.from_c_string_padded(mds_surface.header.name)

        # mdi vertices
        for num_vertex in range(len(mds_surface.vertices)):

            mdi_rigged_vertex = \
                ModelToMDI._to_mdi_rigged_vertex(mds_model,
                                                 num_surface,
                                                 num_vertex)
            mdi_surface.vertices.append(mdi_rigged_vertex)

        # mdi triangles
        for num_triangle in range(len(mds_surface.triangles)):

            mdi_triangle = \
                ModelToMDI._to_mdi_triangle(mds_model,
                                            num_surface,
                                            num_triangle)
            mdi_surface.triangles.append(mdi_triangle)

        # mdi shader
        mdi_surface.shader = ModelToMDI._to_mdi_shader(mds_model, num_surface)

        # mdi uv map
        mdi_surface.uv_map = ModelToMDI._to_mdi_uv_map(mds_model, num_surface)

        return mdi_surface

    @staticmethod
    def convert(mds_model, root_frame = 0):
        """Converts MDS to MDI.

        Args:

            mdc_model (MDS): MDS model.
            root_frame (int): bind pose frame.

        Returns:

            mdi_model (MDI): MDI model.
        """

        timer = timer_m.Timer()
        reporter_m.info("Converting MDS to MDI ...")

        mdi_model = mdi_m.MDI()

        mdi_model.name = mdi_util_m.from_c_string_padded(mds_model.header.name)

        if root_frame >= mds_model.header.num_frames:

            reporter_m.warning("Given bind pose frame '{}' out of range."
                               " Defaulting to '0'"
                               .format(root_frame))
            mdi_model.root_frame = 0

        else:

            mdi_model.root_frame = root_frame

        # mdi surfaces
        for num_surface in range(len(mds_model.surfaces)):

            mdi_surface = ModelToMDI._to_mdi_surface(mds_model, num_surface)
            mdi_model.surfaces.append(mdi_surface)

        # mdi skeleton
        mdi_model.skeleton = ModelToMDI._to_mdi_skeleton(mds_model)

        # mdi tags
        for num_tag in range(len(mds_model.tags)):

            mdi_tag = ModelToMDI._to_mdi_tag(mds_model, num_tag)
            mdi_model.tags.append(mdi_tag)

        # mdi bounding volume
        mdi_model.bounds = ModelToMDI._to_mdi_bounds(mds_model)

        # mdi lod
        mdi_model.lod = ModelToMDI._to_mdi_lod(mds_model)

        time = timer.time()
        reporter_m.info("Converting MDS to MDI DONE (time={})".format(time))

        return mdi_model
