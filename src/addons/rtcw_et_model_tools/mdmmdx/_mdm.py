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

"""In-memory representation of the MDM file format. Provides file read and file
write functions to deal with the formats binary encoding.

Notes:

    The file format is stored as a byte stream to file. Data types are encoded
    in little-endian byte order. If not else specified, all coordinates are
    given in cartesian space. Convention is right-handed: x points forward,
    y points left, z points up.

Background:

    MDM is defined as a triangle mesh using skeletal animation. Surfaces make
    up the basic model. They are described by geometry, level of detail and
    color data. Tags complement the format.

    Geometry of a surface is described by grouping vertices into a triangle.
    Triangles are then grouped into a surface.

    A progressive mesh algorithm is used to draw a surface with varying level
    of detail (LOD) during runtime. This is described by a collapse map.

    Colorization of a surface is done by defining UV-maps and references to
    shaders. The UV-maps are used to color surfaces with solid color from a 2D
    image. Shaders manipulate surface properties. These properties define how
    the surface interacts with light sources present in a scene. Additionally
    vertex normals manipulate the shading of a surface.

    Animation of a surface is done by storing vertex location and normal values
    in relation to a skeleton. This animation technique is also known as
    "skeletal animation". The way it works is that for each key frame the
    vertex location and normal values are influenced-by/weighted-against the
    location and orientation values of 1 or more bones. Thus, only bones
    contain animation data while vertex values are stored once in a special
    model pose called "binding pose".

    Tags provide the possibility to attach external models to the model.

    While MDM specifies surface and tag data, the actual animation data is
    defined separately in an MDX file. MDM references this skeletal animation
    data for the purpose of reusing the same set of animations across several
    different meshes (see MDX for more details).
"""

import struct

import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


class MDMTag:
    """Frame independent tag information.

    Attributes:

        name (bytes): tag name, ASCII encoded, null-terminated, length 64.
        orientation (tuple): orientation as rotation matrix in binding pose as
            tuple of floats given in parent bone space. Each sequence of 3
            floats make up the coordinates of a basis vector. The first 3
            floats make up the x basis vector, etc.
        parent_bone (int): bone that controls the tags location and
            orientation. Given as index into the list of bone_infos (from the
            referenced MDX file).
        location (tuple): location in binding pose relative to its referenced
            bone as tuple of floats. The values are given in parent bone space.
        num_bone_refs (int): number of bones this tag references.
        ofs_bone_refs (int): file offset to list of bone references.
        ofs_end (int): file offset to end of tag.
        bone_refs (MDMBoneRefs): reference to MDMBoneRefs object.

    File encodings:

        name: 64*ASCII (C-String).
        orientation: 3*3*F32, IEEE-754.
        parent_bone: UINT32.
        location: 3*F32, IEEE-754.
        num_bone_refs: UINT32.
        ofs_bone_refs: UINT32.
        ofs_end: UINT32.
        bone_refs: num_bone_refs*UINT32.

    Notes:

        MDM tags are different from MDS tags in that their location and
        orientation values are stored in binding pose and with location offset
        to the parent bone. The orientation values therefore are fixed and
        controlled by the parent bone, whereas a bone in MDS is actually the
        tag and can be animated/oriented per frame.

    Background:

        Tags are used to attach external models to a model. Attachment means
        that the external models origin aligns itself with the models tag
        location and orientation. As the external model is parented to the tag
        (nested in tag space), any animation of the tag will also affect the
        external model.

        Domain specific scripts tell the engine which external models to attach
        to a given tag. These scripts are either located in mapscript files
        (attachtotag command) or .skin files. Sometimes they are also hard
        coded.

        An example use case is a hat model (defined separately) attached to a
        head model. This way, characters can be assembled with different looks
        without having to duplicate their model definitions. Tags therefore
        support reuse.

        Another example use case is that of a tank turret model attached to a
        tank model. Instead of having a shooting animation (rotate turret left,
        shoot, rotate turret right) be recorded as vertex positions across
        several key-frames inside a single model, a tag can be used to control
        the shooting animation of a separated model. This safes memory, as the
        tags animation data most likely takes much less space compared to the
        animation data of the tank turret inside a single model.

        However, reuse and memory savings are traded against loss in
        performance. Vertex positions of the external models have to be
        recalculated against the current frame tags location and orientation.
    """

    format = '<64s9fI3f3I'
    format_size = struct.calcsize(format)
    name_len = 64

    def __init__(self, name, orientation, parent_bone, location,
                 num_bone_refs, ofs_bone_refs, ofs_end):

        self.name = name
        self.orientation = orientation
        self.parent_bone = parent_bone
        self.location = location
        self.num_bone_refs = num_bone_refs
        self.ofs_bone_refs = ofs_bone_refs
        self.ofs_end = ofs_end

        self.bone_refs = None

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDMTag object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdm_tag (MDMTag): MDMTag object.
        """

        file.seek(file_ofs)

        name, \
            orientation_x1, orientation_x2, orientation_x3, \
            orientation_y1, orientation_y2, orientation_y3, \
            orientation_z1, orientation_z2, orientation_z3, \
            parent_bone, \
            location_x, location_y, location_z,\
            num_bone_refs, ofs_bone_refs, ofs_end \
            = struct.unpack(MDMTag.format, file.read(MDMTag.format_size))

        orientation = (orientation_x1, orientation_x2, orientation_x3,
                       orientation_y1, orientation_y2, orientation_y3,
                       orientation_z1, orientation_z2, orientation_z3)

        location = (location_x, location_y, location_z)

        mdm_tag = MDMTag(name, orientation, parent_bone, location,
                         num_bone_refs, ofs_bone_refs, ofs_end)

        # mdm_tag.bone_refs
        file_ofs = file_ofs + mdm_tag.ofs_bone_refs

        mdm_tag.bone_refs \
            = MDMBoneRefs.read(file, file_ofs, mdm_tag.num_bone_refs)

        return mdm_tag

    def write(self, file, file_ofs):
        """Writes MDMTag object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDMTag.format,
                               self.name,
                               self.orientation[0], self.orientation[1],
                               self.orientation[2], self.orientation[3],
                               self.orientation[4], self.orientation[5],
                               self.orientation[6], self.orientation[7],
                               self.orientation[8],
                               self.parent_bone,
                               self.location[0],
                               self.location[1],
                               self.location[2],
                               self.num_bone_refs, self.ofs_bone_refs,
                               self.ofs_end))

        # mdm_tag.bone_refs
        file_ofs = file_ofs + self.ofs_bone_refs

        self.bone_refs.write(file, file_ofs)


