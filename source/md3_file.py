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

"""File backend for MD3 file format. MD3 contains mesh data and tags. Animation
is done by deforming all vertices per frame.
"""

import struct


class MD3Vertex:

    """Defines a vertex and vertex normal.
    """

    format = '<hhhh'
    formatSize = struct.calcsize(format)
    maxVertices = 4096

    def __init__(self, location, normal):

        self.location = location
        self.normal = normal

    def read(file, fileOfs):

        file.seek(fileOfs)

        locationX, locationY, locationZ, normal \
        = struct.unpack(MD3Vertex.format, file.read(MD3Vertex.formatSize))

        md3Vertex = MD3Vertex((locationX, locationY, locationZ), normal)

        return md3Vertex

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3Vertex.format, self.location[0], \
            self.location[1], self.location[2], self.normal))


class MD3TexCoords:

    """Defines a texture coordinate into the UV-Map for a vertex. Indices are
    implicit into the list of vertices.
    """

    format = '<ff'
    formatSize = struct.calcsize(format)

    def __init__(self, texCoords):

        self.texCoords = texCoords

    def read(file, fileOfs):

        file.seek(fileOfs)

        texCoordU, texCoordV = struct.unpack(MD3TexCoords.format, \
            file.read(MD3TexCoords.formatSize))

        md3TexCoords = MD3TexCoords((texCoordU, texCoordV))

        return md3TexCoords

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3TexCoords.format, self.texCoords[0], \
            self.texCoords[1]))


class MD3Shader:

    """Defines a shader for this surface.
    """

    format = '<64si'
    formatSize = struct.calcsize(format)
    maxShaders = 256

    def __init__(self, name, shaderIndex):

        self.name = name
        self.shaderIndex = shaderIndex

    def read(file, fileOfs):

        file.seek(fileOfs)

        name, shaderIndex = struct.unpack(MD3Shader.format, \
            file.read(MD3Shader.formatSize))

        md3Shader = MD3Shader(name, shaderIndex)

        return md3Shader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3Shader.format, self.name, self.shaderIndex))


class MD3Triangle:

    """Defines a face for this surface. Each index value points to the list of
    vertices.
    """

    format = '<iii'
    formatSize = struct.calcsize(format)
    maxTriangles = 8192

    def __init__(self, indices):

        self.indices = indices

    def read(file, fileOfs):

        file.seek(fileOfs)

        indices = struct.unpack(MD3Triangle.format, \
            file.read(MD3Triangle.formatSize))

        md3Triangle = MD3Triangle(indices)

        return md3Triangle

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3Triangle.format, self.indices[0], \
            self.indices[1], self.indices[2]))


class MD3SurfaceHeader:

    """General information about this surface.
    """

    format = '<4s64siiiiiiiiii'
    formatSize = struct.calcsize(format)
    ident = b'\x09\x00\x00\x00' # TODO
    nameLen = 64
    shaderNameLen = 64
    shaderIndex = 0

    def __init__(self, ident, name, flags, numFrames, numShaders, numVertices, \
        numTriangles, ofsTriangles, ofsShaders, ofsTexCoords, ofsVertices, \
        ofsEnd):

        self.ident = ident
        self.name = name
        self.flags = flags

        self.numFrames = numFrames
        self.numShaders = numShaders
        self.numVertices = numVertices
        self.numTriangles = numTriangles

        self.ofsTriangles = ofsTriangles
        self.ofsShaders = ofsShaders
        self.ofsTexCoords = ofsTexCoords
        self.ofsVertices = ofsVertices

        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, name, flags, numFrames, numShaders, numVertices, numTriangles, \
        ofsTriangles, ofsShaders, ofsTexCoords, ofsVertices, ofsEnd \
        = struct.unpack(MD3SurfaceHeader.format, \
            file.read(MD3SurfaceHeader.formatSize))

        md3SurfaceHeader = MD3SurfaceHeader(ident, name, flags, numFrames, \
            numShaders, numVertices, numTriangles, ofsTriangles, ofsShaders, \
            ofsTexCoords, ofsVertices, ofsEnd)

        return md3SurfaceHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3SurfaceHeader.format, self.ident, self.name, \
            self.flags, self.numFrames, self.numShaders, self.numVertices, \
            self.numTriangles, self.ofsTriangles, self.ofsShaders, \
            self.ofsTexCoords, self.ofsVertices, self.ofsEnd))


