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

"""In-memory representation of the MD3 file format. Provides file read and file
write functions to deal with the formats binary encoding.

Notes:

    The file format is stored as a byte stream to file. Data types are encoded
    in little-endian byte order. If not else specified, all coordinates are
    given in cartesian space. Convention is right-handed: x points forward,
    y points left, z points up.

Background:

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
"""

import struct


class MD3FrameVertex:
    """Vertex location and normal in a specific frame.

    Attributes:

        location (tuple): location coordinates in frame as tuple of shorts.
        normal (tuple): vertex normal in spherical coordinates as tuple of
            bytes. Index 0 = latitude, index 1 = longitude.

    File encodings:

        location: 3*INT16.
        normal: 2*UINT8.

    Notes:

        Each key frame contains a list of vertex locations and normals.

        Vertex location values from file are given as compressed 16-Bit
        integers. To convert this range to a range of floats, the given value
        is linearly mapped. For this, a hard coded scale value is used.

        Vertex normals manipulate the shading of a surface (for example smooth
        or flat). They are given in spherical coordinates. Since the
        coordinates describe the direction of a normal, the radius value is
        omitted and only latitude and longitude values are given as unsigned
        8-bit values from file. To convert them to cartesian space, the upwards
        vector is first rotated by the latitude value, then by the longitude
        value. Latitude range is within [0, 180] degrees. Longitude range is
        within [0, 360) degrees. To obtain the values in degrees, the given
        range of [0, 255] from file needs to be linearly mapped to [0, 360)
        degrees.
    """

    format = '<3h2B'
    format_size = struct.calcsize(format)
    location_scale = 1.0 / 64
    normal_scale = 360.0 / 255

    def __init__(self, location, normal):

        self.location = location
        self.normal = normal

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MD3FrameVertex object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_frame_vertex (MD3FrameVertex): MD3FrameVertex object.
        """

        file.seek(file_ofs)

        location_x, location_y, location_z, normal_lon, normal_lat \
            = struct.unpack(MD3FrameVertex.format,
                            file.read(MD3FrameVertex.format_size))

        location = (location_x, location_y, location_z)
        normal = (normal_lat, normal_lon)

        md3_frame_vertex = MD3FrameVertex(location, normal)

        return md3_frame_vertex

    def write(self, file, file_ofs):
        """Writes MD3FrameVertex object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3FrameVertex.format, self.location[0],
                               self.location[1], self.location[2],
                               self.normal[1], self.normal[0]))


class MD3TexCoords:
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
        """Reads file data into an MD3TexCoords object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_tex_coords (MD3TexCoords): MD3TexCoords object.
        """

        file.seek(file_ofs)

        tex_coord_u, tex_coord_v \
            = struct.unpack(MD3TexCoords.format,
                            file.read(MD3TexCoords.format_size))

        tex_coords = (tex_coord_u, tex_coord_v)

        md3_tex_coords = MD3TexCoords(tex_coords)

        return md3_tex_coords

    def write(self, file, file_ofs):
        """Writes MD3TexCoords object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3TexCoords.format,
                               self.tex_coords[0],
                               self.tex_coords[1]))


class MD3Shader:
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
        """Reads file data into an MD3Shader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_shader (MD3Shader): MD3Shader object.
        """

        file.seek(file_ofs)

        name, shader_index \
            = struct.unpack(MD3Shader.format,
                            file.read(MD3Shader.format_size))

        md3_shader = MD3Shader(name, shader_index)

        return md3_shader

    def write(self, file, file_ofs):
        """Writes MD3Shader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3Shader.format,
                               self.name, self.shader_index))


