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

"""In-memory representation of the MDC file format. Provides file read and file
write functions to deal with the formats binary encoding.

Notes:

    The file format is stored as a byte stream to file. Data types are encoded
    in little-endian byte order. If not else specified, all coordinates are
    given in cartesian space. Convention is right-handed: x points forward,
    y points left, z points up.

Background:

    MDC is a compressed version of MD3.

    MD3 is defined as a triangle mesh using morph target animation. Surfaces
    make up the basic model. They are described by geometry, color and
    animation data. Tags complement the format.

    Geometry of a surface is described by grouping vertices into a triangle.
    Triangles are then grouped into a surface.

    Colorization of a surface is done by defining UV-maps and references to
    shaders. The UV-maps are used to color surfaces with solid color from a 2D
    image. Shaders manipulate surface properties. These properties define how
    the surface interacts with light sources present in a scene. Additionally
    vertex normals manipulate the shading of a surface.

    Animation of a surface is done by storing vertex positions per frame. This
    animation technique is also known as "morph target animation". The way it
    works is that for each key frame a series of vertex positions is stored.
    Between two successive frames, the vertices are then interpolated between
    the positions. MD3 stores absolute vertex positions as opposed to MDC,
    which can store offsets relative to a base frame.

    Tags provide the possibility to attach external models to the model.

    The major difference between MDC and MD3 is compression of animation data.
    In MDC, the coordinates of vertices in each frame may be stored as 8-Bit
    offset values. MD3 always stores 16-Bit absolute values. The offset values
    are relative to a pre-calculated base frame. This allows MDC to have a
    compression rate of nearly 50% in good cases compared to MD3. Those
    rates are achieved when the models vertex coordinates do not travel large
    distances over several successive key frames. For models whose animated
    vertex coordinates change across great distances regularly, the rate of
    compression goes down, as more base frames are needed. In such a case MD3
    might be the better choice, as it is more precise and faster to calculate.
    If the model is not animated, no compression is done and the format is
    identical to MD3 in terms of rendered result.
"""

import struct


class MDCCompFrameIndices:
    """Indices into the list of compressed frame vertices.

    Attributes:

        indices (list): indices into the list of comp_vertices for this
            surface, size=num_frames.

    File encodings:

        indices: num_frames*UINT16.

    Notes:

        Surfaces hold two seperate lists to store the vertex coordinates either
        as base or compressed. The indices are used to retrieve the index into
        the list of compressed frames for a specific frame. If a frame is not
        compressed, the retrieved value will be -1.
    """

    format = '<H'
    format_size = struct.calcsize(format)

    def __init__(self, indices):

        self.indices = indices

    @staticmethod
    def read(file, file_ofs, num_frames):
        """Reads file data into an MDCCompFrameIndices object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_frames(int): number of frames.

        Returns:

            mdc_comp_frame_indices (MDCCompFrameIndices):
                MDCCompFrameIndices object.
        """

        indices = []

        file.seek(file_ofs)

        for i in range(0, num_frames):

            index = struct.unpack(MDCCompFrameIndices.format,
                                  file.read(MDCCompFrameIndices.format_size))
            indices.append(index[0])

        mdc_comp_frame_indices = MDCCompFrameIndices(indices)

        return mdc_comp_frame_indices

    def write(self, file, file_ofs):
        """Writes MDCCompFrameIndices object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        for i in range(0, len(self.indices)):

            file.write(struct.pack(MDCCompFrameIndices.format,
                                   self.indices[i]))


class MDCBaseFrameIndices:
    """Indices into the list of base frame vertices.

    Attributes:

        indices (list): indices into the list of base_vertices for this
            surface, size=num_frames.

    File encodings:

        indices: num_frames*UINT16.

    Notes:

        Surfaces hold two seperate lists to store the vertex coordinates either
        as base or compressed. The indices are used to retrieve the index into
        the list of base frames for a specific frame.
    """

    format = '<H'
    format_size = struct.calcsize(format)

    def __init__(self, indices):

        self.indices = indices

    @staticmethod
    def read(file, file_ofs, num_frames):
        """Reads file data into an MDCBaseFrameIndices object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_frames(int): number of frames.

        Returns:

            mdc_base_frame_indices (MDCBaseFrameIndices):
                MDCBaseFrameIndices object.
        """

        indices = []

        file.seek(file_ofs)

        for i in range(0, num_frames):

            index = struct.unpack(MDCBaseFrameIndices.format,
                                  file.read(MDCBaseFrameIndices.format_size))
            indices.append(index[0])

        mdc_base_frame_indices = MDCBaseFrameIndices(indices)

        return mdc_base_frame_indices

    def write(self, file, file_ofs):
        """Writes MDCBaseFrameIndices object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        for i in range(0, len(self.indices)):

            file.write(struct.pack(MDCBaseFrameIndices.format,
                                   self.indices[i]))