class MD3Surface:

    """Represents a surface. A surface is defined as a polygon mesh (triangle
    mesh). Each vertex is animated per frame (vertex deform).
    """

    maxSurfaces = 32

    def __init__(self):

        self.header = {}         # MD3SurfaceHeader
        self.triangles = []      # MD3Triangle (numTriangles)
        self.shaders = []        # MD3Shader (numShaders)
        self.texCoords = []      # MD3TexCoords (numVertices)
        self.vertices = []       # MD3Vertex (numFrames*numVertices)

    def read(file, fileOfs):

        md3Surface = MD3Surface()

        md3SurfaceOfs = fileOfs

        # md3Surface.header
        md3Surface.header = MD3SurfaceHeader.read(file, fileOfs)

        # md3Surface.triangles
        fileOfs = md3SurfaceOfs + md3Surface.header.ofsTriangles

        for i in range(0, md3Surface.header.numTriangles):

            md3Triangle = MD3Triangle.read(file, fileOfs)
            md3Surface.triangles.append(md3Triangle)

            fileOfs = fileOfs + MD3Triangle.formatSize

        # md3Surface.shaders
        fileOfs = md3SurfaceOfs + md3Surface.header.ofsShaders

        for i in range(0, md3Surface.header.numShaders):

            md3Shader = MD3Shader.read(file, fileOfs)
            md3Surface.shaders.append(md3Shader)

            fileOfs = fileOfs + MD3Shader.formatSize

        # md3Surface.texCoords
        fileOfs = md3SurfaceOfs + md3Surface.header.ofsTexCoords

        for i in range(0, md3Surface.header.numVertices):

            md3TexCoords = MD3TexCoords.read(file, fileOfs)
            md3Surface.texCoords.append(md3TexCoords)

            fileOfs = fileOfs + MD3TexCoords.formatSize

        # md3Surface.vertices
        fileOfs = md3SurfaceOfs + md3Surface.header.ofsVertices
        for i in range(0, md3Surface.header.numFrames):

            vertices = []

            for j in range(0, md3Surface.header.numVertices):

                md3Vertex = MD3Vertex.read(file, fileOfs)
                vertices.append(md3Vertex)

                fileOfs = fileOfs + MD3Vertex.formatSize

            md3Surface.vertices.append(vertices)

        return md3Surface

    def write(self, file, fileOfs):

        md3SurfaceOfs = fileOfs

        # self.header
        self.header.write(file, fileOfs)

        # self.triangles
        fileOfs = md3SurfaceOfs + self.header.ofsTriangles

        for triangle in self.triangles:

            triangle.write(file, fileOfs)

            fileOfs = fileOfs + MD3Triangle.formatSize

        # self.shaders
        fileOfs = md3SurfaceOfs + self.header.ofsShaders

        for shader in self.shaders:

            shader.write(file, fileOfs)

            fileOfs = fileOfs + MD3Shader.formatSize

        # self.texCoords
        fileOfs = md3SurfaceOfs + self.header.ofsTexCoords

        for texCoords in self.texCoords:

            texCoords.write(file, fileOfs)

            fileOfs = fileOfs + MD3TexCoords.formatSize

        # self.vertices
        fileOfs = md3SurfaceOfs + self.header.ofsVertices

        for vertices in self.vertices:

            for vertex in vertices:

                vertex.write(file, fileOfs)

                fileOfs = fileOfs + MD3Vertex.formatSize