class MD3Triangle:
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
        """Reads file data into an MD3Triangle object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_triangle (MD3Triangle): MD3Triangle object.
        """

        file.seek(file_ofs)

        indices = struct.unpack(MD3Triangle.format,
                                file.read(MD3Triangle.format_size))

        md3_triangle = MD3Triangle(indices)

        return md3_triangle

    def write(self, file, file_ofs):
        """Writes MD3Triangle object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3Triangle.format,
                               self.indices[0], self.indices[1],
                               self.indices[2]))


class MD3SurfaceHeader:
    """General information about a surface.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, reads "IDP3".
        name (bytes): surface name, ASCII encoded, null-terminated, length 64.
        flags (int): not used.
        num_frames (int): number of animation frames.
        num_shaders (int): number of shaders.
        num_vertices (int): number of vertices.
        num_triangles (int): number of triangles.
        ofs_triangles (int): file offset to field of triangles.
        ofs_shaders (int): file offset to field of shaders.
        ofs_tex_coords (int): file offset to field of texture coordinates.
        ofs_vertices (int): file offset to field of vertices.
        ofs_end (int): file offset to end of surface.

    File encodings:

        ident: 4*ASCII.
        name: 64*ASCII (C-String).
        flags: UINT32.
        num_frames: UINT32.
        num_shaders: UINT32.
        num_vertices: UINT32.
        num_triangles: UINT32.
        ofs_triangles: UINT32.
        ofs_shaders: UINT32.
        ofs_tex_coords: UINT32.
        ofs_vertices: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4s64s10I'
    format_size = struct.calcsize(format)
    ident = b'IDP3'
    name_len = 64
    shader_name_len = 64
    shader_index = 0
    flags = 0

    def __init__(self, ident, name, flags, num_frames, num_shaders,
                 num_vertices, num_triangles, ofs_triangles, ofs_shaders,
                 ofs_tex_coords, ofs_vertices, ofs_end):

        self.ident = ident
        self.name = name
        self.flags = flags

        self.num_frames = num_frames
        self.num_shaders = num_shaders
        self.num_vertices = num_vertices
        self.num_triangles = num_triangles

        self.ofs_triangles = ofs_triangles
        self.ofs_shaders = ofs_shaders
        self.ofs_tex_coords = ofs_tex_coords
        self.ofs_vertices = ofs_vertices

        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MD3SurfaceHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_surface_header (MD3SurfaceHeader): MD3SurfaceHeader object.
        """

        file.seek(file_ofs)

        ident, name, flags, num_frames, num_shaders, num_vertices, \
            num_triangles, ofs_triangles, ofs_shaders, ofs_tex_coords, \
            ofs_vertices, ofs_end \
            = struct.unpack(MD3SurfaceHeader.format,
                            file.read(MD3SurfaceHeader.format_size))

        md3_surface_header = MD3SurfaceHeader(ident, name, flags, num_frames,
                                              num_shaders, num_vertices,
                                              num_triangles, ofs_triangles,
                                              ofs_shaders, ofs_tex_coords,
                                              ofs_vertices, ofs_end)

        return md3_surface_header

    def write(self, file, file_ofs):
        """Writes MD3SurfaceHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3SurfaceHeader.format,
                               self.ident, self.name, self.flags,
                               self.num_frames, self.num_shaders,
                               self.num_vertices, self.num_triangles,
                               self.ofs_triangles, self.ofs_shaders,
                               self.ofs_tex_coords, self.ofs_vertices,
                               self.ofs_end))