class MDCCompFrameVertex:
    """Vertex location and normal in a compressed frame.

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO
    """

    format = '<3B1B'
    format_size = struct.calcsize(format)

    def __init__(self, location_offset, normal):

        self.location_offset = location_offset
        self.normal = normal

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCCompFrameVertex object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_comp_frame_vertex (MDCCompFrameVertex):
                MDCCompFrameVertex object.
        """

        file.seek(file_ofs)

        location_offset_x, location_offset_y, location_offset_z, normal \
            = struct.unpack(MDCCompFrameVertex.format,
                            file.read(MDCCompFrameVertex.format_size))

        location_offset \
            = (location_offset_x, location_offset_y, location_offset_z)
        mdc_comp_frame_vertex = MDCCompFrameVertex(location_offset, normal)

        return mdc_comp_frame_vertex

    def write(self, file, file_ofs):
        """Writes MDCCompFrameVertex object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCCompFrameVertex.format,
                               self.location_offset[0],
                               self.location_offset[1],
                               self.location_offset[2],
                               self.normal))


class MDCBaseFrameVertex:
    """Vertex location and normal in a base frame.

    Attributes:

        TODO

    File encodings:

        TODO

    Background:

        TODO
    """

    format = '<3h2B'
    format_size = struct.calcsize(format)
    location_scale = 1.0 / 64

    def __init__(self, location, normal):

        self.location = location
        self.normal = normal

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCBaseFrameVertex object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_base_frame_vertex (MDCBaseFrameVertex):
                MDCBaseFrameVertex object.
        """

        file.seek(file_ofs)

        location_x, location_y, location_z, normal_lon, normal_lat \
            = struct.unpack(MDCBaseFrameVertex.format,
                            file.read(MDCBaseFrameVertex.format_size))

        location = (location_x, location_y, location_z)
        normal = (normal_lat, normal_lon)

        mdc_base_frame_vertex = MDCBaseFrameVertex(location, normal)

        return mdc_base_frame_vertex

    def write(self, file, file_ofs):
        """Writes MDCBaseFrameVertex object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCBaseFrameVertex.format, self.location[0],
                               self.location[1], self.location[2],
                               self.normal[1], self.normal[0]))


class MDCTexCoords:
    """Texture coordinates for a single vertex.

    Attributes:

        tex_coords (tuple): u and v coordinates in UV-space as tuple.

    File encodings:

        tex_coords: 2*F32, IEEE-754.

    Notes:

        UV coordinates are given so that u points right, and v points down.
        Each value should be in range of [0, 1]. Values outside this range are
        interpreted as repeating. Each vertex is mapped exactly once to
        UV-space. Therefore, seams will most likely cause an exporter to add
        additional vertices along the seam line to enforce bijection. UV-maps
        are stored once per surface.

    Background:

        The UV-map is used to color the surface with solid color from a 2D
        image. Texture coordinates make up UV-space.
    """

    format = '<2f'
    format_size = struct.calcsize(format)

    def __init__(self, tex_coords):

        self.tex_coords = tex_coords

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCTexCoords object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_tex_coords (MDCTexCoords): MDCTexCoords object.
        """

        file.seek(file_ofs)

        tex_coord_u, tex_coord_v \
            = struct.unpack(MDCTexCoords.format,
                            file.read(MDCTexCoords.format_size))

        tex_coords = (tex_coord_u, tex_coord_v)

        mdc_tex_coords = MDCTexCoords(tex_coords)

        return mdc_tex_coords

    def write(self, file, file_ofs):
        """Writes MDCTexCoords object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCTexCoords.format,
                               self.tex_coords[0],
                               self.tex_coords[1]))


