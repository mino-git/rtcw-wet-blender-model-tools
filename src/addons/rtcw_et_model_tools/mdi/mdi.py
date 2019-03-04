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

import mathutils

import rtcw_et_model_tools.mdi.mdi_util as mdi_util
import rtcw_et_model_tools.mdmmdx._mdx as mdx
import rtcw_et_model_tools.blender.scene as scene


class MDIType:

    unknown = 0
    morph_vertices = 1
    rigged_vertices = 2
    shader_references = 3
    shader_reference = 4
    uv_map_surjective = 5
    uv_map_bijective = 6
    lod_discrete = 7
    lod_collapse_map = 8
    socket_free = 9
    socket_parent_bone = 10
    socket_parent_bone_offset = 11

    """TODO

    Attributes:

        TODO

    File encodings:

        type: 16*ASCII

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, type_ = unknown):

        self.type_ = type_

# ====================
# Sockets
# ====================

class MDISocket:
    """TODO

    Attributes:

        TODO

    File encodings:

        name: 64*ASCII (C-String)

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, name, type_ = MDIType.unknown):

        self.name = name

        self.type_ = MDIType(type_)


class MDISocketParentBoneOffset(MDISocket):
    """TODO

    Attributes:

        TODO

    File encodings:

        parent_skeleton: UINT32
        parent_bone: UINT32
        location: 3*F32
        orientation: 3*3*F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, name, parent_skeleton, parent_bone, location,
                 orientation):

        super().__init__(name, MDIType.socket_parent_bone_offset)

        self.parent_skeleton = parent_skeleton
        self.parent_bone = parent_bone
        self.location = location
        self.orientation = orientation


class MDISocketParentBone(MDISocket):
    """TODO

    Attributes:

        TODO

    File encodings:

        parent_skeleton: UINT32
        parent_bone: UINT32
        torso_weight: F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, name, parent_skeleton, parent_bone, torso_weight = 0.0):

        super().__init__(name, MDIType.socket_parent_bone)

        self.parent_skeleton = parent_skeleton
        self.parent_bone = parent_bone
        self.torso_weight = torso_weight


class MDISocketFreeInFrame:
    """TODO

    Attributes:

        TODO

    File encodings:

        location: 3*F32
        orientation: 3*3*F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, location = None, orientation = None):

        self.location = location
        self.orientation = orientation


class MDISocketFreeAnimation:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, frames = None):

        if frames is None:
            self.frames = []
        else:
            self.frames = frames


class MDISocketFree(MDISocket):
    """TODO

    Attributes:

        TODO

    File encodings:

        location: 3*F32
        orientation: 3*3*F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, name, location = None, orientation = None,
                 animation = None):

        super().__init__(name, MDIType.socket_free)

        self.location = location
        self.orientation = orientation

        if animation is None:
            self.animation = MDISocketFreeAnimation()
        else:
            self.animation = animation


class MDISocketsNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_sockets: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_sockets):

        '''
        TODO
        num_sockets
        '''
        pass


class MDISockets:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, socket_list = None):

        self.navigation_info = None

        if socket_list is None:
            self.socket_list = []
        else:
            self.socket_list = socket_list


# ====================
# Skeletons
# ====================

class MDIBoneInFrame:
    """TODO

    Attributes:

        TODO

    File encodings:

        location: 3*F32
        orientation: 3*3*F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, location = None, orientation = None):

        self.location = location
        self.orientation = orientation


class MDIBoneAnimation:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, frames = None):

        if frames is None:
            self.frames = []
        else:
            self.frames = frames


class MDIBone:
    """TODO

    Attributes:

        TODO

    File encodings:

        name: 64*ASCII (C-String)
        parent_bone: UINT32
        parent_dist: F32
        torso_weight: F32
        flags: UINT32
        location: 3*F32
        orientation: 3*3*F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, name, parent_bone = -1, parent_dist = 0,
                 torso_weight = 0, flags = 0, location = None,
                 orientation = None, animation = None):

        self.name = name
        self.parent_bone = parent_bone
        self.parent_dist = parent_dist
        self.torso_weight = torso_weight
        self.flags = flags
        self.location = location
        self.orientation = orientation

        if animation is None:
            self.animation = MDIBoneAnimation()
        else:
            self.animation = animation


class MDIBonesNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_bones: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self):

        '''
        TODO
        num_bones
        '''
        pass


class MDIBones:
    """TODO

    Attributes:

        TODO

    File encodings:

        torso_parent_bone: INT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, torso_parent_bone = None, bone_list = None):

        self.torso_parent_bone = torso_parent_bone

        self.navigation_info = None

        if bone_list is None:
            self.bone_list = []
        else:
            self.bone_list = bone_list


class MDISkeleton:
    """TODO

    Attributes:

        TODO

    File encodings:

        name: 64*ASCII (C-String)

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, name = "MDISkeleton None", bones = None):

        self.name = name

        if bones is None:
            self.bones = MDIBones()
        else:
            self.bones = bones


class MDISkeletonsNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_skeletons: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_skeletons):

        '''
        TODO
        '''
        pass


