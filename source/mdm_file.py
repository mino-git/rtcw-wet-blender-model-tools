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

"""File backend for MDM file format. MDM contains mesh and tag data and
references animation data from MDX.
"""

import struct


class MDMTag:

    """Tags are used to specify which models (.md3, .mdc) the game code has to
    attach to the player model. They are a coordinate system (location and
    orientation). The attached models origin and orientation gets aligned with
    the origin and orientation of the tag. Animation is done in relation to a
    parent bone, which is defined in MDX.
    """

    format = '<64sfffffffffifffiii'
    formatSize = struct.calcsize(format)
    maxTags = 128
    nameLen = 64

    def __init__(self, name, rotationMatrix, parentBoneIndex, offsetLocation, \
        numBoneRefs, ofsBoneRefs, ofsEnd):

        self.name = name
        self.rotationMatrix = rotationMatrix
        self.parentBoneIndex = parentBoneIndex
        self.offsetLocation = offsetLocation
        self.numBoneRefs = numBoneRefs
        self.ofsBoneRefs = ofsBoneRefs
        self.ofsEnd = ofsEnd

        self.boneRefs = None

    def read(file, fileOfs):

        file.seek(fileOfs)

        name, rmX1, rmX2, rmX3, rmY1, rmY2, rmY3, rmZ1, rmZ2, rmZ3, \
        parentBoneIndex, offX, offY, offZ, numBoneRefs, ofsBoneRefs, ofsEnd \
        = struct.unpack(MDMTag.format, file.read(MDMTag.formatSize))

        rotationMatrix = ((rmX1, rmX2, rmX3), \
                          (rmY1, rmY2, rmY3), \
                          (rmZ1, rmZ2, rmZ3))

        offsetLocation = (offX, offY, offZ)

        mdmTag = MDMTag(name, rotationMatrix, parentBoneIndex, offsetLocation, \
            numBoneRefs, ofsBoneRefs, ofsEnd)

        # mdmTag.boneRefs
        fileOfs = fileOfs + mdmTag.ofsBoneRefs

        mdmTag.boneRefs = MDMBoneRefs.read(file, fileOfs, mdmTag.numBoneRefs)

        return mdmTag

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDMTag.format, self.name,
            self.rotationMatrix[0][0], self.rotationMatrix[0][1], \
            self.rotationMatrix[0][2], self.rotationMatrix[1][0], \
            self.rotationMatrix[1][1], self.rotationMatrix[1][2], \
            self.rotationMatrix[2][0], self.rotationMatrix[2][1], \
            self.rotationMatrix[2][2], self.parentBoneIndex, \
            self.offsetLocation[0], self.offsetLocation[1], \
            self.offsetLocation[2], self.numBoneRefs, self.ofsBoneRefs, \
            self.ofsEnd))

        # self.boneRefs
        fileOfs = fileOfs + self.ofsBoneRefs

        self.boneRefs.write(file, fileOfs)


class MDMBoneRefs:

    """Defines which bones a tag or surface references. Is used for optimization
    inside the engine. Needs to be hierarchically ordered.
    """

    format = '<i' # numBoneRefs
    formatSize = struct.calcsize(format)

    def __init__(self, boneRefs):

        self.boneRefs = boneRefs

    def read(file, fileOfs, numBoneRefs):

        boneRefs = []

        file.seek(fileOfs)

        for i in range(0, numBoneRefs):

            boneRef = struct.unpack(MDMBoneRefs.format, \
                file.read(MDMBoneRefs.formatSize))
            boneRefs.append(boneRef[0])

        mdmBoneRefs = MDMBoneRefs(boneRefs)

        return mdmBoneRefs

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        for i in range(0, len(self.boneRefs)):

            file.write(struct.pack(MDMBoneRefs.format, self.boneRefs[i]))


class MDMCollapseMap:

    """Defines which bones a tag or surface references. Is used for optimization
    inside the engine. Needs to be hierarchically ordered.
    """

    format = '<i' # numVertices
    formatSize = struct.calcsize(format)

    def __init__(self, mappings):

        self.mappings = mappings

    def read(file, fileOfs, numVertices):

        mappings = []

        file.seek(fileOfs)

        for i in range(0, numVertices):

            mapping = struct.unpack(MDMCollapseMap.format, \
                file.read(MDMCollapseMap.formatSize))
            mappings.append(mapping[0])

        mdmCollapseMap = MDMCollapseMap(mappings)

        return mdmCollapseMap

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        for i in range(0, len(self.mappings)):

            file.write(struct.pack(MDMCollapseMap.format, self.mappings[i]))