class MDCShader:
    """Shader for a surface.

    Attributes:

        name (bytes): shader name, ASCII encoded, null-terminated, length 64.
        shader_index (int): used in-game only.

    File encodings:

        name: 64*ASCII (C-String).
        shader_index: UINT32.

    Notes:

        The name of the shader is a reference to either a shader inside a
        script file, or a path from top level directory to an texture image.
        Suffixes like .tga or .jpg can be omitted. Search order is:
        shader, .tga, .jpg. First found will be used.

    Background:

        Shaders manipulate surface properties. These properties define how the
        surface interacts with light sources present in a scene.

        The term can be a bit confusing, since a shader in this context can
        either mean a script file (with references to texture images) or an
        texture image.
    """

    format = '<64sI'
    format_size = struct.calcsize(format)
    name_len = 64
    shader_index = 0

    def __init__(self, name, shader_index):

        self.name = name
        self.shader_index = shader_index

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCShader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_shader (MDCShader): MDCShader object.
        """

        file.seek(file_ofs)

        name, shader_index \
            = struct.unpack(MDCShader.format,
                            file.read(MDCShader.format_size))

        mdc_shader = MDCShader(name, shader_index)

        return mdc_shader

    def write(self, file, file_ofs):
        """Writes MDCShader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCShader.format,
                               self.name, self.shader_index))


class MDCTriangle:
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
        """Reads file data into an MDCTriangle object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_triangle (MDCTriangle): MDCTriangle object.
        """

        file.seek(file_ofs)

        indices = struct.unpack(MDCTriangle.format,
                                file.read(MDCTriangle.format_size))

        mdc_triangle = MDCTriangle(indices)

        return mdc_triangle

    def write(self, file, file_ofs):
        """Writes MDCTriangle object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCTriangle.format,
                               self.indices[0], self.indices[1],
                               self.indices[2]))


class MDCSurfaceHeader:
    """General information about a surface.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, latest known is 
            7.
        name (bytes): surface name, ASCII encoded, null-terminated, length 64.
        flags (int): not used.
        num_comp_frames (int): number of compressed animation frames.
        num_base_frames (int): number of base animation frames.
        num_shaders (int): number of shaders.
        num_vertices (int): number of vertices.
        num_triangles (int): number of triangles.
        ofs_triangles (int): file offset to field of triangles.
        ofs_shaders (int): file offset to field of shaders.
        ofs_tex_coords (int): file offset to field of texture coordinates.
        ofs_base_vertices (int): file offset to field of base vertices.
        ofs_comp_vertices (int): file offset to field of compressed vertices.
        ofs_base_frame_indices (int): file offset to field of base vertex
            indices.
        ofs_comp_frame_indices (int): file offset to field of compressed vertex
            indices.
        ofs_end (int): file offset to end of surface.

    File encodings:

        ident: 4*ASCII.
        name: 64*ASCII (C-String).
        flags: UINT32.
        num_comp_frames: UINT32.
        num_base_frames: UINT32.
        num_shaders: UINT32.
        num_vertices: UINT32.
        num_triangles: UINT32.
        ofs_triangles: UINT32.
        ofs_shaders: UINT32.
        ofs_tex_coords: UINT32.
        ofs_base_vertices: UINT32.
        ofs_comp_vertices: UINT32.
        ofs_base_frame_indices: UINT32.
        ofs_comp_frame_indices: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4s64s14I'
    format_size = struct.calcsize(format)
    ident = b'\x07\x00\x00\x00'
    name_len = 64

    def __init__(self, ident, name, flags, num_comp_frames, num_base_frames,
                 num_shaders, num_vertices, num_triangles, ofs_triangles,
                 ofs_shaders, ofs_tex_coords, ofs_base_vertices,
                 ofs_comp_vertices, ofs_base_frame_indices,
                 ofs_comp_frame_indices, ofs_end):

        self.ident = ident
        self.name = name
        self.flags = flags
        self.num_comp_frames = num_comp_frames
        self.num_base_frames = num_base_frames
        self.num_shaders = num_shaders
        self.num_vertices = num_vertices
        self.num_triangles = num_triangles
        self.ofs_triangles = ofs_triangles
        self.ofs_shaders = ofs_shaders
        self.ofs_tex_coords = ofs_tex_coords
        self.ofs_base_vertices = ofs_base_vertices
        self.ofs_comp_vertices = ofs_comp_vertices
        self.ofs_base_frame_indices = ofs_base_frame_indices
        self.ofs_comp_frame_indices = ofs_comp_frame_indices
        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCSurfaceHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_surface_header (MDCSurfaceHeader): MDCSurfaceHeader object.
        """

        file.seek(file_ofs)

        ident, name, flags, num_comp_frames, num_base_frames, num_shaders, \
            num_vertices, num_triangles, ofs_triangles, ofs_shaders, \
            ofs_tex_coords, ofs_base_vertices, ofs_comp_vertices, \
            ofs_base_frame_indices, ofs_comp_frame_indices, ofs_end \
            = struct.unpack(MDCSurfaceHeader.format,
                            file.read(MDCSurfaceHeader.format_size))

        mdc_surface_header = MDCSurfaceHeader(ident, name, flags,
                                              num_comp_frames,
                                              num_base_frames, num_shaders,
                                              num_vertices, num_triangles,
                                              ofs_triangles, ofs_shaders,
                                              ofs_tex_coords,
                                              ofs_base_vertices,
                                              ofs_comp_vertices,
                                              ofs_base_frame_indices,
                                              ofs_comp_frame_indices, ofs_end)

        return mdc_surface_header

    def write(self, file, file_ofs):
        """Writes MDCSurfaceHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCSurfaceHeader.format, self.ident, self.name,
                               self.flags, self.num_comp_frames,
                               self.num_base_frames, self.num_shaders,
                               self.num_vertices, self.num_triangles,
                               self.ofs_triangles, self.ofs_shaders,
                               self.ofs_tex_coords, self.ofs_base_vertices,
                               self.ofs_comp_vertices,
                               self.ofs_base_frame_indices,
                               self.ofs_comp_frame_indices, self.ofs_end))