class MDMBoneRefs:
    """Defines which bones a surface or tag references.

    Attributes:

        bone_refs (list): indices into the list of bone_infos for this surface
        or tag, size=num_bone_refs.

    File encodings:

        bone_refs: num_bone_refs*UINT32.

    Notes:

        Used for optimization inside the engine. Needs to be hierarchically
        ordered.
    """

    format = '<I'
    format_size = struct.calcsize(format)

    def __init__(self, bone_refs):

        self.bone_refs = bone_refs

    @staticmethod
    def read(file, file_ofs, num_bone_refs):
        """Reads file data into an MDMBoneRefs object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_bone_refs (int): number of bone references.

        Returns:

            mdm_bone_refs (MDMBoneRefs): MDMBoneRefs object.
        """

        bone_refs = []

        file.seek(file_ofs)

        for i in range(0, num_bone_refs):
            bone_ref = struct.unpack(MDMBoneRefs.format,
                                     file.read(MDMBoneRefs.format_size))
            bone_refs.append(bone_ref[0])

        mdm_bone_refs = MDMBoneRefs(bone_refs)

        return mdm_bone_refs

    def write(self, file, file_ofs):
        """Writes MDMBoneRefs object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        for i in range(0, len(self.bone_refs)):
            file.write(struct.pack(MDMBoneRefs.format, self.bone_refs[i]))


class MDMCollapseMap:
    """The collapse map is used to render a surface with varying level of
    detail (LOD) dependent on view distance during runtime (progressive mesh
    algorithm).

    Attributes:

        mappings (list): indices into the list of vertices for this surface,
            size=num_vertices.

    File encodings:

        mappings: num_vertices*UINT32.

    Background:

        The collapse map is a list of vertex indices pointing into the list of
        vertices for this surface. The value j at index i of the collapse map
        describes a collapse operation. This operation can be read as "vertex i
        is to be mapped/collapsed to vertex j".

        A user will take a fully detailed mesh and gradually reduce vertex and
        triangle count at runtime by using the pre-calculated collapse map. For
        this, he first determines the amount of vertices the mesh should have.
        Then he applies the collapse operations starting from the end of the
        collapse map.

        The particular method used was described by Stan Melax in a publication
        from November 1998, see "A Simple, Fast, and Effective Polygon
        Reduction Algorithm" for further details. A demo implementation can be
        found at: https://github.com/melax/sandbox/tree/master/bunnylod
    """

    format = '<I'
    format_size = struct.calcsize(format)

    def __init__(self, mappings):

        self.mappings = mappings

    @staticmethod
    def read(file, file_ofs, num_vertices):
        """Reads file data into an MDMCollapseMap object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_vertices (int): number of vertices.

        Returns:

            mdm_collapse_map (MDMCollapseMap): MDMCollapseMap object.
        """

        mappings = []

        file.seek(file_ofs)

        for i in range(0, num_vertices):

            mapping = struct.unpack(MDMCollapseMap.format,
                                    file.read(MDMCollapseMap.format_size))
            mappings.append(mapping[0])

        mdm_collapse_map = MDMCollapseMap(mappings)

        return mdm_collapse_map

    def write(self, file, file_ofs):
        """Writes MDMCollapseMap object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        for i in range(0, len(self.mappings)):

            file.write(struct.pack(MDMCollapseMap.format, self.mappings[i]))


