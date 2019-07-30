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

"""MDI (Model Definition Interchange) format. MDI is a general model format
abstracting MD3, MDC, MDS and MDM/MDX for easier handling.
"""

import math
import sys

import mathutils

import rtcw_et_model_tools.common.collapse_map as collapse_map_m
import rtcw_et_model_tools.common.reporter as reporter_m


class MDI:
    """MDI.

    Attributes:

        name (str): name of the model.
        root_frame (int): frame of model in bind or base pose.
        surfaces (list<MDISurface>[num_surfaces]): surfaces (if present).
        skeleton (MDISkeleton): skeleton (if present).
        tags (list<MDITag>[num_tags]): tags of the model (if present).
        bounds (MDIBoundingVolume): bounding info.
        lod (MDILOD): level of detail.
    """

    def __init__(self, name = "unknown name", root_frame = 0, surfaces = None,
                 skeleton = None, tags = None, bounds = None, lod = None):

        self.name = name
        self.root_frame = root_frame

        if surfaces:
            self.surfaces = surfaces
        else:
            self.surfaces = []

        self.skeleton = skeleton

        if tags:
            self.tags = tags
        else:
            self.tags = []

        self.bounds = bounds
        self.lod = lod

    def tags_to_type(self, target_type):

        tags = []
        for tag in self.tags:

            new_tag = tag.to_type(target_type, self)
            tags.append(new_tag)

        self.tags = tags

    def lod_to_type(self, target_type, collapse_frame = 0):

        self.lod = self.lod.to_type(self, target_type, collapse_frame)


class MDISurface:
    """TODO

    Attributes:

        name (str)
        vertices (list<MDIVertex>[num_vertices])
        triangles (list<MDITriangle>[num_triangles])
        shader (MDIShader)
        uv_map (MDIUVMap)
    """

    def __init__(self, name = "unknown name", vertices = None,
                 triangles = None, shader = None, uv_map = None):

        self.name = name

        if vertices:
            self.vertices = vertices
        else:
            self.vertices = []

        if triangles:
            self.triangles = triangles
        else:
            self.triangles = []

        self.shader = shader
        self.uv_map = uv_map

    def uv_map_to_type(self, target_type):

        self.uv_map = self.uv_map.to_type(self, target_type)

    def shader_to_type(self, target_type):

        new_shader = self.shader.to_type(target_type)

        self.shader = new_shader

    def vertices_to_type(self, target_type, mdi_model = None):

        vertices = []
        for vertex in self.vertices:

            new_vertex = vertex.to_type(target_type, mdi_model)
            vertices.append(new_vertex)

        self.vertices = vertices

    def calc_bone_refs(self, mdi_skeleton):

        bone_indices = set()
        for mdi_rigged_vertex in self.vertices:

            for mdi_weight in mdi_rigged_vertex.weights:

                bone_index = mdi_weight.parent_bone
                while bone_index != -1:

                    bone_indices.add(bone_index)
                    bone_index = mdi_skeleton.bones[bone_index].parent_bone

        bone_refs = sorted(bone_indices)

        return bone_refs

    def get_vertices_ms(self, mdi_skeleton = None, num_frame = 0):
        """Returns a list of tuples representing model space coordinates for
        the locations of vertices in a specific frame"""

        vertices_ms = []

        for mdi_vertex in self.vertices:

            if isinstance(mdi_vertex, MDIMorphVertex):

                location = mdi_vertex.locations[num_frame]
                vertices_ms.append(location)

            elif isinstance(mdi_vertex, MDIRiggedVertex):

                location = mdi_vertex.calc_location_ms(mdi_skeleton, num_frame)
                vertices_ms.append((location[0], location[1], location[2]))

            else:

                pass  # TODO

        return vertices_ms

    def get_triangles(self):

        triangles = []
        for mdi_triangle in self.triangles:
            i1 = mdi_triangle.indices[0]
            i2 = mdi_triangle.indices[1]
            i3 = mdi_triangle.indices[2]
            triangles.append((i1, i2, i3))

        return triangles