class MDMTriangle:

    """Defines a face for the triangle mesh. Each index value points to the
    list of vertices.
    """

    format = '<iii'
    formatSize = struct.calcsize(format)
    maxTriangles = 8192

    def __init__(self, indices):

        self.indices = indices

    def read(file, fileOfs):

        file.seek(fileOfs)

        indices = struct.unpack(MDMTriangle.format, \
            file.read(MDMTriangle.formatSize))

        mdmTriangle = MDMTriangle(indices)

        return mdmTriangle

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDMTriangle.format, self.indices[0], \
            self.indices[1], self.indices[2]))


class MDMWeight:

    """Defines a vertex location in conjunction with all other weights of the
    vertex. Multiple bones excersise some influence over the vertexes final
    frame postion. To simulate this, for each bone the offset value is fired
    through the bones frame rotation matrix, then translated by the bones
    location, and then multiplied by its weight. Once done for all referenced
    bones, the values are summed up (see "Skinning" or "Skeletal animation" for
    more details). The sum of all weights should never be unequal to 1.
    """

    format = '<iffff'
    formatSize = struct.calcsize(format)

    minWeight = 0
    maxWeight = 1

    def __init__(self, boneIndex, boneWeight, offsetLocation):

        self.boneIndex = boneIndex
        self.boneWeight = boneWeight
        self.offsetLocation = offsetLocation

    def read(file, fileOfs):

        file.seek(fileOfs)

        boneIndex, boneWeight, offsetX, offsetY, offsetZ \
        = struct.unpack(MDMWeight.format, file.read(MDMWeight.formatSize))

        offsetLocation = (offsetX, offsetY, offsetZ)
        mdmWeight = MDMWeight(boneIndex, boneWeight, offsetLocation)

        return mdmWeight

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDMWeight.format, self.boneIndex, \
            self.boneWeight, self.offsetLocation[0], self.offsetLocation[1], \
            self.offsetLocation[2]))


class MDMVertex:

    """Vertex information. The vertex normal is used for lightning (see Gouraud
    Shading). The texture coordinate is used for the UV Map. The list of weights
    defines the vertexes position in relation to bones.
    """

    format = '<fffffi'
    formatSize = struct.calcsize(format)
    maxVertices = 6000
    maxWeights = 3

    def __init__(self, normal, texCoords, numWeights):

        self.normal = normal
        self.texCoords = texCoords
        self.numWeights = numWeights

        self.weights = []

    def read(file, fileOfs):

        file.seek(fileOfs)

        normalX, normalY, normalZ, texCoordU, texCoordV, numWeights \
        = struct.unpack(MDMVertex.format, file.read(MDMVertex.formatSize))

        mdmVertex = MDMVertex((normalX, normalY, normalZ), \
            (texCoordU, texCoordV), numWeights)

        # mdmVertex.weights
        fileOfs = fileOfs + MDMVertex.formatSize

        for i in range(0, mdmVertex.numWeights):

            mdmWeight = MDMWeight.read(file, fileOfs)
            mdmVertex.weights.append(mdmWeight)

            fileOfs = fileOfs + MDMWeight.formatSize

        return mdmVertex

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDMVertex.format, self.normal[0], \
            self.normal[1], self.normal[2], self.texCoords[0], \
            self.texCoords[1], self.numWeights))

        # self.weights
        fileOfs = fileOfs + MDMVertex.formatSize

        for weight in self.weights:

            weight.write(file, fileOfs)

            fileOfs = fileOfs + MDMWeight.formatSize