class MDMTriangle:
    """A triangle for a surface.

    Attributes:

        indices (tuple): indices into the list of vertices. The order defines
            in which direction the face normal is pointing.

    File encodings:

        indices: 3*UINT32.
    """

    format = '<3I'
    format_size = struct.calcsize(format)

    def __init__(self, indices):

        self.indices = indices

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDMTriangle object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdm_triangle (MDMTriangle): MDMTriangle object.
        """

        file.seek(file_ofs)

        indices = struct.unpack(MDMTriangle.format,
                                file.read(MDMTriangle.format_size))

        mdm_triangle = MDMTriangle(indices)

        return mdm_triangle

    def write(self, file, file_ofs):
        """Writes MDMTriangle object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDMTriangle.format, self.indices[0],
                               self.indices[1], self.indices[2]))


class MDMWeight:
    """Weights are used to define a vertex location in conjunction with all
    other weights of a vertex. The weights and their offsets are specified in
    binding pose.

    Attributes:

        bone_index (int): bone that exercises a weighted influence over the
            vertex location given as index into the list of bone_infos.
        bone_weight (float): amount of influence from the bone over the vertex
            location.
        location (tuple): location coordinates given in bone space.
            TODO recheck with source code

    File encodings:

        bone_index: UINT32.
        bone_weight: F32, IEEE-754.
        location: 3*F32, IEEE-754.

    Notes:

        The sum of all weights for a vertex should always be equal to 1.

    Background:

        See "skinning" or "skeletal animation" for more details.
    """

    format = '<If3f'
    format_size = struct.calcsize(format)

    def __init__(self, bone_index, bone_weight, location):

        self.bone_index = bone_index
        self.bone_weight = bone_weight
        self.location = location

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDMWeight object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdm_weight (MDMWeight): MDMWeight object.
        """

        file.seek(file_ofs)

        bone_index, bone_weight, location_x, location_y, location_z \
            = struct.unpack(MDMWeight.format, file.read(MDMWeight.format_size))

        location = (location_x, location_y, location_z)
        mdm_weight = MDMWeight(bone_index, bone_weight, location)

        return mdm_weight

    def write(self, file, file_ofs):
        """Writes MDMWeight object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDMWeight.format,
                               self.bone_index,
                               self.bone_weight,
                               self.location[0],
                               self.location[1],
                               self.location[2]))


class MDMVertex:
    """Vertex location, normal and texture coordinates.

    Attributes:

        normal (tuple): vertex normal coordinates.
        tex_coords (tuple): u and v coordinates in UV-space as tuple.
        num_weights (int): number of weights for this vertex.

    File encodings:

        normal: 3*F32, IEEE-754.
        tex_coords: 2*F32, IEEE-754.
        num_weights: UINT32.

    Notes:

        The number of weights usually does not exceed 3 (at least i have never
        seen any model with more).

    Background:

        Vertex normals manipulate the shading of a surface (for example smooth
        or flat).

        Texture coordinate values refer to the process of UV-mapping.
    """

    format = '<3f2fI'
    format_size = struct.calcsize(format)

    def __init__(self, normal, tex_coords, num_weights):

        self.normal = normal
        self.tex_coords = tex_coords
        self.num_weights = num_weights

        self.weights = []

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDMVertex object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdm_vertex (MDMVertex): MDMVertex object.
        """

        file.seek(file_ofs)

        normal_x, normal_y, normal_z, tex_coord_u, tex_coord_v, num_weights \
            = struct.unpack(MDMVertex.format, file.read(MDMVertex.format_size))

        mdm_vertex = MDMVertex((normal_x, normal_y, normal_z),
                               (tex_coord_u, tex_coord_v), num_weights)

        # mdm_vertex.weights
        file_ofs = file_ofs + MDMVertex.format_size

        for i in range(0, mdm_vertex.num_weights):

            mdm_weight = MDMWeight.read(file, file_ofs)
            mdm_vertex.weights.append(mdm_weight)

            file_ofs = file_ofs + MDMWeight.format_size

        return mdm_vertex

    def write(self, file, file_ofs):
        """Writes MDMVertex object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDMVertex.format,
                               self.normal[0], self.normal[1], self.normal[2],
                               self.tex_coords[0], self.tex_coords[1],
                               self.num_weights))

        # mdm_vertex.weights
        file_ofs = file_ofs + MDMVertex.format_size

        for mdm_weight in self.weights:

            mdm_weight.write(file, file_ofs)

            file_ofs = file_ofs + MDMWeight.format_size