class MDIMorphVertex:
    """TODO

    Attributes:

        locations (list<Vector>[num_frames])
        normals (list<Vector>[num_frames])
    """

    def __init__(self, locations = None, normals = None):

        if locations:
            self.locations = locations
        else:
            self.locations = []

        if normals:
            self.normals = normals
        else:
            self.normals = []

    def to_type(self, target_type, mdi_model = None):

        if target_type == MDIMorphVertex:
            return self
        elif target_type == MDIRiggedVertex:
            # TODO not supported
            pass

        return None


class MDIRiggedVertex:
    """TODO

    Attributes:

        normal (Vector)
        weights (list<MDIVertexWeight>[num_weights])
    """

    def __init__(self, normal = None, weights = None):

        self.normal = normal

        if weights:
            self.weights = weights
        else:
            self.weights = []

    def to_type(self, target_type, mdi_model = None):

        if target_type == MDIMorphVertex:

            mdi_skeleton = mdi_model.skeleton

            locations = []
            normals = []
            for num_frame in range(len(mdi_model.bounds.aabbs)):

                location, normal = self.calc_ms_coords(mdi_skeleton, num_frame)
                locations.append(location)
                normals.append(normal)

            mdi_morph_vertex = MDIMorphVertex(locations, normals)

            return mdi_morph_vertex

        elif target_type == MDIRiggedVertex:

            return self

        return None

    def calc_location_ms(self, mdi_skeleton, num_frame):

        location_ms = mathutils.Vector((0.0, 0.0, 0.0))

        for mdi_weight in self.weights:

            mdi_bone = mdi_skeleton.bones[mdi_weight.parent_bone]

            bone_weight = mdi_weight.weight_value

            # to object space
            tmp = mdi_bone.orientations[num_frame] @ mdi_weight.location
            object_space_coords = mdi_bone.locations[num_frame] + tmp

            # weight it against bone
            object_space_coords_weighted = object_space_coords * bone_weight

            location_ms += object_space_coords_weighted

        return location_ms

    def calc_normal_ms(self, mdi_skeleton, num_frame):

        total_rotation = None

        for mdi_weight in self.weights:

            mdi_bone = mdi_skeleton.bones[mdi_weight.parent_bone]

            bone_weight = mdi_weight.weight_value
            bone_orientation = mdi_bone.orientations[num_frame]

            if total_rotation == None:

                total_rotation = bone_orientation * bone_weight

            else:

                total_rotation = \
                    total_rotation + (bone_orientation * bone_weight)

        normal_ms = total_rotation @ self.normal
        normal_ms.normalize()

        return normal_ms

    def calc_normal_weighted(self, mdi_skeleton, num_frame):

        total_rotation = None

        for mdi_weight in self.weights:

            mdi_bone = mdi_skeleton.bones[mdi_weight.parent_bone]

            bone_weight = mdi_weight.weight_value
            bone_orientation = mdi_bone.orientations[num_frame]

            if total_rotation == None:

                total_rotation = bone_orientation.transposed() * bone_weight

            else:

                total_rotation = \
                    total_rotation + (bone_orientation.transposed() * bone_weight)

        normal_w = total_rotation @ self.normal
        normal_w.normalize()

        return normal_w

    def calc_ms_coords(self, mdi_skeleton, num_frame):

        location_ms = mathutils.Vector((0.0, 0.0, 0.0))
        orientation_weighted = mathutils.Matrix.Identity(3)

        for mdi_weight in self.weights:

            mdi_bone = mdi_skeleton.bones[mdi_weight.parent_bone]

            bone_weight = mdi_weight.weight_value

            # to object space
            tmp = mdi_bone.orientations[num_frame] @ mdi_weight.location
            object_space_coords = mdi_bone.locations[num_frame] + tmp

            # weight it against bone
            object_space_coords_weighted = object_space_coords * bone_weight

            location_ms += object_space_coords_weighted
            orientation_weighted += \
                mdi_bone.orientations[num_frame] * bone_weight

        normal_ms = self.calc_normal_ms(mdi_skeleton, num_frame)

        return (location_ms, normal_ms)