class MDMSurfaceHeader:

    """General information about this surface.
    """

    format = '<4s64s64siiiiiiiiiii'
    formatSize = struct.calcsize(format)
    ident = b'\x09\x00\x00\x00'
    nameLen = 64
    shaderNameLen = 64
    shaderIndex = 0

    def __init__(self, ident, name, shader, shaderIndex, minLod, ofsHeader, \
        numVertices, ofsVertices, numTriangles, ofsTriangles, \
        ofsCollapseMap, numBoneRefs, ofsBoneRefs, ofsEnd):

        self.ident = ident
        self.name = name
        self.shader = shader
        self.shaderIndex = shaderIndex

        self.minLod = minLod

        self.ofsHeader = ofsHeader

        self.numVertices = numVertices
        self.ofsVertices = ofsVertices

        self.numTriangles = numTriangles
        self.ofsTriangles = ofsTriangles

        self.ofsCollapseMap = ofsCollapseMap

        self.numBoneRefs = numBoneRefs
        self.ofsBoneRefs = ofsBoneRefs

        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, name, shader, shaderIndex, minLod, ofsHeader, numVertices, \
        ofsVertices, numTriangles, ofsTriangles, ofsCollapseMap, numBoneRefs, \
        ofsBoneRefs, ofsEnd \
        = struct.unpack(MDMSurfaceHeader.format, \
            file.read(MDMSurfaceHeader.formatSize))

        mdmSurfaceHeader = MDMSurfaceHeader(ident, name, shader, shaderIndex, \
            minLod, ofsHeader, numVertices, ofsVertices, numTriangles, \
            ofsTriangles, ofsCollapseMap, numBoneRefs, ofsBoneRefs, ofsEnd)

        return mdmSurfaceHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDMSurfaceHeader.format, self.ident, self.name, \
            self.shader, self.shaderIndex, self.minLod, self.ofsHeader, \
            self.numVertices, self.ofsVertices, self.numTriangles, \
            self.ofsTriangles, self.ofsCollapseMap, self.numBoneRefs, \
            self.ofsBoneRefs, self.ofsEnd))


class MDMSurface:

    """Represents a surface. A surface is defined as a polygon mesh (triangle
    mesh). Because this format uses skeletal animation, each vertex is weighted
    against all of its associated bones (from MDX) in order to get its current
    frame position. The collapse map is used for creating different levels of
    detail (LOD) of the model during runtime (for the particular method used see
    "A Simple, Fast, and Effective Polygon Reduction Algorithm - Stan Melax".
    """

    formatCollapseMap = '<i'
    formatCollapseMapSize = struct.calcsize(formatCollapseMap)

    maxSurfaces = 32

    def __init__(self):

        self.header = {}         # MDMSurfaceHeader
        self.vertices = []       # MDMVertex (numVertices)
        self.triangles = []      # MDMTriangle (numTriangles)
        self.collapseMap = None  # MDMCollapseMap
        self.boneRefs = None     # MDMBoneRefs

    def read(file, fileOfs):

        mdmSurface = MDMSurface()

        mdmSurfaceOfs = fileOfs

        # mdmSurface.header
        mdmSurface.header = MDMSurfaceHeader.read(file, fileOfs)

        # mdmSurface.vertices
        fileOfs = mdmSurfaceOfs + mdmSurface.header.ofsVertices

        for i in range(mdmSurface.header.numVertices):

            mdmVertex = MDMVertex.read(file, fileOfs)
            mdmSurface.vertices.append(mdmVertex)

            fileOfs = fileOfs + MDMVertex.formatSize + \
                      mdmVertex.numWeights * MDMWeight.formatSize

        # mdmSurface.triangles
        fileOfs = mdmSurfaceOfs + mdmSurface.header.ofsTriangles

        for i in range(mdmSurface.header.numTriangles):

            mdmTriangle = MDMTriangle.read(file, fileOfs)
            mdmSurface.triangles.append(mdmTriangle)

            fileOfs = fileOfs + MDMTriangle.formatSize

        # mdmSurface.collapseMap
        fileOfs = mdmSurfaceOfs + mdmSurface.header.ofsCollapseMap

        mdmSurface.collapseMap = MDMCollapseMap.read(file, fileOfs, \
            mdmSurface.header.numVertices)

        # mdmSurface.boneRefs
        fileOfs = mdmSurfaceOfs + mdmSurface.header.ofsBoneRefs

        mdmSurface.boneRefs = MDMBoneRefs.read(file, fileOfs, \
            mdmSurface.header.numBoneRefs)

        return mdmSurface

    def write(self, file, fileOfs):

        mdmSurfaceOfs = fileOfs

        # self.header
        self.header.write(file, fileOfs)

        # self.vertices
        fileOfs = mdmSurfaceOfs + self.header.ofsVertices

        for vertex in self.vertices:

            vertex.write(file, fileOfs)

            fileOfs = fileOfs + MDMVertex.formatSize + \
                      vertex.numWeights * MDMWeight.formatSize

        # self.triangles
        fileOfs = mdmSurfaceOfs + self.header.ofsTriangles

        for triangle in self.triangles:

            triangle.write(file, fileOfs)

            fileOfs = fileOfs + MDMTriangle.formatSize

        # self.collapseMap
        fileOfs = mdmSurfaceOfs + self.header.ofsCollapseMap

        self.collapseMap.write(file, fileOfs)

        # self.boneRefs
        fileOfs = mdmSurfaceOfs + self.header.ofsBoneRefs

        self.boneRefs.write(file, fileOfs)