class MD3Tag:

    """Tags are used to attach external models (.md3, .mdc) to this model
    during runtime. They are a coordinate system (location and orientation).
    Once attached, the external model aligns itself with the tag location and
    orientation. MD3 tags are animated by recording location and orientation per
    frame. Attachment is sometimes configurable via script files, but often also
    hard coded in compilation.
    """

    format = '<64s3f9f'
    formatSize = struct.calcsize(format)
    maxTags = 16

    def __init__(self, name, location, rotationMatrix):

        self.name = name
        self.location = location
        self.rotationMatrix = rotationMatrix

    def read(file, fileOfs):

        file.seek(fileOfs)

        name, locationX, locationY, locationZ, rmX1, rmX2, rmX3, rmY1, rmY2, \
        rmY3, rmZ1, rmZ2, rmZ3 \
        = struct.unpack(MD3Tag.format, file.read(MD3Tag.formatSize))

        md3Tag = MD3Tag(name, (locationX, locationY, locationZ), ((rmX1, rmX2, \
            rmX3), (rmY1, rmY2, rmY3), (rmZ1, rmZ2, rmZ3)))

        return md3Tag

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3Tag.format, self.name, self.location[0], \
            self.location[1], self.location[2], self.rotationMatrix[0][0], \
            self.rotationMatrix[0][1], self.rotationMatrix[0][2], \
            self.rotationMatrix[1][0], self.rotationMatrix[1][1], \
            self.rotationMatrix[1][2], self.rotationMatrix[2][0], \
            self.rotationMatrix[2][1], self.rotationMatrix[2][2]))


class MD3FrameHeader:

    """General information about a frame.
    """

    format = '<ffffffffff16s'
    formatSize = struct.calcsize(format)

    def __init__(self, minBounds, maxBounds, localOrigin, radius, name):

        self.minBounds = minBounds
        self.maxBounds = maxBounds
        self.localOrigin = localOrigin
        self.radius = radius
        self.name = name

    def read(file, fileOfs):

        file.seek(fileOfs)

        minBoundsX, minBoundsY, minBoundsZ, \
        maxBoundsX, maxBoundsY, maxBoundsZ, \
        localOriginX, localOriginY, localOriginZ, \
        radius, \
        name \
        = struct.unpack(MD3FrameHeader.format, \
            file.read(MD3FrameHeader.formatSize))

        md3FrameHeader = MD3FrameHeader((minBoundsX, minBoundsY, minBoundsZ), \
            (maxBoundsX, maxBoundsY, maxBoundsZ), \
            (localOriginX, localOriginY, localOriginZ), \
            radius, \
            name)

        return md3FrameHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3FrameHeader.format, \
            self.minBounds[0], self.minBounds[1], self.minBounds[2], \
            self.maxBounds[0], self.maxBounds[1], self.maxBounds[2], \
            self.localOrigin[0], self.localOrigin[1], self.localOrigin[2], \
            self.radius, \
            self.name))


class MD3FileHeader:

    """General information about this file.
    """

    format = '<4si64siiiiiiiii'
    formatSize = struct.calcsize(format)
    ident = b'IDP3'
    version = 15
    nameLen = 64

    def __init__(self, ident, version, name, flags, numFrames, numTags, \
        numSurfaces, numSkins, ofsFrameHeaders, ofsTags, ofsSurfaces, ofsEnd):

        self.ident = ident
        self.version = version
        self.name = name
        self.flags = flags

        self.numFrames = numFrames
        self.numTags = numTags
        self.numSurfaces = numSurfaces
        self.numSkins = numSkins

        self.ofsFrameHeaders = ofsFrameHeaders
        self.ofsTags = ofsTags
        self.ofsSurfaces = ofsSurfaces
        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, version, name, flags, numFrames, numTags, numSurfaces, \
        numSkins, ofsFrameHeaders, ofsTags, ofsSurfaces, ofsEnd \
        = struct.unpack(MD3FileHeader.format, \
            file.read(MD3FileHeader.formatSize))

        md3FileHeader = MD3FileHeader(ident, version, name, flags, numFrames, \
            numTags, numSurfaces, numSkins, ofsFrameHeaders, ofsTags, \
            ofsSurfaces, ofsEnd)

        return md3FileHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MD3FileHeader.format, self.ident, self.version, \
            self.name, self.flags, self.numFrames, self.numTags, \
            self.numSurfaces, self.numSkins, self.ofsFrameHeaders, \
            self.ofsTags, self.ofsSurfaces, self.ofsEnd))