class MDMSurfaceHeader:
    """General information about a surface.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4.
        name (bytes): surface name, ASCII encoded, null-terminated, length 64.
        shader (bytes): shader name, ASCII encoded, null-terminated, length 64.
        shader_index (int): used in-game only.
        min_lod (int): minimum amount of vertices for the surface or maximum
            amount of collapse operations during runtime.
        ofs_header (int): relative offset from this surface to start of file.
            This is a negative number.
        num_vertices (int): number of vertices.
        ofs_vertices (int): file offset to field of vertices.
        num_triangles (int): number of triangles.
        ofs_triangles (int): file offset to field of triangles.
        ofs_collapse_map (int): file offset to collapse map.
        num_bone_refs (int): number of bones this surface references.
        ofs_bone_refs (int): file offset to bone references.
        ofs_end (int): file offset to end of surface.

    File encodings:

        ident: 4*ASCII.
        name: 64*ASCII (C-String).
        shader: 64*ASCII (C-String).
        shader_index: UINT32.
        min_lod: UINT32.
        ofs_header: UINT32.
        num_vertices: UINT32.
        ofs_vertices: UINT32.
        num_triangles: UINT32.
        ofs_triangles: UINT32.
        ofs_collapse_map: UINT32.
        num_bone_refs: UINT32.
        ofs_bone_refs: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4s64s64s2Ii8I'
    format_size = struct.calcsize(format)
    ident = b'\x09\x00\x00\x00'
    name_len = 64
    shader_name_len = 64
    shader_index = 0

    def __init__(self, ident, name, shader, shader_index, min_lod, ofs_header,
                 num_vertices, ofs_vertices, num_triangles, ofs_triangles,
                 ofs_collapse_map, num_bone_refs, ofs_bone_refs, ofs_end):
        self.ident = ident
        self.name = name
        self.shader = shader
        self.shader_index = shader_index

        self.min_lod = min_lod

        self.ofs_header = ofs_header

        self.num_vertices = num_vertices
        self.ofs_vertices = ofs_vertices

        self.num_triangles = num_triangles
        self.ofs_triangles = ofs_triangles

        self.ofs_collapse_map = ofs_collapse_map

        self.num_bone_refs = num_bone_refs
        self.ofs_bone_refs = ofs_bone_refs

        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDMSurfaceHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdm_surface_header (MDMSurfaceHeader): MDMSurfaceHeader object.
        """

        file.seek(file_ofs)

        ident, name, shader, shader_index, min_lod, ofs_header, num_vertices, \
            ofs_vertices, num_triangles, ofs_triangles, ofs_collapse_map, \
            num_bone_refs, ofs_bone_refs, ofs_end \
            = struct.unpack(MDMSurfaceHeader.format,
                            file.read(MDMSurfaceHeader.format_size))

        mdm_surface_header \
            = MDMSurfaceHeader(ident, name, shader, shader_index, min_lod,
                               ofs_header, num_vertices, ofs_vertices,
                               num_triangles, ofs_triangles, ofs_collapse_map,
                               num_bone_refs, ofs_bone_refs, ofs_end)

        return mdm_surface_header

    def write(self, file, file_ofs):
        """Writes MDMSurfaceHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDMSurfaceHeader.format, self.ident, self.name,
                               self.shader, self.shader_index, self.min_lod,
                               self.ofs_header, self.num_vertices,
                               self.ofs_vertices, self.num_triangles,
                               self.ofs_triangles, self.ofs_collapse_map,
                               self.num_bone_refs, self.ofs_bone_refs,
                               self.ofs_end))


class MDMSurface:
    """A surface of the model.

    Attributes:

        header (MDMSurfaceHeader): reference to MDMSurfaceHeader object.
        vertices (list): list of MDMVertex objects, size=num_vertices.
        triangles (list): list of MDMTriangle objects, size=num_triangles.
        collapse_map (MDMCollapseMap): reference to MDMCollapseMap object.
        bone_refs (MDMBoneRefs): reference to MDMBoneRefs object.

    Background:

        Surfaces are described by geometry, level-of-detail and color data. A
        model can consist of multiple surfaces.
    """

    def __init__(self):

        self.header = None
        self.vertices = []
        self.triangles = []
        self.collapse_map = None
        self.bone_refs = None

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDMSurface object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdm_surface (MDMSurface): MDMSurface object.
        """

        mdm_surface = MDMSurface()

        mdm_surface_ofs = file_ofs

        # mdm_surface.header
        mdm_surface.header = MDMSurfaceHeader.read(file, file_ofs)

        # mdm_surface.vertices
        file_ofs = mdm_surface_ofs + mdm_surface.header.ofs_vertices
        for i in range(mdm_surface.header.num_vertices):

            mdm_vertex = MDMVertex.read(file, file_ofs)
            mdm_surface.vertices.append(mdm_vertex)

            file_ofs = file_ofs + MDMVertex.format_size + \
                mdm_vertex.num_weights * MDMWeight.format_size

        # mdm_surface.triangles
        file_ofs = mdm_surface_ofs + mdm_surface.header.ofs_triangles
        for i in range(mdm_surface.header.num_triangles):

            mdm_triangle = MDMTriangle.read(file, file_ofs)
            mdm_surface.triangles.append(mdm_triangle)

            file_ofs = file_ofs + MDMTriangle.format_size

        # mdm_surface.collapse_map
        file_ofs = mdm_surface_ofs + mdm_surface.header.ofs_collapse_map
        mdm_surface.collapse_map \
            = MDMCollapseMap.read(file,
                                  file_ofs,
                                  mdm_surface.header.num_vertices)

        # mdm_surface.bone_refs
        file_ofs = mdm_surface_ofs + mdm_surface.header.ofs_bone_refs
        mdm_surface.bone_refs \
            = MDMBoneRefs.read(file,
                               file_ofs,
                               mdm_surface.header.num_bone_refs)

        return mdm_surface

    def write(self, file, file_ofs):
        """Writes MDMSurface object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        mdm_surface_ofs = file_ofs

        # mdm_surface.header
        self.header.write(file, file_ofs)

        # mdm_surface.vertices
        file_ofs = mdm_surface_ofs + self.header.ofs_vertices
        for vertex in self.vertices:

            vertex.write(file, file_ofs)

            file_ofs = file_ofs + MDMVertex.format_size + \
                vertex.num_weights * MDMWeight.format_size

        # mdm_surface.triangles
        file_ofs = mdm_surface_ofs + self.header.ofs_triangles
        for triangle in self.triangles:

            triangle.write(file, file_ofs)

            file_ofs = file_ofs + MDMTriangle.format_size

        # mdm_surface.collapse_map
        file_ofs = mdm_surface_ofs + self.header.ofs_collapse_map
        self.collapse_map.write(file, file_ofs)

        # mdm_surface.bone_refs
        file_ofs = mdm_surface_ofs + self.header.ofs_bone_refs
        self.bone_refs.write(file, file_ofs)


class MDMHeader:
    """General information about MDM data.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, reads "MDMW".
        version (int): version number, latest known is 4.
        name (bytes): model name, usually its pathname, ASCII encoded,
            null-terminated, length 64.
        lod_scale (int): TODO.
        lod_bias (int): TODO.
        num_surfaces (int): number of surfaces.
        ofs_surfaces (int): file offset to field of surfaces.
        num_tags (int): number of tags.
        ofs_tags (int): file offset to field of tags.
        ofs_end (int): file offset to end of file.

    File encodings:

        ident: 4*ASCII.
        version: UINT32.
        name: 64*ASCII (C-String).
        lod_scale: F32, IEEE-754.
        lod_bias: F32, IEEE-754.
        num_surfaces: UINT32.
        ofs_surfaces: UINT32.
        num_tags: UINT32.
        ofs_tags: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4sI64s2f5I'
    format_size = struct.calcsize(format)
    ident = b'MDMW'
    version = 3
    name_len = 64

    def __init__(self, ident, version, name, lod_scale, lod_bias, num_surfaces,
                 ofs_surfaces, num_tags, ofs_tags, ofs_end):

        self.ident = ident
        self.version = version
        self.name = name

        self.lod_scale = lod_scale
        self.lod_bias = lod_bias

        self.num_surfaces = num_surfaces
        self.ofs_surfaces = ofs_surfaces
        self.num_tags = num_tags
        self.ofs_tags = ofs_tags

        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):

        file.seek(file_ofs)

        ident, version, name, lod_scale, lod_bias, num_surfaces, \
            ofs_surfaces, num_tags, ofs_tags, ofs_end \
            = struct.unpack(MDMHeader.format,
                            file.read(MDMHeader.format_size))

        if ident != MDMHeader.ident:
            reporter_m("MDMHeader.ident mismatch. Found '{}'. Used '{}'"
                       " Make sure the file is indeed MDM."
                       .format(ident, MDMHeader.ident))

        mdm_file_header = MDMHeader(ident, version, name, lod_scale, lod_bias,
                                    num_surfaces, ofs_surfaces, num_tags,
                                    ofs_tags, ofs_end)

        return mdm_file_header

    def write(self, file, file_ofs):

        file.seek(file_ofs)

        file.write(struct.pack(MDMHeader.format,
                               self.ident, self.version, self.name,
                               self.lod_scale, self.lod_bias,
                               self.num_surfaces, self.ofs_surfaces,
                               self.num_tags, self.ofs_tags, self.ofs_end))