class MDMFileHeader:

    """General information about this file.
    """

    format = '<4si64sffiiiii'
    formatSize = struct.calcsize(format)
    ident = b'MDMW'
    version = 3
    nameLen = 64

    def __init__(self, ident, version, name, lodScale, lodBias, numSurfaces, \
        ofsSurfaces, numTags, ofsTags, ofsEnd):

        self.ident = ident
        self.version = version
        self.name = name

        self.lodScale = lodScale
        self.lodBias = lodBias

        self.numSurfaces = numSurfaces
        self.ofsSurfaces = ofsSurfaces
        self.numTags = numTags
        self.ofsTags = ofsTags

        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, version, name, lodScale, lodBias, numSurfaces, ofsSurfaces, \
        numTags, ofsTags, ofsEnd \
        = struct.unpack(MDMFileHeader.format, \
            file.read(MDMFileHeader.formatSize))

        mdmFileHeader = MDMFileHeader(ident, version, name, lodScale, \
        lodBias, numSurfaces, ofsSurfaces, numTags, ofsTags, ofsEnd)

        return mdmFileHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDMFileHeader.format, self.ident, self.version, \
            self.name, self.lodScale, self.lodBias, self.numSurfaces, \
            self.ofsSurfaces, self.numTags, self.ofsTags, self.ofsEnd))


class MDMFile:

    """Holds references to all MDM file data. Provides public file read and
    write functions.
    """

    def __init__(self):

        self.header = {}        # MDMFileHeader
        self.surfaces = []      # MDMSurface (numSurfaces)
        self.tags = []          # MDMTag (numTags)

    def read(filepath):
        with open(filepath, 'rb') as file:

            """Reads MDM file to MDMFile object.
            """

            mdmFile = MDMFile()

            # mdmFile.header
            fileOfs = 0
            mdmFile.header = MDMFileHeader.read(file, fileOfs)

            # mdmFile.surfaces
            fileOfs = mdmFile.header.ofsSurfaces
            for i in range(mdmFile.header.numSurfaces):

                mdmSurface = MDMSurface.read(file, fileOfs)
                mdmFile.surfaces.append(mdmSurface)

                fileOfs = fileOfs + mdmSurface.header.ofsEnd

            # mdmFile.tags
            fileOfs = mdmFile.header.ofsTags
            for i in range(mdmFile.header.numTags):

                mdmTag = MDMTag.read(file, fileOfs)
                mdmFile.tags.append(mdmTag)

                fileOfs = fileOfs + mdmTag.ofsEnd

            return mdmFile

    def write(self, filepath):
        with open(filepath, 'wb') as file:

            """Writes MDMFile object to MDM file.
            """

            # self.header
            fileOfs = 0
            self.header.write(file, fileOfs)

            # self.surfaces
            fileOfs = self.header.ofsSurfaces
            for surface in self.surfaces:

                surface.write(file, fileOfs)

                fileOfs = fileOfs + surface.header.ofsEnd

            # self.tags
            fileOfs = self.header.ofsTags
            for tag in self.tags:

                tag.write(file, fileOfs)

                fileOfs = fileOfs + tag.ofsEnd


# HELP
# ==============================================================================

import os
import sys
import bpy

def settings():

    mdmFilepathIn = dir + "\\import\\body_engineer_allied.mdm"
    mdmFilepathOut = dir + "\\export\\body_engineer_allied.mdm"

    xmlMdmFilepathOut = dir + "\\export\\body_engineer_allied.mdm.xml"
    #bindPoseFrame = 32
    #collapseMapFrame = 4274
    bindPoseFrame = 0
    collapseMapFrame = 1

    return (mdmFilepathIn, mdmFilepathOut, xmlMdmFilepathOut, bindPoseFrame, \
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

mdmFilepathIn, mdmFilepathOut, \
xmlMdmFilepathOut, \
bindPoseFrame, collapseMapFrame \
= settings()

mdmFile = MDMFile.read(mdmFilepathIn)
mdmFile.write(mdmFilepathOut)

XMLWriter.writeMDM(mdmFile, xmlMdmFilepathOut)

print("SUCCESS")
