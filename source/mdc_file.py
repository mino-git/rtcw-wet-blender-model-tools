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

"""File backend for MDC file format. MDC contains mesh data and tags. Animation
is done by deforming all vertices per frame. The file format is a compressed
version of the MD3 file format.
"""

import struct


class MDCCompFrameIndices:

    """For each frame gives an index into the list of compressed frame vertices
    (verticesComp = []). If the frame is a base frame the index will be set to
    -1.
    """

    format = '<h' # numFrames
    formatSize = struct.calcsize(format)

    def __init__(self, indices):

        self.indices = indices

    def read(file, fileOfs, numFrames):

        indices = []

        file.seek(fileOfs)

        for i in range(0, numFrames):

            index = struct.unpack(MDCCompFrameIndices.format, \
                file.read(MDCCompFrameIndices.formatSize))
            indices.append(index[0])

        mdcCompFrameIndices = MDCCompFrameIndices(indices)

        return mdcCompFrameIndices

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        for i in range(0, len(self.indices)):

            file.write(struct.pack(MDCCompFrameIndices.format, self.indices[i]))


class MDCBaseFrameIndices:

    """For each frame gives an index into the list of base frame vertices
    (verticesBase = []).
    """

    format = '<h' # numFrames
    formatSize = struct.calcsize(format)

    def __init__(self, indices):

        self.indices = indices

    def read(file, fileOfs, numFrames):

        indices = []

        file.seek(fileOfs)

        for i in range(0, numFrames):

            index = struct.unpack(MDCBaseFrameIndices.format, \
                file.read(MDCBaseFrameIndices.formatSize))
            indices.append(index[0])

        mdcBaseFrameIndices = MDCBaseFrameIndices(indices)

        return mdcBaseFrameIndices

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        for i in range(0, len(self.indices)):

            file.write(struct.pack(MDCBaseFrameIndices.format, self.indices[i]))


class MDCVertexComp:

    """Defines compressed frame vertex and vertex normal. The compressed
    frames vertices take a base frame as a reference and store all their
    coordinates as an offset to their corresponding base vertex. This makes it
    possible to compress 16-Bit coordinate values into 8-Bit offset values.
    """

    format = '<BBBB'
    formatSize = struct.calcsize(format)

    maxOfs = 127.0
    scale = 1.0 / 20
    maxDist = maxOfs * scale # 6,35
    maxCompressionDelta = 0.1

    def __init__(self, offsetLocation, normal):

        self.offsetLocation = offsetLocation
        self.normal = normal

    def read(file, fileOfs):

        file.seek(fileOfs)

        offsetLocationX, offsetLocationY, offsetLocationZ, normal \
        = struct.unpack(MDCVertexComp.format, \
            file.read(MDCVertexComp.formatSize))

        mdcVertexComp = MDCVertexComp((offsetLocationX, offsetLocationY, \
            offsetLocationZ), normal)

        return mdcVertexComp

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCVertexComp.format, \
            self.offsetLocation[0], self.offsetLocation[1], \
            self.offsetLocation[2], self.normal))


class MDCVertexBase:

    """Defines a base frame vertex and vertex normal.
    """

    format = '<hhhH'
    formatSize = struct.calcsize(format)
    maxVertices = 4096

    def __init__(self, location, normal):

        self.location = location
        self.normal = normal

    def read(file, fileOfs):

        file.seek(fileOfs)

        locationX, locationY, locationZ, normal \
        = struct.unpack(MDCVertexBase.format, \
            file.read(MDCVertexBase.formatSize))

        mdcVertexBase = MDCVertexBase((locationX, locationY, locationZ), normal)

        return mdcVertexBase

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCVertexBase.format, self.location[0], \
            self.location[1], self.location[2], self.normal))


class MDCTexCoords:

    """Defines a texture coordinate into the UV-Map for a vertex. Indices are
    implicit into the list of vertices.
    """

    format = '<ff'
    formatSize = struct.calcsize(format)

    def __init__(self, texCoords):

        self.texCoords = texCoords

    def read(file, fileOfs):

        file.seek(fileOfs)

        texCoordU, texCoordV = struct.unpack(MDCTexCoords.format, \
            file.read(MDCTexCoords.formatSize))

        mdcTexCoords = MDCTexCoords((texCoordU, texCoordV))

        return mdcTexCoords

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCTexCoords.format, self.texCoords[0], \
            self.texCoords[1]))