class MDM:
    """Holds references to all MDM data.

    Attributes:

        header (MDMHeader): reference to MDMHeader object.
        surfaces (list): list of MDMSurface objects, size=num_surfaces.
        tags (list): list of MDMTag objects, size=num_tags.
    """

    max_tags = 128
    max_surfaces = 32
    max_bones = 128  # TODO recheck with source
    max_triangles = 8192
    # TODO max_shaders, max_shader_vertices?
    max_vertices = 6000  # per surface

    max_weights = 3  # per vertex

    min_weight_value = 0.0
    max_weight_value = 1.0

    def __init__(self):

        self.header = None
        self.surfaces = []
        self.tags = []

    @staticmethod
    def read(file_path):
        """Reads a binary encoded MDM file into an MDM object.

        Args:

            file_path (str): path to MDM file.

        Returns:

            mdm (MDM): MDM object.
        """

        with open(file_path, 'rb') as file:

            timer = timer_m.Timer()
            reporter_m.info("Reading MDM file: {} ...".format(file_path))

            mdm = MDM()

            # mdm.header
            file_ofs = 0
            mdm.header = MDMHeader.read(file, file_ofs)

            # mdm.surfaces
            file_ofs = mdm.header.ofs_surfaces
            for i in range(mdm.header.num_surfaces):

                mdm_surface = MDMSurface.read(file, file_ofs)
                mdm.surfaces.append(mdm_surface)

                file_ofs = file_ofs + mdm_surface.header.ofs_end

            # mdm.tags
            file_ofs = mdm.header.ofs_tags
            for i in range(mdm.header.num_tags):

                mdm_tag = MDMTag.read(file, file_ofs)
                mdm.tags.append(mdm_tag)

                file_ofs = file_ofs + mdm_tag.ofs_end

            time = timer.time()
            reporter_m.info("Reading MDM file DONE (time={})".format(time))

            return mdm

    def write(self, file_path):
        """Writes MDM object to file with binary encoding.

        Args:

            file_path (str): path to MDM file.
        """

        with open(file_path, 'wb') as file:

            timer = timer_m.Timer()
            reporter_m.info("Writing MDM file: {} ...".format(file_path))

            # mdm.header
            file_ofs = 0
            self.header.write(file, file_ofs)

            # mdm.surfaces
            file_ofs = self.header.ofs_surfaces
            for mdm_surface in self.surfaces:

                mdm_surface.write(file, file_ofs)

                file_ofs = file_ofs + mdm_surface.header.ofs_end

            # mdm.tags
            file_ofs = self.header.ofs_tags
            for mdm_tag in self.tags:

                mdm_tag.write(file, file_ofs)

                file_ofs = file_ofs + mdm_tag.ofs_end

            time = timer.time()
            reporter_m.info("Writing MDM file DONE (time={})".format(time))