class MDCSurface:
    """A surface of the model.

    Attributes:

        header (MDCSurfaceHeader): reference to MDCSurfaceHeader object.
        triangles (list): list of MDCTriangle objects, size=num_triangles.
        shaders (list): list of MDCShader objects, size=num_shaders.
        tex_coords (list): list of MDCTexCoords objects, size=num_vertices.
        base_vertices (list): list of list objects, size=num_base_frames. Each
            nested list contains MDCBaseFrameVertex objects, size=num_vertices.
            Access like this: base_vertices[num_base_frame][num_vertex].
        comp_vertices (list): list of list objects, size=num_comp_frames. Each
            nested list contains MDCCompFrameVertex objects, size=num_vertices.
            Access like this: comp_vertices[num_comp_frame][num_vertex].
        base_frame_indices (MDCBaseFrameIndices): reference to
            MDCBaseFrameIndices object.
        comp_frame_indices (MDCCompFrameIndices): reference to
            MDCCompFrameIndices object.

    Notes:

        TODO how base frames are calculated.

    Background:

        Surfaces are described by geometry, color and animation data. A model
        can consist of multiple surfaces.
    """

    def __init__(self):

        self.header = None
        self.triangles = []
        self.shaders = []
        self.tex_coords = []
        self.base_vertices = []
        self.comp_vertices = []
        self.base_frame_indices = None
        self.comp_frame_indices = None

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCSurface object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_surface (MDCSurface): MDCSurface object.
        """

        mdc_surface = MDCSurface()

        mdc_surface_ofs = file_ofs

        # mdc_surface.header
        mdc_surface.header = MDCSurfaceHeader.read(file, file_ofs)

        # mdc_surface.triangles
        file_ofs = mdc_surface_ofs + mdc_surface.header.ofs_triangles

        for _ in range(0, mdc_surface.header.num_triangles):

            mdc_triangle = MDCTriangle.read(file, file_ofs)
            mdc_surface.triangles.append(mdc_triangle)

            file_ofs = file_ofs + MDCTriangle.format_size

        # mdc_surface.shaders
        file_ofs = mdc_surface_ofs + mdc_surface.header.ofs_shaders

        for _ in range(0, mdc_surface.header.num_shaders):

            mdc_shader = MDCShader.read(file, file_ofs)
            mdc_surface.shaders.append(mdc_shader)

            file_ofs = file_ofs + MDCShader.format_size

        # mdc_surface.tex_coords
        file_ofs = mdc_surface_ofs + mdc_surface.header.ofs_tex_coords

        for i in range(0, mdc_surface.header.num_vertices):

            mdc_tex_coords = MDCTexCoords.read(file, file_ofs)
            mdc_surface.tex_coords.append(mdc_tex_coords)

            file_ofs = file_ofs + MDCTexCoords.format_size

        # mdc_surface.base_vertices
        file_ofs = mdc_surface_ofs + mdc_surface.header.ofs_base_vertices

        for i in range(0, mdc_surface.header.num_base_frames):

            base_vertices = []

            for j in range(0, mdc_surface.header.num_vertices):

                mdc_base_frame_vertex = MDCBaseFrameVertex.read(file, file_ofs)
                base_vertices.append(mdc_base_frame_vertex)

                file_ofs = file_ofs + MDCBaseFrameVertex.format_size

            mdc_surface.base_vertices.append(base_vertices)

        # mdc_surface.comp_vertices
        file_ofs = mdc_surface_ofs + mdc_surface.header.ofs_comp_vertices

        for i in range(0, mdc_surface.header.num_comp_frames):

            comp_vertices = []

            for j in range(0, mdc_surface.header.num_vertices):

                mdc_comp_frame_vertex = MDCCompFrameVertex.read(file, file_ofs)
                comp_vertices.append(mdc_comp_frame_vertex)

                file_ofs = file_ofs + MDCCompFrameVertex.format_size

            mdc_surface.comp_vertices.append(comp_vertices)

        # mdc_surface.base_frame_indices
        file_ofs = mdc_surface_ofs + mdc_surface.header.ofs_base_frame_indices
        num_frames = \
            mdc_surface.header.num_base_frames + \
            mdc_surface.header.num_comp_frames

        mdc_surface.base_frame_indices = MDCBaseFrameIndices.read(file,
                                                                  file_ofs,
                                                                  num_frames)

        # mdc_surface.comp_frame_indices
        file_ofs = mdc_surface_ofs + mdc_surface.header.ofs_comp_frame_indices
        num_frames = \
            mdc_surface.header.num_base_frames + \
            mdc_surface.header.num_comp_frames

        mdc_surface.comp_frame_indices = MDCCompFrameIndices.read(file,
                                                                  file_ofs,
                                                                  num_frames)

        return mdc_surface

    def write(self, file, file_ofs):
        """Writes MDCSurface object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        mdc_surface_ofs = file_ofs

        # mdc_surface.header
        self.header.write(file, file_ofs)

        # mdc_surface.triangles
        file_ofs = mdc_surface_ofs + self.header.ofs_triangles

        for mdc_triangle in self.triangles:

            mdc_triangle.write(file, file_ofs)

            file_ofs = file_ofs + MDCTriangle.format_size

        # mdc_surface.shaders
        file_ofs = mdc_surface_ofs + self.header.ofs_shaders

        for mdc_shader in self.shaders:

            mdc_shader.write(file, file_ofs)

            file_ofs = file_ofs + MDCShader.format_size

        # mdc_surface.tex_coords
        file_ofs = mdc_surface_ofs + self.header.ofs_tex_coords

        for mdc_tex_coords in self.tex_coords:

            mdc_tex_coords.write(file, file_ofs)

            file_ofs = file_ofs + MDCTexCoords.format_size

        # mdc_surface.base_vertices
        file_ofs = mdc_surface_ofs + self.header.ofs_base_vertices

        for base_vertices in self.base_vertices:

            for mdc_base_frame_vertex in base_vertices:

                mdc_base_frame_vertex.write(file, file_ofs)

                file_ofs = file_ofs + MDCBaseFrameVertex.format_size

        # mdc_surface.comp_vertices
        file_ofs = mdc_surface_ofs + self.header.ofs_comp_vertices

        for comp_vertices in self.comp_vertices:

            for mdc_comp_frame_vertex in comp_vertices:

                mdc_comp_frame_vertex.write(file, file_ofs)

                file_ofs = file_ofs + MDCCompFrameVertex.format_size

        # mdc_surface.base_frame_indices
        file_ofs = mdc_surface_ofs + self.header.ofs_base_frame_indices

        self.base_frame_indices.write(file, file_ofs)

        # mdc_surface.comp_frame_indices
        file_ofs = mdc_surface_ofs + self.header.ofs_comp_frame_indices

        self.comp_frame_indices.write(file, file_ofs)