class MDCShader:

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

        name, shaderIndex = struct.unpack(MDCShader.format, \
            file.read(MDCShader.formatSize))

        mdcShader = MDCShader(name, shaderIndex)

        return mdcShader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCShader.format, self.name, self.shaderIndex))


class MDCTriangle:

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

        indices = struct.unpack(MDCTriangle.format, \
            file.read(MDCTriangle.formatSize))

        mdcTriangle = MDCTriangle(indices)

        return mdcTriangle

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCTriangle.format, self.indices[0], \
            self.indices[1], self.indices[2]))


class MDCSurfaceHeader:

    """General information about this surface.
    """

    format = '<4s64siiiiiiiiiiiiii'
    formatSize = struct.calcsize(format)
    ident = b'\x07\x00\x00\x00'
    nameLen = 64

    def __init__(self, ident, name, flags, numCompFrames, numBaseFrames, \
        numShaders, numVertices, numTriangles, ofsTriangles, ofsShaders, \
        ofsTexCoords, ofsVerticesBase, ofsVerticesComp, ofsBaseFrameIndices, \
        ofsCompFrameIndices, ofsEnd):

        self.ident = ident
        self.name = name
        self.flags = flags
        self.numCompFrames = numCompFrames
        self.numBaseFrames = numBaseFrames
        self.numShaders = numShaders
        self.numVertices = numVertices
        self.numTriangles = numTriangles
        self.ofsTriangles = ofsTriangles
        self.ofsShaders = ofsShaders
        self.ofsTexCoords = ofsTexCoords
        self.ofsVerticesBase = ofsVerticesBase
        self.ofsVerticesComp = ofsVerticesComp
        self.ofsBaseFrameIndices = ofsBaseFrameIndices
        self.ofsCompFrameIndices = ofsCompFrameIndices
        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, name, flags, numCompFrames, numBaseFrames, numShaders, \
        numVertices, numTriangles, ofsTriangles, ofsShaders, ofsTexCoords, \
        ofsVerticesBase, ofsVerticesComp, ofsBaseFrameIndices, \
        ofsCompFrameIndices, ofsEnd \
        = struct.unpack(MDCSurfaceHeader.format, \
            file.read(MDCSurfaceHeader.formatSize))

        mdcSurfaceHeader = MDCSurfaceHeader(ident, name, flags, numCompFrames, \
            numBaseFrames, numShaders, numVertices, numTriangles, \
            ofsTriangles, ofsShaders, ofsTexCoords, ofsVerticesBase, \
            ofsVerticesComp, ofsBaseFrameIndices, ofsCompFrameIndices, ofsEnd)

        return mdcSurfaceHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCSurfaceHeader.format, self.ident, self.name, \
            self.flags, self.numCompFrames, self.numBaseFrames, \
            self.numShaders, self.numVertices, self.numTriangles, \
            self.ofsTriangles, self.ofsShaders, self.ofsTexCoords, \
            self.ofsVerticesBase, self.ofsVerticesComp, \
            self.ofsBaseFrameIndices, self.ofsCompFrameIndices, self.ofsEnd))