class MDIVertexWeight:
    """TODO

    Attributes:

        parent_bone (int)
        weight_value (float)
        location (Vector)
    """

    def __init__(self, parent_bone = 0, weight_value = 0.0, location = None):

        self.parent_bone = parent_bone
        self.weight_value = weight_value
        self.location = location


class MDITriangle:
    """TODO

    Attributes:

        indices (list<int>[3])
    """

    def __init__(self, indices = None):

        if indices:
            self.indices = indices
        else:
            self.indices = []


class MDIShaderPaths:
    """TODO

    Attributes:

        paths (list<MDIShaderPath>[num_shaders])
    """

    def __init__(self, paths = None):

        if paths:
            self.paths = paths
        else:
            self.paths = []

    def to_type(self, target_type):

        if target_type == MDIShaderPaths:

            return self

        elif target_type == MDIShaderPath:

            # TODO warning message
            mdi_shader_path = self.paths[0]  # TODO we just assume it exists
            return mdi_shader_path

        return None


class MDIShaderPath:
    """TODO

    Attributes:

        path (str)
    """

    def __init__(self, path = "unknown path"):

        self.path = path

    def to_type(self, target_type):

        if target_type == MDIShaderPaths:

            paths = [self]
            mdi_shader_paths = MDIShaderPaths(paths)

            return mdi_shader_paths

        elif target_type == MDIShaderPath:

            return self

        return None


class MDIUVMapSurjective:
    """TODO
    """

    def __init__(self, num_vertices):

        self.uvs = []

        for _ in range(num_vertices):
            self.uvs.append(None)

    def add(self, num_vertex, uv_coordinates, polygon_index):

        if not self.uvs[num_vertex]:

            mdi_uv_vertex_polygons = MDIUVVertexPolygons(uv_coordinates)
            mdi_uv_vertex_polygons.polygon_indices.append(polygon_index)
            self.uvs[num_vertex] = []
            self.uvs[num_vertex].append(mdi_uv_vertex_polygons)
            return

        found = False
        for mdi_uv_vertex_polygons in self.uvs[num_vertex]:

            if mdi_uv_vertex_polygons.uv_coordinates == uv_coordinates:
                mdi_uv_vertex_polygons.polygon_indices.append(polygon_index)
                found = True
                break

        if not found:

            mdi_uv_vertex_polygons = MDIUVVertexPolygons(uv_coordinates)
            mdi_uv_vertex_polygons.polygon_indices.append(polygon_index)
            self.uvs[num_vertex].append(mdi_uv_vertex_polygons)

    def biject(self, mdi_surface, target_type):

        mdi_uv_map_bijective = MDIUVMapBijective()

        # first pass
        for num_vertex, uvs in enumerate(self.uvs):

            if uvs:

                mdi_uv_vertex_polygons = uvs[0]
                uv_coordinates = mdi_uv_vertex_polygons.uv_coordinates
                mdi_uv = MDIUV(uv_coordinates[0], uv_coordinates[1])
                mdi_uv_map_bijective.uvs.append(mdi_uv)

            else:

                reporter_m.warning("Found unmapped vertex. Defaulting to"
                                   " (0, 0).")
                mdi_uv = MDIUV(0.0, 0.0)
                mdi_uv_map_bijective.uvs.append(mdi_uv)

        # second pass
        num_new_vertices = 0
        for num_vertex, uvs in enumerate(self.uvs):

            mdi_vertex = mdi_surface.vertices[num_vertex]

            if not uvs:
                continue  # fixed during first pass already

            # skip the first one, since it's already mapped
            for i in range(1, len(uvs)):

                mdi_uv_vertex_polygons = uvs[i]

                # create new vertex
                mdi_surface.vertices.append(mdi_vertex)
                new_vertex_index = len(mdi_surface.vertices) - 1
                num_new_vertices += 1

                # modify the triangles
                for polygon_index in mdi_uv_vertex_polygons.polygon_indices:

                    mdi_triangle = mdi_surface.triangles[polygon_index]

                    for j, index in enumerate(mdi_triangle.indices):

                        if index == num_vertex:

                            mdi_triangle.indices[j] = new_vertex_index
                            break

                # modify uv list
                uv_coordinates = mdi_uv_vertex_polygons.uv_coordinates
                mdi_uv = MDIUV(uv_coordinates[0], uv_coordinates[1])
                mdi_uv_map_bijective.uvs.append(mdi_uv)

        if num_new_vertices:

            reporter_m.info("Created {} new vertices for mdi surface '{}'"
                            " during uv map pass. To avoid this try to reduce"
                            " the number of seams crossing each vertex."
                            .format(num_new_vertices, mdi_surface.name))

        return mdi_uv_map_bijective

    def to_type(self, mdi_surface, target_type):

        if target_type == MDIUVMapBijective:

            return self.biject(mdi_surface, target_type)

        elif target_type == MDIUVMapSurjective:

            return self

        else:

            raise Exception("Unknown UVMap type")

        return None


