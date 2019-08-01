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

"""In-memory representation of the MDS file format. Provides file read and file
write functions to deal with the formats binary encoding.

Notes:

    The file format is stored as a byte stream to file. Data types are encoded
    in little-endian byte order. If not else specified, all coordinates are
    given in cartesian space. Convention is right-handed: x points forward,
    y points left, z points up.

Background:

    MDS is defined as a triangle mesh using skeletal animation. Surfaces make
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
"""

import struct

import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


class MDSTag:
    """Frame independent tag information.

    Attributes:

        name (bytes): tag name, ASCII encoded, null-terminated, length 64.
        torso_weight (float): scale torso rotation about torso parent by this.
        parent_bone (int): bone that controls the tags location and
            orientation. Given as index into the list of bone_infos.

    File encodings:

        name: 64*ASCII (C-String).
        torso_weight: F32, IEEE-754.
        parent_bone: UINT32.

    Notes:

        MDS stores location and orientation values for a tag in the field of
        bones, so tags are actually bones with a special flag.

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

    format = '<64sfI'
    format_size = struct.calcsize(format)
    name_len = 64

    def __init__(self, name, torso_weight, parent_bone):

        self.name = name
        self.torso_weight = torso_weight
        self.parent_bone = parent_bone

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDSTag object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_tag (MDSTag): MDSTag object.
        """

        file.seek(file_ofs)

        name, torso_weight, parent_bone \
            = struct.unpack(MDSTag.format, file.read(MDSTag.format_size))

        mds_tag = MDSTag(name, torso_weight, parent_bone)

        return mds_tag

    def write(self, file, file_ofs):
        """Writes MDSTag object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSTag.format, self.name, self.torso_weight,
                               self.parent_bone))


class MDSBoneRefs:
    """Defines which bones a surface references.

    Attributes:

        bone_refs (list): indices into the list of bone_infos for this surface,
        size=num_bone_refs.

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
        """Reads file data into an MDSBoneRefs object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_bone_refs (int): number of bone references.

        Returns:

            mds_bone_refs (MDSBoneRefs): MDSBoneRefs object.
        """

        bone_refs = []

        file.seek(file_ofs)

        for i in range(0, num_bone_refs):

            bone_ref = struct.unpack(MDSBoneRefs.format,
                                     file.read(MDSBoneRefs.format_size))
            bone_refs.append(bone_ref[0])

        mds_bone_refs = MDSBoneRefs(bone_refs)

        return mds_bone_refs

    def write(self, file, file_ofs):
        """Writes MDSBoneRefs object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        for i in range(0, len(self.bone_refs)):

            file.write(struct.pack(MDSBoneRefs.format, self.bone_refs[i]))


class MDSCollapseMap:
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
        """Reads file data into an MDSCollapseMap object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_vertices (int): number of vertices.

        Returns:

            mds_collapse_map (MDSCollapseMap): MDSCollapseMap object.
        """

        mappings = []

        file.seek(file_ofs)

        for i in range(0, num_vertices):

            mapping = struct.unpack(MDSCollapseMap.format,
                                    file.read(MDSCollapseMap.format_size))
            mappings.append(mapping[0])

        mds_collapse_map = MDSCollapseMap(mappings)

        return mds_collapse_map

    def write(self, file, file_ofs):
        """Writes MDSCollapseMap object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        for i in range(0, len(self.mappings)):

            file.write(struct.pack(MDSCollapseMap.format, self.mappings[i]))