class MDISkeletons:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, skeleton_list = None):

        self.navigation_info = None

        if skeleton_list is None:
            self.skeleton_list = []
        else:
            self.skeleton_list = skeleton_list


# ====================
# LOD
# ====================

class MDILOD:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, type_ = MDIType.unknown):

        self.type_ = MDIType(type_)


class MDILODCollapseMap(MDILOD):
    """TODO

    Attributes:

        TODO

    File encodings:

        min_lod: UINT32
        mappings: num_vertices*UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, min_lod = 0, mappings = None):

        super().__init__(MDIType.lod_collapse_map)

        self.min_lod = min_lod

        if mappings is None:
            self.mappings = []
        else:
            self.mappings = mappings


class MDILODDiscrete(MDILOD):
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self):

        super().__init__(MDIType.lod_discrete)


# ====================
# UVMap
# ====================

class MDIUVMap:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, type_ = MDIType.unknown):

        self.type_ = MDIType(type_)


class MDIUVMapBijective(MDIUVMap):
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, tex_coords_list = None):

        super().__init__(MDIType.uv_map_bijective)

        if tex_coords_list is None:
            self.tex_coords_list = []
        else:
            self.tex_coords_list = tex_coords_list


class MDITexCoords:
    """TODO

    Attributes:

        TODO

    File encodings:

        u: F32
        v: F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, u = 0.0, v = 0.0):

        self.u = u
        self.v = v


class MDITexCoordsMappingsNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_tex_coords_mappings):

        '''
        TODO
        num_mappings
        '''
        pass


class MDITexCoordsMappings:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, tex_coords_list = None):

        self.navigation_info = None

        if tex_coords_list is None:
            self.tex_coords_list = []
        else:
            self.tex_coords_list = tex_coords_list


class MDIUVMapSurjective(MDIUVMap):
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, tex_coords_mappings_list = None):

        super().__init__(MDIType.uv_map_surjective)

        if tex_coords_mappings_list is None:
            self.tex_coords_mappings_list = []
        else:
            self.tex_coords_mappings_list = tex_coords_mappings_list


# ====================
# Shaders
# ====================

class MDIShaderData:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, type_ = MDIType.unknown):

        self.type_ = MDIType(type_)


class MDIShaderReference(MDIShaderData):
    """TODO

    Attributes:

        TODO

    File encodings:

        reference: 64*ASCII (C-String)

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, reference = "Shader None"):

        super().__init__(MDIType.shader_reference)

        self.reference = reference


class MDIShaderReferencesNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_shaders: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_shader_references):

        '''
        TODO
        num_shaders
        '''
        pass


class MDIShaderReferences(MDIShaderData):
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, shader_reference_list = None):

        super().__init__(MDIType.shader_references)

        self.navigation_info = None

        if shader_reference_list is None:
            self.shader_reference_list = []
        else:
            self.shader_reference_list = shader_reference_list


# ====================
# Color
# ====================

class MDIColorNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        ofs_shaders: UINT32
        ofs_uv_map: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_color):

        '''
        TODO
        ofs_shaders
        ofs_uv_map
        '''
        pass


class MDIColor:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, shader_data = None, uv_map = None):

        self.navigation_info = None

        self.shader_data = shader_data
        self.uv_map = uv_map


# ====================
# Bounds
# ====================

class MDIBoundsInFrame:
    """TODO

    Attributes:

        TODO

    File encodings:

        min_bound: 3*F32
        max_bound: 3*F32
        local_origin: 3*F32
        radius: F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, min_bound = None, max_bound = None, local_origin = None,
                 radius = 0.0):

        self.min_bound = min_bound
        self.max_bound = max_bound
        self.local_origin = local_origin
        self.radius = radius


class MDIBoundsAnimation:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, frames = None):

        if frames is None:
            self.frames = []
        else:
            self.frames = frames


class MDIBounds:
    """TODO

    Attributes:

        TODO

    File encodings:

        min_bound: 3*F32
        max_bound: 3*F32
        local_origin: 3*F32
        radius: F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, min_bound = None, max_bound = None, local_origin = None,
                 radius = 0.0, animation = None):

        self.min_bound = min_bound
        self.max_bound = max_bound
        self.local_origin = local_origin
        self.radius = radius

        self.animation = animation


# ====================
# Triangles
# ====================

class MDITriangle:
    """TODO

    Attributes:

        TODO

    File encodings:

        indices: 3*UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, indices):

        self.indices = indices


class MDITrianglesNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_triangles: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_triangles):

        '''
        TODO
        self.num_triangles
        '''
        pass


class MDITriangles:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, triangle_list = None):

        self.navigation_info = None

        if triangle_list is None:
            self.triangle_list = []
        else:
            self.triangle_list = triangle_list


# ====================
# Vertices
# ====================

class MDIVerticesAnimation:
    """Vertex animation.
    """

    def __init__(self, type_):

        self.type_ = MDIType(type_)