class MDCFrameTag:
    """A tag in a specific frame.

    Attributes:

        location (tuple): location coordinates in frame as tuple of shorts.
        orientation (tuple): orientation as euler angles in frame as tuple of
            shorts. Index 0 = pitch, index 1 = yaw, index 2 = roll.

    File encodings:

        location: 3*INT16.
        orientation: 3*INT16.

    Notes:

        To convert location and orientation values to float, a scale value is
        used.

        Orientation values are given as euler angles. Inside file they are
        stored in order of pitch, yaw, roll. Rotation order is: first roll,
        then pitch, then yaw (XYZ, intrinsic).

        Additionally, orientation values should be in range of [-32700, 32700],
        since the hardcoded scale value is 360/32700. TODO value ranges,
        normalized.

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

    format = '<3h3h'
    format_size = struct.calcsize(format)
    location_scale = 1.0 / 64
    orientation_scale = 360.0 / 32700

    def __init__(self, location, orientation):

        self.location = location
        self.orientation = orientation

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCFrameTag object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_frame_tag (MDCFrameTag): MDCFrameTag object.
        """

        file.seek(file_ofs)

        location_x, location_y, location_z,\
            orientation_pitch, orientation_yaw, orientation_roll \
            = struct.unpack(MDCFrameTag.format,
                            file.read(MDCFrameTag.format_size))

        location = (location_x, location_y, location_z)
        orientation = (orientation_pitch, orientation_yaw, orientation_roll)

        mdc_frame_tag = MDCFrameTag(location, orientation)

        return mdc_frame_tag

    def write(self, file, file_ofs):
        """Writes MDCFrameTag object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCFrameTag.format,
                               self.location[0], self.location[1],
                               self.location[2], self.orientation[0],
                               self.orientation[1], self.orientation[2]))


class MDCTagInfo:
    """General information about a tag.

    Attributes:

        name (bytes): name of tag, ASCII encoded, null-terminated, length 64.

    File encodings:

        name: 64*ASCII (C-String).
    """

    format = '<64s'
    format_size = struct.calcsize(format)

    def __init__(self, name):

        self.name = name

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCTagInfo object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_tag_info (MDCTagInfo): MDCTagInfo object.
        """

        file.seek(file_ofs)

        name = struct.unpack(MDCTagInfo.format,
                             file.read(MDCTagInfo.format_size))

        mdc_tag_info = MDCTagInfo(name[0])

        return mdc_tag_info

    def write(self, file, file_ofs):
        """Writes MDCTagInfo object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCTagInfo.format, self.name))


class MDCFrameInfo:
    """General information about a frame.

    Attributes:

        min_bound (tuple): location coordinates of min corner of minimum
            bounding box as tuple of floats.
        max_bound (tuple): location coordinates of max corner of minimum
            bounding box as tuple of floats.
        local_origin (tuple): TODO
        radius (float): TODO
        name (bytes): name of frame, ASCII encoded, null-terminated, length 16,
            does not seem to be used.

    File encodings:

        min_bound: 3*F32, IEEE-754.
        max_bound: 3*F32, IEEE-754.
        local_origin: 3*F32, IEEE-754.
        radius: F32, IEEE-754.
        name: 16*ASCII (C-String).

    Notes:

        Describes mostly bounding box information. (TODO For frustum culling?)
    """

    format = '<10f16s'
    format_size = struct.calcsize(format)
    frame_name = "(mdc frame)"
    name_len = 16

    def __init__(self, min_bound, max_bound, local_origin, radius, name):

        self.min_bound = min_bound
        self.max_bound = max_bound
        self.local_origin = local_origin
        self.radius = radius
        self.name = name

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCFrameInfo object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_frame_info (MDCFrameInfo): MDCFrameInfo object.
        """

        file.seek(file_ofs)

        min_bound_x, min_bound_y, min_bound_z, \
            max_bound_x, max_bound_y, max_bound_z, \
            local_origin_x, local_origin_y, local_origin_z, \
            radius, \
            name \
            = struct.unpack(MDCFrameInfo.format,
                            file.read(MDCFrameInfo.format_size))

        mdc_frame_info \
            = MDCFrameInfo((min_bound_x, min_bound_y, min_bound_z),
                           (max_bound_x, max_bound_y, max_bound_z),
                           (local_origin_x, local_origin_y, local_origin_z),
                           radius,
                           name)

        return mdc_frame_info

    def write(self, file, file_ofs):
        """Writes MDCFrameInfo object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCFrameInfo.format,
                               self.min_bound[0], self.min_bound[1],
                               self.min_bound[2], self.max_bound[0],
                               self.max_bound[1], self.max_bound[2],
                               self.local_origin[0], self.local_origin[1],
                               self.local_origin[2], self.radius, self.name))


class MDCHeader:
    """General information about MDC data.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, reads "IDPC".
        version (int): version number, latest known is 2.
        name (bytes): model name, usually its pathname, ASCII encoded,
            null-terminated, length 64.
        flags (int): not used.
        num_frames (int): number of animation frames.
        num_tags (int): number of tags.
        num_surfaces (int): number of surfaces.
        num_skins (int): not used.
        ofs_frame_infos (int): file offset to field of frame infos.
        ofs_tag_infos (int): file offset to field of tag infos.
        ofs_tags (int): file offset to field of tags.
        ofs_surfaces (int): file offset to field of surfaces.
        ofs_end (int): file offset to end of file.

    File encodings:

        ident: 4*ASCII.
        version: UINT32.
        name: 64*ASCII (C-String).
        flags: UINT32.
        num_frames: UINT32.
        num_tags: UINT32.
        num_surfaces: UINT32.
        num_skins: UINT32.
        ofs_frame_infos: UINT32.
        ofs_tag_infos: UINT32.
        ofs_tags: UINT32.
        ofs_surfaces: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4sI64s10I'
    format_size = struct.calcsize(format)
    ident = b'IDPC'
    version = 2
    name_len = 64

    def __init__(self, ident, version, name, flags, num_frames, num_tags,
                 num_surfaces, num_skins, ofs_frame_infos, ofs_tag_infos,
                 ofs_tags, ofs_surfaces, ofs_end):

        self.ident = ident
        self.version = version
        self.name = name
        self.flags = flags

        self.num_frames = num_frames
        self.num_tags = num_tags
        self.num_surfaces = num_surfaces
        self.num_skins = num_skins

        self.ofs_frame_infos = ofs_frame_infos
        self.ofs_tag_infos = ofs_tag_infos
        self.ofs_tags = ofs_tags
        self.ofs_surfaces = ofs_surfaces
        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDCHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdc_header (MDCHeader): MDCHeader object.
        """

        file.seek(file_ofs)

        ident, version, name, flags, num_frames, num_tags, num_surfaces, \
            num_skins, ofs_frame_infos, ofs_tag_infos, ofs_tags, \
            ofs_surfaces, ofs_end \
            = struct.unpack(MDCHeader.format,
                            file.read(MDCHeader.format_size))

        mdc_header = MDCHeader(ident, version, name, flags, num_frames,
                               num_tags, num_surfaces, num_skins,
                               ofs_frame_infos, ofs_tag_infos, ofs_tags,
                               ofs_surfaces, ofs_end)

        return mdc_header

    def write(self, file, file_ofs):
        """Writes MDCHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDCHeader.format, self.ident, self.version,
                               self.name, self.flags, self.num_frames,
                               self.num_tags, self.num_surfaces,
                               self.num_skins, self.ofs_frame_infos,
                               self.ofs_tag_infos, self.ofs_tags,
                               self.ofs_surfaces, self.ofs_end))