class MDIUVVertexPolygons:
    """TODO
    """

    def __init__(self, uv_coordinates):

        self.uv_coordinates = uv_coordinates
        self.polygon_indices = []


class MDIUVMapBijective:
    """TODO

    Attributes:

        uvs (list<MDIUV>[num_vertices])
    """

    def __init__(self, uvs = None):

        if uvs:
            self.uvs = uvs
        else:
            self.uvs = []

    def to_type(self, mdi_surface, target_type):

        if target_type == MDIUVMapBijective:

            return self

        elif target_type == MDIUVMapSurjective:

            raise Exception("Can not convert bijective to surjective uv map")

        else:

            raise Exception("Unknown UVMap type")

        return None


class MDIUV:
    """TODO

    Attributes:

        u (float)
        v (float)
    """

    def __init__(self, u = 0.0, v = 0.0):

        self.u = u
        self.v = v


class MDISkeleton:
    """TODO
    - fixed distance note

    Attributes:

        name (str)
        torso_parent_bone (int)
        bones (list<MDIBone>[num_bones])
    """

    def __init__(self, name = "unknown name", torso_parent_bone = -1,
                 bones = None):

        self.name = name
        self.torso_parent_bone = torso_parent_bone

        if bones:
            self.bones = bones
        else:
            self.bones = []


class MDIBone:
    """TODO

    Attributes:

        name (str)
        parent_bone (int)
        parent_dist (float)
        torso_weight (float)
        locations (list<Vector>[num_frames])
        orientations (list<Matrix>[num_frames])
    """

    def __init__(self, name = "unknown name", parent_bone = 0,
                 parent_dist = 0.0, torso_weight = None, locations = None,
                 orientations = None):

        self.name = name
        self.parent_bone = parent_bone
        self.parent_dist = parent_dist
        self.torso_weight = torso_weight

        if locations:
            self.locations = locations
        else:
            self.locations = []

        if orientations:
            self.orientations = orientations
        else:
            self.orientations = []


class MDIFreeTag:
    """TODO

    Attributes:

        name (str)
        locations (list<Vector>[num_frames])
        orientations (list<Matrix>[num_frames])
    """

    def __init__(self, name = "unknown name", locations = None,
                 orientations = None):

        self.name = name

        if locations:
            self.locations = locations
        else:
            self.locations = []

        if orientations:
            self.orientations = orientations
        else:
            self.orientations = []

    def to_type(self, target_type, mdi_model = None):

        if target_type == MDIFreeTag:

            return self

        elif target_type == MDIBoneTag:
            # TODO possible, but it will fail on vertices conversion
            pass

        elif target_type == MDIBoneTagOff:
            # TODO possible, but it will fail on vertices conversion
            pass

        return None