class MDCSurface:

    """Represents a surface. A surface is defined as a polygon mesh (triangle
    mesh). Each vertex is animated per frame (vertex deform). The animation
    frames are divided into base frames and compressed frames.
    """

    maxSurfaces = 32

    def __init__(self):

        self.header = {}       # MDCSurfaceHeader
        self.triangles = []    # MDCTriangle (numTriangles)
        self.shaders = []      # MDCShader (numShaders)
        self.texCoords = []    # MDCTexCoords (numVertices)
        self.verticesBase = [] # MDCVertexBase (numBaseFrames*numVertices)
        self.verticesComp = [] # MDCVertexComp (numCompFrames*numVertices)
        self.baseFrameIndices = None
        self.compFrameIndices = None

    def read(file, fileOfs):

        mdcSurface = MDCSurface()

        mdcSurfaceOfs = fileOfs

        # header
        mdcSurface.header = MDCSurfaceHeader.read(file, fileOfs)

        # triangles
        fileOfs = mdcSurfaceOfs + mdcSurface.header.ofsTriangles
        for i in range(0, mdcSurface.header.numTriangles):

            mdcTriangle = MDCTriangle.read(file, fileOfs)
            mdcSurface.triangles.append(mdcTriangle)

            fileOfs = fileOfs + MDCTriangle.formatSize

        # shaders
        fileOfs = mdcSurfaceOfs + mdcSurface.header.ofsShaders
        for i in range(0, mdcSurface.header.numShaders):

            mdcShader = MDCShader.read(file, fileOfs)
            mdcSurface.shaders.append(mdcShader)

            fileOfs = fileOfs + MDCShader.formatSize

        # texCoords
        fileOfs = mdcSurfaceOfs + mdcSurface.header.ofsTexCoords
        for i in range(0, mdcSurface.header.numVertices):

            mdcTexCoords = MDCTexCoords.read(file, fileOfs)
            mdcSurface.texCoords.append(mdcTexCoords)

            fileOfs = fileOfs + MDCTexCoords.formatSize

        # verticesBase
        fileOfs = mdcSurfaceOfs + mdcSurface.header.ofsVerticesBase
        for i in range(0, mdcSurface.header.numBaseFrames):

            frameVerticesBase = []

            for j in range(0, mdcSurface.header.numVertices):

                mdcVertexBase = MDCVertexBase.read(file, fileOfs)
                frameVerticesBase.append(mdcVertexBase)

                fileOfs = fileOfs + MDCVertexBase.formatSize

            mdcSurface.verticesBase.append(frameVerticesBase)

        # verticesComp
        fileOfs = mdcSurfaceOfs + mdcSurface.header.ofsVerticesComp
        for i in range(0, mdcSurface.header.numCompFrames):

            frameVerticesComp = []

            for j in range(0, mdcSurface.header.numVertices):

                mdcVertexComp = MDCVertexComp.read(file, fileOfs)
                frameVerticesComp.append(mdcVertexComp)

                fileOfs = fileOfs + MDCVertexComp.formatSize

            mdcSurface.verticesComp.append(frameVerticesComp)

        # baseFrameIndices
        fileOfs = mdcSurfaceOfs + mdcSurface.header.ofsBaseFrameIndices
        numFrames = mdcSurface.header.numBaseFrames \
            + mdcSurface.header.numCompFrames
        mdcSurface.baseFrameIndices = MDCBaseFrameIndices.read(file, fileOfs, \
            numFrames)

        # compFrameIndices
        fileOfs = mdcSurfaceOfs + mdcSurface.header.ofsCompFrameIndices
        numFrames = mdcSurface.header.numBaseFrames \
            + mdcSurface.header.numCompFrames
        mdcSurface.compFrameIndices = MDCCompFrameIndices.read(file, fileOfs, \
            numFrames)

        return mdcSurface

    def write(self, file, fileOfs):

        mdcSurfaceOfs = fileOfs

        # header
        self.header.write(file, fileOfs)

        # triangles
        fileOfs = mdcSurfaceOfs + self.header.ofsTriangles
        for triangle in self.triangles:

            triangle.write(file, fileOfs)

            fileOfs = fileOfs + MDCTriangle.formatSize

        # shaders
        fileOfs = mdcSurfaceOfs + self.header.ofsShaders
        for shader in self.shaders:

            shader.write(file, fileOfs)

            fileOfs = fileOfs + MDCShader.formatSize

        # texCoords
        fileOfs = mdcSurfaceOfs + self.header.ofsTexCoords
        for texCoords in self.texCoords:

            texCoords.write(file, fileOfs)

            fileOfs = fileOfs + MDCTexCoords.formatSize

        # verticesBase
        fileOfs = mdcSurfaceOfs + self.header.ofsVerticesBase
        for frameVerticesBase in self.verticesBase:

            for vertexBase in frameVerticesBase:

                vertexBase.write(file, fileOfs)

                fileOfs = fileOfs + MDCVertexBase.formatSize

        # verticesComp
        fileOfs = mdcSurfaceOfs + self.header.ofsVerticesComp
        for frameVerticesComp in self.verticesComp:

            for vertexComp in frameVerticesComp:

                vertexComp.write(file, fileOfs)

                fileOfs = fileOfs + MDCVertexComp.formatSize

        # baseFrameIndices
        fileOfs = mdcSurfaceOfs + self.header.ofsBaseFrameIndices
        self.baseFrameIndices.write(file, fileOfs)

        # compFrameIndices
        fileOfs = mdcSurfaceOfs + self.header.ofsCompFrameIndices
        self.compFrameIndices.write(file, fileOfs)