class MDIVertexWeight:
    """TODO

    Attributes:

        TODO

    File encodings:

        parent_bone: UINT32
        weight: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, parent_bone, weight = 0.0):

        self.parent_bone = parent_bone
        self.weight = weight


class MDIRiggedVertexNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_weights: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_weights):

        '''
        TODO
        self.num_weights
        '''
        pass


class MDIRiggedVertex:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, weights = None):

        self.navigation_info = None

        if weights is None:
            self.weights = []
        else:
            self.weights = weights


class MDIRiggedVertices(MDIVerticesAnimation):
    """TODO

    Attributes:

        TODO

    File encodings:

        parent_skeleton: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, parent_skeleton, vertex_list = None):

        super().__init__(MDIType.rigged_vertices)

        self.parent_skeleton = parent_skeleton

        if vertex_list is None:
            self.vertex_list = []
        else:
            self.vertex_list = vertex_list


class MDIMorphVertexInFrame:
    """TODO

    Attributes:

        TODO

    File encodings:

        location: 3*F32
        normal: 3*F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, location = None, normal = None):

        self.location = location
        self.normal = normal


class MDIMorphVerticesInFrame:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, vertex_list = None):

        if vertex_list is None:
            self.vertex_list = []
        else:
            self.vertex_list = vertex_list


class MDIMorphVertices(MDIVerticesAnimation):
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, frame_list = None):

        super().__init__(MDIType.morph_vertices)

        if frame_list is None:
            self.frame_list = []
        else:
            self.frame_list = frame_list


class MDIVertex:
    """TODO

    Attributes:

        TODO

    File encodings:

        location: 3*F32
        normal: 3*F32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, location = None, normal = None, animation = None):

        self.location = location
        self.normal = normal

        self.animation = animation


class MDIVerticesNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_vertices: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_vertices):

        '''
        TODO
        self.num_vertices
        '''
        pass


class MDIVertices:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, vertex_list = None, animation = None):

        self.navigation_info = None

        if vertex_list is None:
            self.vertex_list = []
        else:
            self.vertex_list = vertex_list

        self.animation = animation


# ====================
# Geometry
# ====================

class MDIGeometryNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        ofs_vertices: UINT32
        ofs_triangles: UINT32
        ofs_bounds: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_geometry):

        '''
        TODO
        self.ofs_vertices
        self.ofs_triangles
        self.ofs_bounds
        '''
        pass


class MDIGeometry:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, vertices = None, triangles = None, bounds = None):

        self.navigation_info = None

        if vertices is None:
            self.vertices = MDIVertices()
        else:
            self.vertices = vertices

        if triangles is None:
            self.triangles = MDITriangles()
        else:
            self.triangles = triangles

        self.bounds = bounds


# ====================
# Surfaces
# ====================

class MDISurfaceNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_frames: UINT32
        ofs_geometry: UINT32
        ofs_color: UINT32
        ofs_lod: UINT32
        ofs_end: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_surface):

        '''
        TODO
        self.num_frames
        self.ofs_geometry
        self.ofs_color
        self.ofs_lod
        self.ofs_end
        '''
        pass


class MDISurface:
    """TODO

    Attributes:

        TODO

    File encodings:

        name: 64*ASCII (C-String)

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, name = "MDISurface None", geometry = None, color = None,
                 lod = None):

        self.name = name

        self.navigation_info = None

        if geometry is None:
            self.geometry = MDIGeometry()
        else:
            self.geometry = geometry

        if color is None:
            self.color = MDIColor()
        else:
            self.color = color

        self.lod = lod


class MDISurfacesNav:
    """TODO

    Attributes:

        TODO

    File encodings:

        num_surfaces: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_surfaces):

        '''
        TODO
        self.num_surfaces
        '''
        pass


class MDISurfaces:
    """TODO

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, surface_list = None):

        self.navigation_info = None

        if surface_list is None:
            self.surface_list = []
        else:
            self.surface_list = surface_list


# ====================
# MDI
# ====================

class MDINav:

    magic = b"MDIW"

    """TODO

    Attributes:

        TODO

    File encodings:

        magic: 4*ASCII
        version: UINT32
        ofs_surfaces: UINT32
        ofs_skeletons: UINT32
        ofs_sockets: UINT32
        ofs_end: UINT32

    Background:

        TODO

    Notes:

        TODO
    """

    def __init__(self, mdi_model):

        self.magic = MDINav.magic
        self.version = MDI.version

        '''
        TODO
        self.ofs_surfaces
        self.ofs_skeletons
        self.ofs_sockets
        self.ofs_end
        '''


class MDI:
    """TODO

    Attributes:

        TODO

    File encodings:

        name: 64*ASCII (C-String)
        lod_scale: F32
        lod_bias: F32

    Background:

        TODO

    Notes:

        TODO
    """

    version = 1

    def __init__(self, name = "MDI None", lod_scale = 5, lod_bias = 0,
                 surfaces = None, skeletons = None, sockets = None):

        self.name = name
        self.lod_scale = lod_scale
        self.lod_bias = lod_bias

        self.navigation_info = None

        if surfaces is None:
            self.surfaces = MDISurfaces()
        else:
            self.surfaces = surfaces

        if skeletons is None:
            self.skeletons = MDISkeletons()
        else:
            self.skeletons = skeletons

        if sockets is None:
            self.sockets = MDISockets()
        else:
            self.sockets = sockets