class MD3Surface:
    """A surface of the model.

    Attributes:

        header (MD3SurfaceHeader): reference to MD3SurfaceHeader object.
        triangles (list): list of MD3Triangle objects, size=num_triangles.
        shaders (list): list of MD3Shader objects, size=num_shaders.
        tex_coords (list): list of MD3TexCoords objects, size=num_vertices.
        vertices (list): list of list objects, size=num_frames. Each nested
            list contains MD3FrameVertex objects, size=num_vertices. Access
            like this: vertices[num_frame][num_vertex].

    Background:

        Surfaces are described by geometry, color and animation data. A model
        can consist of multiple surfaces.
    """

    def __init__(self):

        self.header = None
        self.triangles = []
        self.shaders = []
        self.tex_coords = []
        self.vertices = []

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MD3Surface object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_surface (MD3Surface): MD3Surface object.
        """

        md3_surface = MD3Surface()

        md3_surface_ofs = file_ofs

        # md3_surface.header
        md3_surface.header = MD3SurfaceHeader.read(file, file_ofs)

        # md3_surface.triangles
        file_ofs = md3_surface_ofs + md3_surface.header.ofs_triangles

        for i in range(0, md3_surface.header.num_triangles):

            md3_triangle = MD3Triangle.read(file, file_ofs)
            md3_surface.triangles.append(md3_triangle)

            file_ofs = file_ofs + MD3Triangle.format_size

        # md3_surface.shaders
        file_ofs = md3_surface_ofs + md3_surface.header.ofs_shaders

        for i in range(0, md3_surface.header.num_shaders):

            md3_shader = MD3Shader.read(file, file_ofs)
            md3_surface.shaders.append(md3_shader)

            file_ofs = file_ofs + MD3Shader.format_size

        # md3_surface.tex_coords
        file_ofs = md3_surface_ofs + md3_surface.header.ofs_tex_coords

        for i in range(0, md3_surface.header.num_vertices):

            md3_tex_coords = MD3TexCoords.read(file, file_ofs)
            md3_surface.tex_coords.append(md3_tex_coords)

            file_ofs = file_ofs + MD3TexCoords.format_size

        # md3_surface.vertices
        file_ofs = md3_surface_ofs + md3_surface.header.ofs_vertices
        for i in range(0, md3_surface.header.num_frames):

            md3_frame_vertices = []

            for j in range(0, md3_surface.header.num_vertices):

                md3_frame_vertex = MD3FrameVertex.read(file, file_ofs)
                md3_frame_vertices.append(md3_frame_vertex)

                file_ofs = file_ofs + MD3FrameVertex.format_size

            md3_surface.vertices.append(md3_frame_vertices)

        return md3_surface

    def write(self, file, file_ofs):
        """Writes MD3Surface object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        md3_surface_ofs = file_ofs

        # md3_surface.header
        self.header.write(file, file_ofs)

        # md3_surface.triangles
        file_ofs = md3_surface_ofs + self.header.ofs_triangles

        for md3_triangle in self.triangles:

            md3_triangle.write(file, file_ofs)

            file_ofs = file_ofs + MD3Triangle.format_size

        # md3_surface.shaders
        file_ofs = md3_surface_ofs + self.header.ofs_shaders

        for md3_shader in self.shaders:

            md3_shader.write(file, file_ofs)

            file_ofs = file_ofs + MD3Shader.format_size

        # md3_surface.tex_coords
        file_ofs = md3_surface_ofs + self.header.ofs_tex_coords

        for md3_tex_coords in self.tex_coords:

            md3_tex_coords.write(file, file_ofs)

            file_ofs = file_ofs + MD3TexCoords.format_size

        # md3_surface.vertices
        file_ofs = md3_surface_ofs + self.header.ofs_vertices

        for md3_frame_vertices in self.vertices:

            for md3_frame_vertex in md3_frame_vertices:

                md3_frame_vertex.write(file, file_ofs)

                file_ofs = file_ofs + MD3FrameVertex.format_size