class MDIBoneTag:
    """TODO

    Attributes:

        name (str)
        parent_bone (int)
        torso_weight (float)
    """

    def __init__(self, name = "unknown name", parent_bone = 0,
                 torso_weight = None):

        self.name = name
        self.parent_bone = parent_bone
        self.torso_weight = torso_weight

    def to_type(self, target_type, mdi_model = None):

        if target_type == MDIFreeTag:

            mdi_parent_bone = mdi_model.skeleton.bones[self.parent_bone]

            name = self.name

            locations = []
            orientations = []
            for num_frame in range(len(mdi_parent_bone.locations)):

                location = mdi_parent_bone.locations[num_frame]
                orientation = mdi_parent_bone.orientations[num_frame]

                locations.append(location)
                orientations.append(orientation)

            mdi_free_tag = MDIFreeTag(name, locations, orientations)

            return mdi_free_tag

        elif target_type == MDIBoneTag:

            return self

        elif target_type == MDIBoneTagOff:

            mdi_parent_bone = mdi_model.skeleton.bones[self.parent_bone]

            name = self.name
            parent_bone = self.parent_bone
            location = mathutils.Vector((0, 0, 0))
            orientation = mathutils.Matrix.Identity(3)
            mdi_bone_tag_off = MDIBoneTagOff(name, parent_bone, location,
                                             orientation)

            return mdi_bone_tag_off

        return None


class MDIBoneTagOff:
    """TODO

    Attributes:

        name (str)
        parent_bone (int)
        location (Vector)
        orientation (Matrix)
    """

    def __init__(self, name = "unknown name", parent_bone = 0, location = None,
                 orientation = None):

        self.name = name
        self.parent_bone = parent_bone
        self.location = location
        self.orientation = orientation

    def to_type(self, target_type, mdi_model = None):

        if target_type == MDIFreeTag:

            mdi_parent_bone = mdi_model.skeleton.bones[self.parent_bone]

            name = self.name

            locations = []
            orientations = []
            for num_frame in range(len(mdi_parent_bone.locations)):

                location = self.calc_frame_location_ms(mdi_model, num_frame)
                orientation = self.calc_frame_orientation_ms(mdi_model, num_frame)

                locations.append(location)
                orientations.append(orientation)

            mdi_free_tag = MDIFreeTag(name, locations, orientations)

            return mdi_free_tag

        elif target_type == MDIBoneTag:

            root_frame = mdi_model.root_frame
            mdi_parent_bone = mdi_model.skeleton.bones[self.parent_bone]

            parent_location = mdi_parent_bone.locations[root_frame]
            parent_orientation = mdi_parent_bone.orientations[root_frame]

            tag_name = self.name
            tag_parent_bone = self.parent_bone

            needs_new_bone = False
            if parent_location == self.location and \
                parent_orientation == self.orientation:  # TODO check with imprecison
                pass
            else:
                needs_new_bone = True

            if needs_new_bone:

                # bone params
                name = self.name
                parent_bone = self.parent_bone
                parent_dist = 0.0  # calculated later
                torso_weight = 0.0  # TODO

                locations = []
                orientations = []

                num_frames = len(mdi_parent_bone.locations)
                for num_frame in range(num_frames):

                    location = \
                        self.calc_frame_location_ms(mdi_model, num_frame)
                    orientation = \
                        self.calc_frame_orientation_ms(mdi_model, num_frame)

                    locations.append(location)
                    orientations.append(orientation)

                parent_dist = self.location.length

                new_bone = MDIBone(name, parent_bone, parent_dist,
                                   torso_weight, locations, orientations)
                mdi_model.skeleton.bones.append(new_bone)

                tag_parent_bone = len(mdi_model.skeleton.bones) - 1

            mdi_bone_tag = MDIBoneTag(tag_name, tag_parent_bone, torso_weight)

            return mdi_bone_tag

        elif target_type == MDIBoneTagOff:

            return self

        return None

    def calc_frame_location_ms(self, mdi_model, num_frame):

        mdi_parent_bone = mdi_model.skeleton.bones[self.parent_bone]

        pfl_ms = mdi_parent_bone.locations[num_frame]
        pfo_ms = mdi_parent_bone.orientations[num_frame]

        tfl_ms = pfl_ms + (pfo_ms @ self.location)

        return tfl_ms

    def calc_frame_orientation_ms(self, mdi_model, num_frame):

        mdi_parent_bone = mdi_model.skeleton.bones[self.parent_bone]

        pfo_ms = mdi_parent_bone.orientations[num_frame]
        tfo_ms = pfo_ms @ self.orientation

        return tfo_ms

    def calc_bone_refs(self, mdi_skeleton):

        # TODO some tags do not include the torso parent bone, why?

        bone_indices = set()

        bone_index = self.parent_bone
        while bone_index != -1:

            bone_indices.add(bone_index)
            bone_index = mdi_skeleton.bones[bone_index].parent_bone

        bone_refs = sorted(bone_indices)

        return bone_refs