class MDCTag:

    """Tags are used to attach external models (.md3, .mdc) to this model
    during runtime. They are a coordinate system (location and orientation).
    Once attached, the external model aligns itself with the tag location and
    orientation. MDC tags are animated by recording location and orientation per
    frame. Attachment is sometimes configurable via script files, but often also
    hard coded in compilation.
    """

    format = '<hhhhhh'
    formatSize = struct.calcsize(format)
    maxTags = 16
    angleScale = 360.0 / 32700.0

    def __init__(self, location, angles):

        self.location = location
        self.angles = angles # pitch, yaw, roll

    def read(file, fileOfs):

        file.seek(fileOfs)

        locationX, locationY, locationZ, anglePitch, angleYaw, angleRoll \
        = struct.unpack(MDCTag.format, file.read(MDCTag.formatSize))

        mdcTag = MDCTag((locationX, locationY, locationZ), (anglePitch, \
            angleYaw, angleRoll))

        return mdcTag

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCTag.format, self.location[0], \
            self.location[1], self.location[2], self.angles[0], \
            self.angles[1], self.angles[2]))


class MDCTagHeader:

    """General information about a tag.
    """

    format = '<64s'
    formatSize = struct.calcsize(format)

    def __init__(self, name):

        self.name = name

    def read(file, fileOfs):

        file.seek(fileOfs)

        name = struct.unpack(MDCTagHeader.format, \
            file.read(MDCTagHeader.formatSize))

        mdcTagHeader = MDCTagHeader(name[0])

        return mdcTagHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCTagHeader.format, self.name))


class MDCFrameHeader:

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
        = struct.unpack(MDCFrameHeader.format, \
            file.read(MDCFrameHeader.formatSize))

        mdcFrameHeader = MDCFrameHeader((minBoundsX, minBoundsY, minBoundsZ), \
            (maxBoundsX, maxBoundsY, maxBoundsZ), \
            (localOriginX, localOriginY, localOriginZ), \
            radius, \
            name)

        return mdcFrameHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCFrameHeader.format, \
            self.minBounds[0], self.minBounds[1], self.minBounds[2], \
            self.maxBounds[0], self.maxBounds[1], self.maxBounds[2], \
            self.localOrigin[0], self.localOrigin[1], self.localOrigin[2], \
            self.radius, \
            self.name))


class MDCFileHeader:

    """General information about this file.
    """

    format = '<4si64siiiiiiiiii'
    formatSize = struct.calcsize(format)
    ident = b'IDPC'
    version = 2
    nameLen = 64

    def __init__(self, ident, version, name, flags, numFrames, numTags, \
        numSurfaces, numSkins, ofsFrameHeaders, ofsTagHeaders, ofsTags, \
        ofsSurfaces, ofsEnd):

        self.ident = ident
        self.version = version
        self.name = name
        self.flags = flags

        self.numFrames = numFrames
        self.numTags = numTags
        self.numSurfaces = numSurfaces
        self.numSkins = numSkins

        self.ofsFrameHeaders = ofsFrameHeaders
        self.ofsTagHeaders = ofsTagHeaders
        self.ofsTags = ofsTags
        self.ofsSurfaces = ofsSurfaces
        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, version, name, flags, numFrames, numTags, numSurfaces, \
        numSkins, ofsFrameHeaders, ofsTagHeaders, ofsTags, ofsSurfaces, ofsEnd \
        = struct.unpack(MDCFileHeader.format, \
            file.read(MDCFileHeader.formatSize))

        mdcFileHeader = MDCFileHeader(ident, version, name, flags, numFrames, \
            numTags, numSurfaces, numSkins, ofsFrameHeaders, ofsTagHeaders, \
            ofsTags, ofsSurfaces, ofsEnd)

        return mdcFileHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDCFileHeader.format, self.ident, self.version, \
            self.name, self.flags, self.numFrames, self.numTags, \
            self.numSurfaces, self.numSkins, self.ofsFrameHeaders, \
            self.ofsTagHeaders, self.ofsTags, self.ofsSurfaces, self.ofsEnd))