class MD3FrameTag:
    """A tag in a specific frame.

    Attributes:

        name (bytes): name of tag, ASCII encoded, null-terminated, length 64.
        location (tuple): location coordinates in this frame as tuple of
            floats.
        orientation (tuple): orientation as rotation matrix in frame as tuple
            of floats. Each sequence of 3 floats make up the coordinates of a
            basis vector. The first 3 floats make up the x basis vector, etc.

    File encodings:

        name: 64*ASCII (C-String).
        location: 3*F32, IEEE-754.
        orientation: 9*F32, IEEE-754.

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

    format = '<64s12f'
    format_size = struct.calcsize(format)
    name_len = 64

    def __init__(self, name, location, orientation):

        self.name = name
        self.location = location
        self.orientation = orientation

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MD3FrameTag object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_frame_tag (MD3FrameTag): MD3FrameTag object.
        """

        file.seek(file_ofs)

        name, \
            location_x, location_y, location_z, \
            orientation_x1, orientation_x2, orientation_x3, \
            orientation_y1, orientation_y2, orientation_y3, \
            orientation_z1, orientation_z2, orientation_z3 \
            = struct.unpack(MD3FrameTag.format,
                            file.read(MD3FrameTag.format_size))

        location = (location_x, location_y, location_z)
        orientation = (orientation_x1, orientation_x2, orientation_x3,
                       orientation_y1, orientation_y2, orientation_y3,
                       orientation_z1, orientation_z2, orientation_z3)

        md3_frame_tag = MD3FrameTag(name, location, orientation)

        return md3_frame_tag

    def write(self, file, file_ofs):
        """Writes MD3FrameTag object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3FrameTag.format,
                               self.name, self.location[0], self.location[1],
                               self.location[2], self.orientation[0],
                               self.orientation[1], self.orientation[2],
                               self.orientation[3], self.orientation[4],
                               self.orientation[5], self.orientation[6],
                               self.orientation[7], self.orientation[8]))


class MD3FrameInfo:
    """General information about a frame.

    Attributes:

        min_bound (tuple): location coordinates of min corner of minimum
            bounding box as tuple of floats.
        max_bound (tuple): location coordinates of max corner of minimum
            bounding box as tuple of floats.
        local_origin (tuple): TODO.
        radius (float): TODO.
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
    frame_name = "(md3 frame)"
    name_len = 16

    def __init__(self, min_bound, max_bound, local_origin, radius, name):

        self.min_bound = min_bound
        self.max_bound = max_bound
        self.local_origin = local_origin
        self.radius = radius
        self.name = name

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MD3FrameInfo object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_frame_info (MD3FrameInfo): MD3FrameInfo object.
        """

        file.seek(file_ofs)

        min_bound_x, min_bound_y, min_bound_z, \
            max_bound_x, max_bound_y, max_bound_z, \
            local_origin_x, local_origin_y, local_origin_z, \
            radius, \
            name \
            = struct.unpack(MD3FrameInfo.format,
                            file.read(MD3FrameInfo.format_size))

        md3_frame_info \
            = MD3FrameInfo((min_bound_x, min_bound_y, min_bound_z),
                           (max_bound_x, max_bound_y, max_bound_z),
                           (local_origin_x, local_origin_y, local_origin_z),
                           radius,
                           name)

        return md3_frame_info

    def write(self, file, file_ofs):
        """Writes MD3FrameInfo object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3FrameInfo.format,
                               self.min_bound[0], self.min_bound[1],
                               self.min_bound[2], self.max_bound[0],
                               self.max_bound[1], self.max_bound[2],
                               self.local_origin[0], self.local_origin[1],
                               self.local_origin[2], self.radius, self.name))