class MDIBoundingVolume:
    """Contains axially aligned bounding box and bound sphere used for (TODO
    basic collision tests? and) culling.

    Attributes:

        aabbs (list<MDIAABB>[num_frames])
        spheres (list<MDIBoundingSphere>[num_frames])
    """

    def __init__(self, aabbs = None, spheres = None):

        if aabbs:
            self.aabbs = aabbs
        else:
            self.aabbs = []

        if spheres:
            self.spheres = spheres
        else:
            self.spheres = []

    @staticmethod
    def calc_num_frames(mdi_model):
        '''Find out the maximum number frames across all surfaces.  If no
        surfaces are present, use tags to find out max frame count. The number
        of frames can also be determined by the skeleton. A model should never
        have no frames at all.
        '''

        num_frames = 0
        for mdi_surface in mdi_model.surfaces:

            mdi_sample_morph_vertex = None
            rigged_vertex_found = False

            for mdi_vertex in mdi_surface.vertices:

                if isinstance(mdi_vertex, MDIMorphVertex):

                    mdi_sample_morph_vertex = mdi_vertex

                elif isinstance(mdi_vertex, MDIRiggedVertex):

                    rigged_vertex_found = True

                else:

                    pass

            if mdi_sample_morph_vertex:

                # all morph vertices should have equal frame count
                num_frames = max(num_frames,
                                 len(mdi_sample_morph_vertex.locations))

            if rigged_vertex_found:

                # all bones should have equal frame count
                mdi_sample_bone = mdi_model.skeleton.bones[0]

                num_frames = max(num_frames, len(mdi_sample_bone.locations))

        if num_frames == 0:  # use tags to determine frame count

            for mdi_tag in mdi_model.tags:

                if isinstance(mdi_tag, MDIFreeTag):

                    num_frames = \
                        max(num_frames, len(mdi_tag.locations))

                elif isinstance(mdi_tag, MDIBoneTag) or \
                     isinstance(mdi_tag, MDIBoneTagOff):

                    parent_bone = mdi_tag.parent_bone
                    mdi_sample_bone = mdi_model.skeleton.bones[parent_bone]

                    num_frames = \
                        max(num_frames, len(mdi_sample_bone.locations))

        return num_frames

    @staticmethod
    def calc(mdi_model):
        '''Calculates the bounding volume which is used for culling.
        '''

        bounds = MDIBoundingVolume()

        num_frames = MDIBoundingVolume.calc_num_frames(mdi_model)

        if mdi_model.surfaces:

            for num_frame in range(num_frames):

                min_x, min_y, min_z = [sys.float_info.max] * 3
                max_x, max_y, max_z = [sys.float_info.min] * 3

                for mdi_surface in mdi_model.surfaces:

                    for mdi_vertex in mdi_surface.vertices:

                        location = None

                        if isinstance(mdi_vertex, MDIMorphVertex):

                            location = mdi_vertex.locations[num_frame]

                        elif isinstance(mdi_vertex, MDIRiggedVertex):

                            location = \
                                mdi_vertex.calc_location_ms(mdi_model.skeleton,
                                                            num_frame)

                        else:

                            pass

                        min_x, min_y, min_z = \
                            min(location[0], min_x), \
                            min(location[1], min_y), \
                            min(location[2], min_z)

                        max_x, max_y, max_z = \
                            max(location[0], max_x), \
                            max(location[1], max_y), \
                            max(location[2], max_z)

                min_bound = mathutils.Vector((min_x, min_y, min_z))
                max_bound = mathutils.Vector((max_x, max_y, max_z))
                mdi_aabb = MDIAABB(min_bound, max_bound)

                mdi_bounding_sphere = \
                    MDIBoundingSphere.calc_from_bounds(min_bound, max_bound)

                #mdi_aabb.scale(1.5)

                bounds.aabbs.append(mdi_aabb)
                bounds.spheres.append(mdi_bounding_sphere)

        else:

            mdi_aabb = MDIAABB()
            mdi_bounding_sphere = MDIBoundingSphere()

            for num_frame in range(num_frames):

                bounds.aabbs.append(mdi_aabb)
                bounds.spheres.append(mdi_bounding_sphere)

        return bounds