class MDSTriangle:
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
        """Reads file data into an MDSTriangle object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_triangle (MDSTriangle): MDSTriangle object.
        """

        file.seek(file_ofs)

        indices = struct.unpack(MDSTriangle.format,
                                file.read(MDSTriangle.format_size))

        mds_triangle = MDSTriangle(indices)

        return mds_triangle

    def write(self, file, file_ofs):
        """Writes MDSTriangle object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSTriangle.format, self.indices[0],
                               self.indices[1], self.indices[2]))


class MDSWeight:
    """Weights are used to define a vertex location in conjunction with all
    other weights of a vertex.

    Attributes:

        bone_index (int): bone that exercises a weighted influence over the
            vertex location given as index into the list of bone_infos.
        bone_weight (float): amount of influence from the bone over the vertex
            location.
        location (tuple): location coordinates given in bone space.
            TODO recheck with source code.

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
        """Reads file data into an MDSWeight object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_weight (MDSWeight): MDSWeight object.
        """

        file.seek(file_ofs)

        bone_index, bone_weight, location_x, location_y, location_z \
            = struct.unpack(MDSWeight.format, file.read(MDSWeight.format_size))

        location = (location_x, location_y, location_z)
        mds_weight = MDSWeight(bone_index, bone_weight, location)

        return mds_weight

    def write(self, file, file_ofs):
        """Writes MDSWeight object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSWeight.format,
                               self.bone_index,
                               self.bone_weight,
                               self.location[0],
                               self.location[1],
                               self.location[2]))


class MDSVertex:
    """Vertex location, normal and texture coordinates.

    Attributes:

        normal (tuple): vertex normal coordinates.
        tex_coords (tuple): u and v coordinates in UV-space as tuple.
        num_weights (int): number of weights for this vertex.
        fixed_parent (int): not used.
        fixed_dist (float): not used.

    File encodings:

        normal: 3*F32, IEEE-754.
        tex_coords: 2*F32, IEEE-754.
        num_weights: UINT32.
        fixed_parent: UINT32.
        fixed_dist: F32, IEEE-754.

    Notes:

        The number of weights usually does not exceed 3 (at least i have never
        seen any model with more).

    Background:

        Vertex normals manipulate the shading of a surface (for example smooth
        or flat).

        Texture coordinate values refer to the process of UV-mapping.
    """

    format = '<3f2fIIf'
    format_size = struct.calcsize(format)

    fixed_parent_default = 0
    fixed_dist_default = 0.0

    def __init__(self, normal, tex_coords, num_weights, fixed_parent,
                 fixed_dist):

        self.normal = normal
        self.tex_coords = tex_coords
        self.num_weights = num_weights
        self.fixed_parent = fixed_parent
        self.fixed_dist = fixed_dist

        self.weights = []

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDSVertex object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_vertex (MDSVertex): MDSVertex object.
        """

        file.seek(file_ofs)

        normal_x, normal_y, normal_z, tex_coord_u, tex_coord_v, num_weights, \
            fixed_parent, fixed_dist \
            = struct.unpack(MDSVertex.format, file.read(MDSVertex.format_size))

        mds_vertex = MDSVertex((normal_x, normal_y, normal_z),
                               (tex_coord_u, tex_coord_v),
                               num_weights, fixed_parent, fixed_dist)

        # mds_vertex.weights
        file_ofs = file_ofs + MDSVertex.format_size

        for _ in range(mds_vertex.num_weights):

            mds_weight = MDSWeight.read(file, file_ofs)
            mds_vertex.weights.append(mds_weight)

            file_ofs = file_ofs + MDSWeight.format_size

        return mds_vertex

    def write(self, file, file_ofs):
        """Writes MDSVertex object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSVertex.format,
                               self.normal[0], self.normal[1], self.normal[2],
                               self.tex_coords[0], self.tex_coords[1],
                               self.num_weights, self.fixed_parent,
                               self.fixed_dist))

        # mds_vertex.weights
        file_ofs = file_ofs + MDSVertex.format_size

        for weight in self.weights:

            weight.write(file, file_ofs)

            file_ofs = file_ofs + MDSWeight.format_size


class MDSSurfaceHeader:
    """General information about a surface.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4.
        name (bytes): surface name, ASCII encoded, null-terminated, length 64.
        shader (bytes): shader name, ASCII encoded, null-terminated, length 64.
        shader_index (int): TODO.
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
        shader_index : UINT32.
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
        """Reads file data into an MDSSurfaceHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_surface_header (MDSSurfaceHeader): MDSSurfaceHeader object.
        """

        file.seek(file_ofs)

        ident, name, shader, shader_index, min_lod, ofs_header, num_vertices, \
            ofs_vertices, num_triangles, ofs_triangles, ofs_collapse_map, \
            num_bone_refs, ofs_bone_refs, ofs_end \
            = struct.unpack(MDSSurfaceHeader.format,
                            file.read(MDSSurfaceHeader.format_size))

        mds_surface_header \
            = MDSSurfaceHeader(ident, name, shader, shader_index, min_lod,
                               ofs_header, num_vertices, ofs_vertices,
                               num_triangles, ofs_triangles, ofs_collapse_map,
                               num_bone_refs, ofs_bone_refs, ofs_end)

        return mds_surface_header

    def write(self, file, file_ofs):
        """Writes MDSSurfaceHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSSurfaceHeader.format, self.ident, self.name,
                               self.shader, self.shader_index, self.min_lod,
                               self.ofs_header, self.num_vertices,
                               self.ofs_vertices, self.num_triangles,
                               self.ofs_triangles, self.ofs_collapse_map,
                               self.num_bone_refs, self.ofs_bone_refs,
                               self.ofs_end))


class MDSSurface:
    """A surface of the model.

    Attributes:

        header (MDSSurfaceHeader): reference to MDSSurfaceHeader object.
        vertices (list): list of MDSVertex objects, size=num_vertices.
        triangles (list): list of MDSTriangle objects, size=num_triangles.
        collapse_map (MDSCollapseMap): reference to MDSCollapseMap object.
        bone_refs (MDSBoneRefs): reference to MDSBoneRefs object.

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
        """Reads file data into an MDSSurface object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_surface (MDSSurface): MDSSurface object.
        """

        mds_surface = MDSSurface()

        mds_surface_ofs = file_ofs

        # mds_surface.header
        mds_surface.header = MDSSurfaceHeader.read(file, file_ofs)

        # mds_surface.vertices
        file_ofs = mds_surface_ofs + mds_surface.header.ofs_vertices
        for i in range(mds_surface.header.num_vertices):

            mds_vertex = MDSVertex.read(file, file_ofs)
            mds_surface.vertices.append(mds_vertex)

            file_ofs = file_ofs + MDSVertex.format_size + \
                mds_vertex.num_weights * MDSWeight.format_size

        # mds_surface.triangles
        file_ofs = mds_surface_ofs + mds_surface.header.ofs_triangles
        for i in range(mds_surface.header.num_triangles):

            mds_triangle = MDSTriangle.read(file, file_ofs)
            mds_surface.triangles.append(mds_triangle)

            file_ofs = file_ofs + MDSTriangle.format_size

        # mds_surface.collapse_map
        file_ofs = mds_surface_ofs + mds_surface.header.ofs_collapse_map
        mds_surface.collapse_map \
            = MDSCollapseMap.read(file,
                                  file_ofs,
                                  mds_surface.header.num_vertices)

        # mds_surface.bone_refs
        file_ofs = mds_surface_ofs + mds_surface.header.ofs_bone_refs
        mds_surface.bone_refs \
            = MDSBoneRefs.read(file,
                               file_ofs,
                               mds_surface.header.num_bone_refs)

        return mds_surface

    def write(self, file, file_ofs):
        """Writes MDSSurface object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        mds_surface_ofs = file_ofs

        # mds_surface.header
        self.header.write(file, file_ofs)

        # mds_surface.vertices
        file_ofs = mds_surface_ofs + self.header.ofs_vertices
        for vertex in self.vertices:

            vertex.write(file, file_ofs)

            file_ofs = file_ofs + MDSVertex.format_size + \
                vertex.num_weights * MDSWeight.format_size

        # mds_surface.triangles
        file_ofs = mds_surface_ofs + self.header.ofs_triangles
        for triangle in self.triangles:

            triangle.write(file, file_ofs)

            file_ofs = file_ofs + MDSTriangle.format_size

        # mds_surface.collapse_map
        file_ofs = mds_surface_ofs + self.header.ofs_collapse_map
        self.collapse_map.write(file, file_ofs)

        # mds_surface.bone_refs
        file_ofs = mds_surface_ofs + self.header.ofs_bone_refs
        self.bone_refs.write(file, file_ofs)


class MDSBoneInfo:
    """Frame independent bone information.

    Attributes:

        name (bytes): bone name, ASCII encoded, null-terminated, length 64.
        parent_bone (int): parent bone as index into the list of bone_infos.
        torso_weight (float): TODO.
        parent_dist (float): distance to parent bone.
        flags (int): this bone is either a bone (0) or a tag (1).

    File encodings:

        name: 64*ASCII (C-String).
        parent_bone: INT32.
        torso_weight: F32, IEEE-754.
        parent_dist: F32, IEEE-754.
        flags: UINT32.

    Background:

        See "skeletal animation".
    """

    format = '<64siffI'
    format_size = struct.calcsize(format)

    name_len = 64
    flags_default_value = 0
    bone_flag_tag = 1  # this bone is actually a tag

    def __init__(self, name, parent_bone, torso_weight, parent_dist, flags):

        self.name = name
        self.parent_bone = parent_bone
        self.torso_weight = torso_weight
        self.parent_dist = parent_dist
        self.flags = flags

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDSBoneInfo object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_bone_info (MDSBoneInfo): MDSBoneInfo object.
        """

        file.seek(file_ofs)

        name, parent_bone, torso_weight, parent_dist, flags \
            = struct.unpack(MDSBoneInfo.format,
                            file.read(MDSBoneInfo.format_size))

        mds_bone_info = MDSBoneInfo(name, parent_bone, torso_weight,
                                    parent_dist, flags)

        return mds_bone_info

    def write(self, file, file_ofs):
        """Writes MDSBoneInfo object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSBoneInfo.format, self.name, self.parent_bone,
                               self.torso_weight, self.parent_dist,
                               self.flags))


class MDSBoneFrameCompressed:
    """Bone location and orientation in a specific frame.

    Attributes:

        orientation (tuple): orientation as Tait–Bryan angles in frame as tuple
            of shorts. Index 0 = pitch, index 1 = yaw, index 2 = roll. Index 3
            is not used and contains a default value.
        location_dir (tuple): location in angles as tuple of shorts.
            Index 0 = yaw, index 1 = pitch.

    File encodings:

        orientation: 4*INT16.
        location_dir: 2*INT16.

    Notes:

        Bone orientation values are given as compressed 16-Bit integers. To
        convert this range to a range of floats, the given value is linearly
        mapped. For this, a hard coded scale value is used. The result is
        an angle in the range of [0, 360). To convert the angles to a rotation
        matrix, we first roll, then pitch, then yaw (intrinsic).
        TODO recheck signed integer to angle range

        Bone location values are given as offset direction from a parent bone.
        Combined with the parent_dist value in the bone info field and the
        parent bones frame location, one can calculate the bones frame
        location. Linear mapping is done the same way as with the bone
        orientation values to get the angle values from the range of integer
        to the range of floats. To convert the angles to a direction vector,
        we first pitch (latitude), then yaw (longitude).
    """

    format = '<hhhhhh'
    format_size = struct.calcsize(format)

    orientation_scale = 360 / 65536.0  # TODO recheck with source
    location_dir_scale = 360 / 4095.0  # TODO recheck with source

    angle_none_default = 777

    def __init__(self, orientation, location_dir):

        self.orientation = orientation
        self.location_dir = location_dir

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDSBoneFrameCompressed object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_bone_frame_compressed (MDSBoneFrameCompressed):
                MDSBoneFrameCompressed object.
        """

        file.seek(file_ofs)

        pitch, yaw, roll, none, off_pitch, off_yaw \
            = struct.unpack(MDSBoneFrameCompressed.format,
                            file.read(MDSBoneFrameCompressed.format_size))

        orientation = (pitch, yaw, roll, none)
        location_dir = (off_yaw, off_pitch)

        mds_bone_frame_compressed = MDSBoneFrameCompressed(orientation,
                                                           location_dir)

        return mds_bone_frame_compressed

    def write(self, file, file_ofs):
        """Writes MDSBoneFrameCompressed object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSBoneFrameCompressed.format,
                               self.orientation[0], self.orientation[1],
                               self.orientation[2], self.orientation[3],
                               self.location_dir[1], self.location_dir[0]))


class MDSFrameInfo:
    """General information about a frame.

    Attributes:

        min_bound (tuple): location coordinates of min corner of minimum
            bounding box as tuple of floats.
        max_bound (tuple): location coordinates of max corner of minimum
            bounding box as tuple of floats.
        local_origin (tuple): TODO
        radius (float): TODO
        root_bone_location (tuple): TODO

    File encodings:

        min_bound: 3*F32, IEEE-754.
        max_bound: 3*F32, IEEE-754.
        local_origin: 3*F32, IEEE-754.
        radius: F32, IEEE-754.
        root_bone_location: 3*F32, IEEE-754.

    Notes:

        Describes mostly bounding box information. (TODO For frustum culling?)
    """

    format = '<3f3f3f1f3f'
    format_size = struct.calcsize(format)

    def __init__(self, min_bound, max_bound, local_origin, radius,
                 root_bone_location):

        self.min_bound = min_bound
        self.max_bound = max_bound
        self.local_origin = local_origin
        self.radius = radius
        self.root_bone_location = root_bone_location

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDSFrameInfo object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_frame_info (MDSFrameInfo): MDSFrameInfo object.
        """

        file.seek(file_ofs)

        min_bound_x, min_bound_y, min_bound_z, \
            max_bound_x, max_bound_y, max_bound_z, \
            local_origin_x, local_origin_y, local_origin_z, \
            radius, \
            root_bone_location_x, root_bone_location_y, root_bone_location_z \
            = struct.unpack(MDSFrameInfo.format,
                            file.read(MDSFrameInfo.format_size))

        mds_frame_info \
            = MDSFrameInfo((min_bound_x, min_bound_y, min_bound_z),
                           (max_bound_x, max_bound_y, max_bound_z),
                           (local_origin_x, local_origin_y, local_origin_z),
                           radius,
                           (root_bone_location_x, root_bone_location_y,
                            root_bone_location_z))

        return mds_frame_info

    def write(self, file, file_ofs):
        """Writes MDSFrameInfo object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSFrameInfo.format,
                               self.min_bound[0], self.min_bound[1],
                               self.min_bound[2], self.max_bound[0],
                               self.max_bound[1], self.max_bound[2],
                               self.local_origin[0], self.local_origin[1],
                               self.local_origin[2], self.radius,
                               self.root_bone_location[0],
                               self.root_bone_location[1],
                               self.root_bone_location[2]))


class MDSFrame:
    """An animation frame. Holds references to general frame information, as
    well as each bones location and orientation values.

    Attributes:

        frame_info (MDSFrameInfo): reference to MDSFrameInfo object.
        bone_frames_compressed (list): list of MDSBoneFrameCompressed objects,
            size=num_bones.
    """

    def __init__(self):

        self.frame_info = None
        self.bone_frames_compressed = []

    @staticmethod
    def read(file, file_ofs, num_bones):
        """Reads file data into an MDSFrame object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_bones (int): number of bones.

        Returns:

            mds_frame (MDSFrame): MDSFrame object.
        """

        mds_frame = MDSFrame()

        # mds_frame.header
        mds_frame.frame_info = MDSFrameInfo.read(file, file_ofs)

        # mds_frame.bone_frames_compressed
        file_ofs = file_ofs + MDSFrameInfo.format_size

        for i in range(0, num_bones):

            bone_frame_compressed = MDSBoneFrameCompressed.read(file, file_ofs)
            mds_frame.bone_frames_compressed.append(bone_frame_compressed)

            file_ofs = file_ofs + MDSBoneFrameCompressed.format_size

        return mds_frame

    def write(self, file, file_ofs):
        """Writes MDSFrame object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        # mds_frame.frame_info
        self.frame_info.write(file, file_ofs)

        # mds_frame.bone_frames_compressed
        file_ofs = file_ofs + MDSFrameInfo.format_size

        for bone_frame_compressed in self.bone_frames_compressed:

            file.seek(file_ofs)

            bone_frame_compressed.write(file, file_ofs)

            file_ofs = file_ofs + MDSBoneFrameCompressed.format_size