class MD3File:

    """Holds references to all MD3 file data. Provides public file read and
    write functions.
    """

    def __init__(self):

        self.header = {}        # MD3FileHeader
        self.frameHeaders = []  # MD3FrameHeader (numFrames)
        self.tags = []          # MD3Tag (numFrames*numTags)
        self.surfaces = []      # MD3Surface (numSurfaces)

    def read(filepath):
        with open(filepath, 'rb') as file:

            """Reads MD3 file to MD3File object.
            """

            md3File = MD3File()

            # md3File.header
            fileOfs = 0
            md3File.header = MD3FileHeader.read(file, fileOfs)

            # md3File.frameHeaders
            fileOfs = md3File.header.ofsFrameHeaders
            for i in range(0, md3File.header.numFrames):

                md3FrameHeader = MD3FrameHeader.read(file, fileOfs)
                md3File.frameHeaders.append(md3FrameHeader)

                fileOfs = fileOfs + MD3FrameHeader.formatSize

            # md3File.tags
            fileOfs = md3File.header.ofsTags
            for i in range(0, md3File.header.numFrames):

                tags = []

                for j in range(0, md3File.header.numTags):

                    md3Tag = MD3Tag.read(file, fileOfs)
                    tags.append(md3Tag)

                    fileOfs = fileOfs + MD3Tag.formatSize

                md3File.tags.append(tags)

            # md3File.surfaces
            fileOfs = md3File.header.ofsSurfaces
            for i in range(0, md3File.header.numSurfaces):

                md3Surface = MD3Surface.read(file, fileOfs)
                md3File.surfaces.append(md3Surface)

                fileOfs = fileOfs + md3Surface.header.ofsEnd

            return md3File

    def write(self, filepath):
        with open(filepath, 'wb') as file:

            """Writes MD3File object to MD3 file.
            """

            # self.header
            fileOfs = 0
            self.header.write(file, fileOfs)

            # self.frameHeaders
            fileOfs = self.header.ofsFrameHeaders
            for frameHeader in self.frameHeaders:

                frameHeader.write(file, fileOfs)

                fileOfs = fileOfs + MD3FrameHeader.formatSize

            # self.tags
            fileOfs = md3File.header.ofsTags
            for tags in self.tags:

                for j in range(0, md3File.header.numTags):

                    tag = tags[j]
                    tag.write(file, fileOfs)

                    fileOfs = fileOfs + MD3Tag.formatSize

            # self.surfaces
            fileOfs = self.header.ofsSurfaces
            for surface in self.surfaces:

                surface.write(file, fileOfs)

                fileOfs = fileOfs + surface.header.ofsEnd


# HELP
# ==============================================================================

import os
import sys
import bpy

def settings():

    md3FilepathIn = dir + "\\import\\head.md3"
    md3FilepathOut = dir + "\\export\\head.md3"

    xmlMd3FilepathOut = dir + "\\export\\head.md3.xml"
    #bindPoseFrame = 32
    #collapseMapFrame = 4274
    bindPoseFrame = 0
    collapseMapFrame = 1

    return (md3FilepathIn, md3FilepathOut, xmlMd3FilepathOut, bindPoseFrame, \
        collapseMapFrame)

def delete_scene(scene):

    scene = bpy.data.scenes[scene]

    for object_ in scene.objects:
        bpy.data.objects.remove(object_, True)

    #bpy.data.scenes.remove(scene, True)

# MAIN
# ==============================================================================

dir = os.path.dirname(bpy.data.filepath)

if not dir in sys.path:
    sys.path.append(dir)

from xml_writer import *

print("=====")

md3FilepathIn, md3FilepathOut, \
xmlMd3FilepathOut, \
bindPoseFrame, collapseMapFrame \
= settings()

md3File = MD3File.read(md3FilepathIn)
md3File.write(md3FilepathOut)

XMLWriter.writeMD3(md3File, xmlMd3FilepathOut, (0, 3))

print("SUCCESS")