class MDC:
    """Holds references to all MDC data.

    Attributes:

        header (MDCHeader): reference to MDCHeader object.
        frame_infos (list): list of MDCFrameInfo objects, size=num_frames.
        tag_infos (list): list of MDCTagInfo objects, size=num_tags.
        tags (list): list of list objects, size=num_frames. Each nested list
            contains MDCFrameTag objects, size=num_tags. Access like this:
            tags[num_frame][num_tag].
        surfaces (list): list of MDCSurface objects, size=num_surfaces.
    """

    max_lods = 4
    max_frames = 1024
    max_tags = 16
    maxSurfaces = 32

    max_triangles = 8192  # per surface
    max_shaders = 256  # per surface
    max_vertices = 4096  # per surface
    max_shader_vertices = 1025  # per surface

    max_ofs = 127.0
    location_scale = 1.0 / 20
    max_dist = max_ofs * location_scale  # per vertex (6,35)
    max_compression_delta = 0.1

    def __init__(self):

        self.header = None
        self.frame_infos = []
        self.tag_infos = []
        self.tags = []
        self.surfaces = []

    @staticmethod
    def read(file_path):
        """Reads a binary encoded MDC file into an MDC object.

        Args:

            file_path (str): path to MDC file.

        Returns:

            mdc (MDC): MDC object.
        """

        with open(file_path, 'rb') as file:

            mdc = MDC()

            # mdc.header
            file_ofs = 0
            mdc.header = MDCHeader.read(file, file_ofs)

            # mdc.frame_infos
            file_ofs = mdc.header.ofs_frame_infos
            for i in range(0, mdc.header.num_frames):

                mdc_frame_info = MDCFrameInfo.read(file, file_ofs)
                mdc.frame_infos.append(mdc_frame_info)

                file_ofs = file_ofs + MDCFrameInfo.format_size

            # mdc.tag_infos
            file_ofs = mdc.header.ofs_tag_infos
            for i in range(0, mdc.header.num_tags):

                mdc_tag_info = MDCTagInfo.read(file, file_ofs)
                mdc.tag_infos.append(mdc_tag_info)

                file_ofs = file_ofs + MDCTagInfo.format_size

            # mdc.tags
            file_ofs = mdc.header.ofs_tags
            for i in range(0, mdc.header.num_frames):

                mdc_frame_tags = []

                for j in range(0, mdc.header.num_tags):

                    mdc_frame_tag = MDCFrameTag.read(file, file_ofs)
                    mdc_frame_tags.append(mdc_frame_tag)

                    file_ofs = file_ofs + MDCFrameTag.format_size

                mdc.tags.append(mdc_frame_tags)

            # mdc.surfaces
            file_ofs = mdc.header.ofs_surfaces
            for i in range(0, mdc.header.num_surfaces):

                mdc_surface = MDCSurface.read(file, file_ofs)
                mdc.surfaces.append(mdc_surface)

                file_ofs = file_ofs + mdc_surface.header.ofs_end

            return mdc

    def write(self, file_path):
        """Writes MDC object to file with binary encoding.

        Args:

            file_path (str): path to MDC file.
        """

        with open(file_path, 'wb') as file:

            # mdc.header
            file_ofs = 0
            self.header.write(file, file_ofs)

            # mdc.frame_infos
            file_ofs = self.header.ofs_frame_infos
            for mdc_frame_info in self.frame_infos:

                mdc_frame_info.write(file, file_ofs)

                file_ofs = file_ofs + MDCFrameInfo.format_size

            # mdc.tag_infos
            file_ofs = self.header.ofs_tag_infos
            for mdc_tag_info in self.tag_infos:

                mdc_tag_info.write(file, file_ofs)

                file_ofs = file_ofs + MDCTagInfo.format_size

            # mdc.tags
            file_ofs = self.header.ofs_tags
            for mdc_frame_tags in self.tags:

                for mdc_frame_tag in mdc_frame_tags:

                    mdc_frame_tag.write(file, file_ofs)

                    file_ofs = file_ofs + MDCFrameTag.format_size

            # mdc.surfaces
            file_ofs = self.header.ofs_surfaces
            for mdc_surface in self.surfaces:

                mdc_surface.write(file, file_ofs)

                file_ofs = file_ofs + mdc_surface.header.ofs_end