class MDSHeader:
    """General information about MDS data.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, reads "MDSW".
        version (int): version number, latest known is 4.
        name (bytes): model name, usually its pathname, ASCII encoded,
            null-terminated, length 64.
        lod_scale (int): TODO.
        lod_bias (int): TODO.
        num_frames (int): number of animation frames.
        num_bones (int): number of bones.
        ofs_frames (int): file offset to field of frames.
        ofs_bone_infos (int): file offset to field of bone infos.
        torso_parent_bone (int): TODO.
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
        num_frames: UINT32.
        num_bones: UINT32.
        ofs_frames: UINT32.
        ofs_bone_infos: UINT32.
        torso_parent_bone: UINT32.
        num_surfaces: UINT32.
        ofs_surfaces: UINT32.
        num_tags: UINT32.
        ofs_tags: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4sI64sff10I'
    format_size = struct.calcsize(format)
    ident = b'MDSW'
    version = 4
    name_len = 64

    def __init__(self, ident, version, name, lod_scale, lod_bias, num_frames,
                 num_bones, ofs_frames, ofs_bone_infos,
                 torso_parent_bone, num_surfaces, ofs_surfaces, num_tags,
                 ofs_tags, ofs_end):

        self.ident = ident
        self.version = version
        self.name = name

        self.lod_scale = lod_scale
        self.lod_bias = lod_bias

        self.num_frames = num_frames
        self.num_bones = num_bones

        self.ofs_frames = ofs_frames
        self.ofs_bone_infos = ofs_bone_infos

        self.torso_parent_bone = torso_parent_bone

        self.num_surfaces = num_surfaces
        self.ofs_surfaces = ofs_surfaces
        self.num_tags = num_tags
        self.ofs_tags = ofs_tags

        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDSHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mds_header (MDSHeader): MDSHeader object.
        """

        file.seek(file_ofs)

        ident, version, name, lod_scale, lod_bias, num_frames, num_bones, \
            ofs_frames, ofs_bone_infos, torso_parent_bone, \
            num_surfaces, ofs_surfaces, num_tags, ofs_tags, ofs_end \
            = struct.unpack(MDSHeader.format,
                            file.read(MDSHeader.format_size))

        if ident != MDSHeader.ident:
            raise Exception("Failed reading MDS file. Reason: MDSHeader.ident."
                            " Make sure the file is indeed MDS.")

        mds_header = MDSHeader(ident, version, name, lod_scale, lod_bias,
                               num_frames, num_bones, ofs_frames,
                               ofs_bone_infos, torso_parent_bone, num_surfaces,
                               ofs_surfaces, num_tags, ofs_tags, ofs_end)

        return mds_header

    def write(self, file, file_ofs):
        """Writes MDSHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDSHeader.format, self.ident, self.version,
                               self.name, self.lod_scale, self.lod_bias,
                               self.num_frames, self.num_bones,
                               self.ofs_frames, self.ofs_bone_infos,
                               self.torso_parent_bone, self.num_surfaces,
                               self.ofs_surfaces, self.num_tags,
                               self.ofs_tags, self.ofs_end))


class MDS:
    """Holds references to all MDS data.

    Attributes:

        header (MDSHeader): reference to MDSHeader object.
        frames (list): list of MDSFrame objects, size=num_frames.
        bone_infos (list): list of MDSBoneInfo objects, size=num_bones.
        surfaces (list): list of MDSSurface objects, size=num_surfaces.
        tags (list): list of MDSTag objects, size=num_tags.
    """

    # TODO max_frames?
    max_tags = 128
    max_surfaces = 32
    max_bones = 128

    max_triangles = 8192  # per surface
    # TODO max_shaders, max_shader_vertices?
    max_vertices = 6000  # per surface

    max_weights = 3  # per vertex

    weights_sum = 1.0
    min_weight_value = 0.0
    max_weight_value = 1.0

    def __init__(self):

        self.header = None
        self.frames = []
        self.bone_infos = []
        self.surfaces = []
        self.tags = []

    @staticmethod
    def read(file_path):
        """Reads a binary encoded MDS file into an MDS object.

        Args:

            file_path (str): path to MDS file.

        Returns:

            mds (MDS): MDS object.
        """

        with open(file_path, 'rb') as file:

            timer = timer_m.Timer()
            reporter_m.info("Reading MDS file: {} ...".format(file_path))

            mds = MDS()

            # mds.header
            file_ofs = 0
            mds.header = MDSHeader.read(file, file_ofs)

            # mds.frames
            file_ofs = mds.header.ofs_frames
            for i in range(0, mds.header.num_frames):

                mds_frame = MDSFrame.read(file, file_ofs, mds.header.num_bones)
                mds.frames.append(mds_frame)

                file_ofs = file_ofs + MDSFrameInfo.format_size + \
                    mds.header.num_bones * MDSBoneFrameCompressed.format_size

            # mds.bone_infos
            file_ofs = mds.header.ofs_bone_infos
            for i in range(0, mds.header.num_bones):

                mds_bone_info = MDSBoneInfo.read(file, file_ofs)
                mds.bone_infos.append(mds_bone_info)

                file_ofs = file_ofs + MDSBoneInfo.format_size

            # mds.surfaces
            file_ofs = mds.header.ofs_surfaces
            for i in range(0, mds.header.num_surfaces):

                mds_surface = MDSSurface.read(file, file_ofs)
                mds.surfaces.append(mds_surface)

                file_ofs = file_ofs + mds_surface.header.ofs_end

            # mds.tags
            file_ofs = mds.header.ofs_tags
            for i in range(0, mds.header.num_tags):

                mds_tag = MDSTag.read(file, file_ofs)
                mds.tags.append(mds_tag)

                file_ofs = file_ofs + MDSTag.format_size

            time = timer.time()
            reporter_m.info("Reading MDS file DONE (time={})".format(time))

            return mds

    def write(self, file_path):
        """Writes MDS object to file with binary encoding.

        Args:

            file_path (str): path to MDS file.
        """

        with open(file_path, 'wb') as file:

            timer = timer_m.Timer()
            reporter_m.info("Writing MDS file: {} ...".format(file_path))

            # mds.header
            file_ofs = 0
            self.header.write(file, file_ofs)

            # mds.frames
            file_ofs = self.header.ofs_frames
            for frame in self.frames:

                frame.write(file, file_ofs)

                file_ofs = file_ofs + MDSFrameInfo.format_size + \
                    self.header.num_bones * MDSBoneFrameCompressed.format_size

            # mds.bone_infos
            file_ofs = self.header.ofs_bone_infos
            for mds_bone_info in self.bone_infos:

                mds_bone_info.write(file, file_ofs)

                file_ofs = file_ofs + MDSBoneInfo.format_size

            # mds.surfaces
            file_ofs = self.header.ofs_surfaces
            for surface in self.surfaces:

                surface.write(file, file_ofs)

                file_ofs = file_ofs + surface.header.ofs_end

            # mds.tags
            file_ofs = self.header.ofs_tags
            for tag in self.tags:

                tag.write(file, file_ofs)

                file_ofs = file_ofs + MDSTag.format_size

            time = timer.time()
            reporter_m.info("Writing MDS file DONE (time={})".format(time))