class MDIAABB:
    """TODO

    Attributes:

        min_bound (Vector)
        max_bound (Vector)
    """

    def scale(self, scale_factor):

        self.min_bound *= scale_factor
        self.max_bound *= scale_factor

    def __init__(self, min_bound = None, max_bound = None):

        if min_bound:
            self.min_bound = min_bound
        else:
            self.min_bound = mathutils.Vector((0, 0, 0))

        if max_bound:
            self.max_bound = max_bound
        else:
            self.max_bound = mathutils.Vector((0, 0, 0))


class MDIBoundingSphere:
    """TODO

    Attributes:

        origin (Vector)
        radius (float)
    """

    def __init__(self, origin = None, radius = 0.0):

        if origin:
            self.origin = origin
        else:
            self.origin = mathutils.Vector((0, 0, 0))

        self.radius = radius

    @staticmethod
    def calc_from_bounds(min_bound, max_bound):

        # make a cube to calc the values
        distance_x = math.fabs(min_bound[0] - max_bound[0])
        distance_y = math.fabs(min_bound[1] - max_bound[1])
        distance_z = math.fabs(min_bound[2] - max_bound[2])
        cube_edge_len = max(distance_x, distance_y, distance_z)

        if distance_x < cube_edge_len:

            len_to_add = (cube_edge_len - distance_x) / 2

            min_bound_x = min_bound[0] - len_to_add
            max_bound_x = max_bound[0] + len_to_add

        else:

            min_bound_x = min_bound[0]
            max_bound_x = max_bound[0]

        if distance_y < cube_edge_len:

            len_to_add = (cube_edge_len - distance_y) / 2

            min_bound_y = min_bound[1] - len_to_add
            max_bound_y = max_bound[1] + len_to_add

        else:

            min_bound_y = min_bound[1]
            max_bound_y = max_bound[1]

        if distance_z < cube_edge_len:

            len_to_add = (cube_edge_len - distance_z) / 2

            min_bound_z = min_bound[2] - len_to_add
            max_bound_z = max_bound[2] + len_to_add

        else:

            min_bound_z = min_bound[2]
            max_bound_z = max_bound[2]

        # calc values from cube
        origin = mathutils.Vector((0, 0, 0))
        origin[0] = min_bound_x + ((max_bound_x - min_bound_x) / 2)
        origin[1] = min_bound_y + ((max_bound_y - min_bound_y) / 2)
        origin[2] = min_bound_z + ((max_bound_z - min_bound_z) / 2)

        radius = (min_bound + origin).length

        mdi_bounding_sphere = MDIBoundingSphere(origin, radius)

        return mdi_bounding_sphere