class MDCFile:

    """Holds references to all MDC file data. Provides public file read and
    write functions.
    """

    def __init__(self):

        self.header = {}        # MDCFileHeader
        self.frameHeaders = []  # MDCFrameHeader (numFrames)
        self.tagHeaders = []    # MDCTagHeader (numTags)
        self.tags = []          # MDCTag (numFrames*numTags)
        self.surfaces = []      # MDCSurface (numSurfaces)

    def read(filepath):
        with open(filepath, 'rb') as file:

            """Reads MDC file to MDCFile object.
            """

            mdcFile = MDCFile()

            # header
            fileOfs = 0
            mdcFile.header = MDCFileHeader.read(file, fileOfs)

            # frameHeaders
            fileOfs = mdcFile.header.ofsFrameHeaders
            for i in range(0, mdcFile.header.numFrames):

                mdcFrameHeader = MDCFrameHeader.read(file, fileOfs)
                mdcFile.frameHeaders.append(mdcFrameHeader)

                fileOfs = fileOfs + MDCFrameHeader.formatSize

            # tagHeaders
            fileOfs = mdcFile.header.ofsTagHeaders
            for i in range(0, mdcFile.header.numTags):

                mdcTagHeader = MDCTagHeader.read(file, fileOfs)
                mdcFile.tagHeaders.append(mdcTagHeader)

                fileOfs = fileOfs + MDCTagHeader.formatSize

            # tags
            fileOfs = mdcFile.header.ofsTags
            for i in range(0, mdcFile.header.numFrames):

                frameTags = []

                for j in range(0, mdcFile.header.numTags):

                    mdcTag = MDCTag.read(file, fileOfs)
                    frameTags.append(mdcTag)

                    fileOfs = fileOfs + MDCTag.formatSize

                mdcFile.tags.append(frameTags)

            # surfaces
            fileOfs = mdcFile.header.ofsSurfaces
            for i in range(0, mdcFile.header.numSurfaces):

                mdcSurface = MDCSurface.read(file, fileOfs)
                mdcFile.surfaces.append(mdcSurface)

                fileOfs = fileOfs + mdcSurface.header.ofsEnd

            return mdcFile

    def write(self, filepath):
        with open(filepath, 'wb') as file:

            """Writes MDCFile object to MDC file.
            """

            # header
            fileOfs = 0
            self.header.write(file, fileOfs)

            # frameHeaders
            fileOfs = self.header.ofsFrameHeaders
            for frameHeader in self.frameHeaders:

                frameHeader.write(file, fileOfs)

                fileOfs = fileOfs + MDCFrameHeader.formatSize

            # tagHeaders
            fileOfs = mdcFile.header.ofsTagHeaders
            for tagHeader in self.tagHeaders:

                tagHeader.write(file, fileOfs)

                fileOfs = fileOfs + MDCTagHeader.formatSize

            # tags
            fileOfs = mdcFile.header.ofsTags
            for frameTags in self.tags:

                for j in range(0, mdcFile.header.numTags):

                    tag = frameTags[j]
                    tag.write(file, fileOfs)

                    fileOfs = fileOfs + MDCTag.formatSize

            # surfaces
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

    mdcFilepathIn = dir + "\\import\\head.mdc"
    mdcFilepathOut = dir + "\\export\\head.mdc"

    xmlMdcFilepathOut = dir + "\\export\\head.mdc.xml"

    return (mdcFilepathIn, mdcFilepathOut, xmlMdcFilepathOut)

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

mdcFilepathIn, mdcFilepathOut, \
xmlMdcFilepathOut, \
= settings()

mdcFile = MDCFile.read(mdcFilepathIn)
mdcFile.write(mdcFilepathOut)

XMLWriter.writeMDC(mdcFile, xmlMdcFilepathOut)
#XMLWriter.writeMDC(mdcFile, xmlMdcFilepathOut, (0, 3))

print("SUCCESS")