class MD3Header:
    """General information about MD3 data.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, reads "IDP3".
        version (int): version number, latest known is 15.
        name (bytes): model name, usually its pathname, ASCII encoded,
            null-terminated, length 64.
        flags (int): not used.
        num_frames (int): number of animation frames.
        num_tags (int): number of tags.
        num_surfaces (int): number of surfaces.
        num_skins (int): not used.
        ofs_frame_infos (int): file offset to field of frame infos.
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
        ofs_tags: UINT32.
        ofs_surfaces: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4sI64s9I'
    format_size = struct.calcsize(format)
    ident = b'IDP3'
    version = 15
    name_len = 64
    flags = 15

    def __init__(self, ident, version, name, flags, num_frames, num_tags,
                 num_surfaces, num_skins, ofs_frame_infos, ofs_tags,
                 ofs_surfaces, ofs_end):

        self.ident = ident
        self.version = version
        self.name = name
        self.flags = flags

        self.num_frames = num_frames
        self.num_tags = num_tags
        self.num_surfaces = num_surfaces
        self.num_skins = num_skins

        self.ofs_frame_infos = ofs_frame_infos
        self.ofs_tags = ofs_tags
        self.ofs_surfaces = ofs_surfaces
        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MD3Header object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            md3_header (MD3Header): MD3Header object.
        """

        file.seek(file_ofs)

        ident, version, name, flags, num_frames, num_tags, num_surfaces, \
            num_skins, ofs_frame_infos, ofs_tags, ofs_surfaces, ofs_end \
            = struct.unpack(MD3Header.format,
                            file.read(MD3Header.format_size))

        md3_header = MD3Header(ident, version, name, flags, num_frames,
                               num_tags, num_surfaces, num_skins,
                               ofs_frame_infos, ofs_tags, ofs_surfaces,
                               ofs_end)

        return md3_header

    def write(self, file, file_ofs):
        """Writes MD3Header object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MD3Header.format, self.ident, self.version,
                               self.name, self.flags, self.num_frames,
                               self.num_tags, self.num_surfaces,
                               self.num_skins, self.ofs_frame_infos,
                               self.ofs_tags, self.ofs_surfaces, self.ofs_end))


class MD3:
    """Holds references to all MD3 data.

    Attributes:

        header (MD3Header): reference to MD3Header object.
        frame_infos (list): list of MD3FrameInfo objects, size=num_frames.
        tags (list): list of list objects, size=num_frames. Each nested list
            contains MD3FrameTag objects, size=num_tags. Access like this:
            tags[num_frame][num_tag].
        surfaces (list): list of MD3Surface objects, size=num_surfaces.
    """

    max_lods = 4
    max_frames = 1024
    max_tags = 16
    max_surfaces = 32

    max_triangles = 8192  # per surface
    max_shaders = 256  # per surface
    max_vertices = 4096  # per surface
    max_shader_vertices = 1025  # per surface

    def __init__(self):

        self.header = None
        self.frame_infos = []
        self.tags = []
        self.surfaces = []

    @staticmethod
    def read(file_path):
        """Reads a binary encoded MD3 file into an MD3 object.

        Args:

            file_path (str): path to MD3 file.

        Returns:

            md3 (MD3): MD3 object.
        """

        with open(file_path, 'rb') as file:

            md3 = MD3()

            # md3.header
            file_ofs = 0
            md3.header = MD3Header.read(file, file_ofs)

            # md3.frame_infos
            file_ofs = md3.header.ofs_frame_infos
            for i in range(0, md3.header.num_frames):

                md3_frame_info = MD3FrameInfo.read(file, file_ofs)
                md3.frame_infos.append(md3_frame_info)

                file_ofs = file_ofs + MD3FrameInfo.format_size

            # md3.tags
            file_ofs = md3.header.ofs_tags
            for i in range(0, md3.header.num_frames):

                md3_frame_tags = []

                for j in range(0, md3.header.num_tags):

                    md3_frame_tag = MD3FrameTag.read(file, file_ofs)
                    md3_frame_tags.append(md3_frame_tag)

                    file_ofs = file_ofs + MD3FrameTag.format_size

                md3.tags.append(md3_frame_tags)

            # md3.surfaces
            file_ofs = md3.header.ofs_surfaces
            for i in range(0, md3.header.num_surfaces):

                md3_surface = MD3Surface.read(file, file_ofs)
                md3.surfaces.append(md3_surface)

                file_ofs = file_ofs + md3_surface.header.ofs_end

            return md3

    def write(self, file_path):
        """Writes MD3 object to file with binary encoding.

        Args:

            file_path (str): path to MD3 file.
        """

        with open(file_path, 'wb') as file:

            # md3.header
            file_ofs = 0
            self.header.write(file, file_ofs)

            # md3.frame_infos
            file_ofs = self.header.ofs_frame_infos
            for md3_frame_info in self.frame_infos:

                md3_frame_info.write(file, file_ofs)

                file_ofs = file_ofs + MD3FrameInfo.format_size

            # md3.tags
            file_ofs = self.header.ofs_tags
            for md3_frame_tags in self.tags:

                for md3_frame_tag in md3_frame_tags:

                    md3_frame_tag.write(file, file_ofs)

                    file_ofs = file_ofs + MD3FrameTag.format_size

            # md3.surfaces
            file_ofs = self.header.ofs_surfaces
            for md3_surface in self.surfaces:

                md3_surface.write(file, file_ofs)

                file_ofs = file_ofs + md3_surface.header.ofs_end