class MDIDiscreteLOD:
    """Currently empty.

    Attributes:

        TODO
    """

    def __init__(self):

        pass

    def to_type(self, mdi_model, target_type, collapse_frame = 0):

        if target_type == MDIDiscreteLOD:

            return self

        elif target_type == MDICollapseMap:

            mdi_collapse_map = MDICollapseMap._calc(mdi_model, collapse_frame)

            return mdi_collapse_map

        return None


class MDICollapseMap:
    """TODO

    Attributes:

        lod_scale (float)
        lod_bias (float)
        min_lods (list<int>[num_surfaces])
        collapses (list<int>[num_surfaces][num_vertices])
    """

    def __init__(self, collapse_frame = None, lod_scale = 5, lod_bias = 0,
                 min_lods = None, collapses = None):

        self.collapse_frame = collapse_frame

        self.lod_scale = lod_scale
        self.lod_bias = lod_bias

        if min_lods:
            self.min_lods = min_lods
        else:
            self.min_lods = []

        if collapses:
            self.collapses = collapses
        else:
            self.collapses = []

    @staticmethod
    def _calc(mdi_model, collapse_frame = 0):

        mdi_collapse_map = MDICollapseMap()

        mdi_collapse_map.collapse_frame = collapse_frame
        mdi_collapse_map.lod_scale = 5 # TODO
        mdi_collapse_map.lod_bias = 0 # TODO

        min_lods = []
        collapses = []

        for mdi_surface in mdi_model.surfaces:

            vertices_ms = mdi_surface.get_vertices_ms(mdi_model.skeleton,
                                                      collapse_frame)

            triangles = mdi_surface.get_triangles()

            collapses_, permutation, min_lod = \
                collapse_map_m.calculate(vertices_ms, triangles)

            # TODO explain
            min_lod = int(min_lod + 0.05 * len(mdi_surface.vertices))
            min_lods.append(min_lod)

            collapses.append(collapses_)

            # permute vertices based on the collapseMap calculation
            tmp_array = []
            if len(permutation) != len(mdi_surface.vertices):
                pass  # TODO print warning

            for mdi_vertex in mdi_surface.vertices:
                tmp_array.append(mdi_vertex)

            for j in range(0, len(mdi_surface.vertices)):
                mdi_surface.vertices[permutation[j]] = tmp_array[j]

            # update the changes in the entries in the triangle Array
            for j in range(0, len(mdi_surface.triangles)):

                i0 = permutation[mdi_surface.triangles[j].indices[0]]
                i1 = permutation[mdi_surface.triangles[j].indices[1]]
                i2 = permutation[mdi_surface.triangles[j].indices[2]]
                mdi_surface.triangles[j] = MDITriangle((i0, i1, i2))

            # reorder uvMap
            tmp_array = []
            if len(permutation) != len(mdi_surface.uv_map.uvs):
                pass # TODO print warning

            for uv in mdi_surface.uv_map.uvs:
                tmp_array.append(uv)

            for j in range(0, len(mdi_surface.uv_map.uvs)):
                mdi_surface.uv_map.uvs[permutation[j]] = tmp_array[j]

        mdi_collapse_map.min_lods = min_lods
        mdi_collapse_map.collapses = collapses

        return mdi_collapse_map

    def to_type(self, mdi_model, target_type, collapse_frame = 0):

        if target_type == MDIDiscreteLOD:

            return MDIDiscreteLOD()

        elif target_type == MDICollapseMap:

            return self

        return None
