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

"""File backend for MDS file format. MDS contains mesh, tag and skeletal
animation data.
"""

import struct


class MDSTag:

    """Tags are used to specify which models (.md3, .mdc) the game code has to
    attach to the player model. They are a coordinate system (location and
    orientation). The attached models origin and orientation gets aligned with
    the origin and orientation of the tag. Animation is done in relation to a
    parent bone.
    """

    format = '<64sfi'
    formatSize = struct.calcsize(format)
    maxTags = 128
    nameLen = 64

    def __init__(self, name, torsoWeight, parentBoneIndex):

        self.name = name
        self.torsoWeight = torsoWeight
        self.parentBoneIndex = parentBoneIndex

    def read(file, fileOfs):

        file.seek(fileOfs)

        name, torsoWeight, parentBoneIndex \
        = struct.unpack(MDSTag.format, file.read(MDSTag.formatSize))

        mdsTag = MDSTag(name, torsoWeight, parentBoneIndex)

        return mdsTag

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSTag.format, self.name, self.torsoWeight, \
            self.parentBoneIndex))


class MDSBoneRefs:

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

            boneRef = struct.unpack(MDSBoneRefs.format, \
                file.read(MDSBoneRefs.formatSize))
            boneRefs.append(boneRef[0])

        mdsBoneRefs = MDSBoneRefs(boneRefs)

        return mdsBoneRefs

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        for i in range(0, len(self.boneRefs)):

            file.write(struct.pack(MDSBoneRefs.format, self.boneRefs[i]))


class MDSCollapseMap:

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

            mapping = struct.unpack(MDSCollapseMap.format, \
                file.read(MDSCollapseMap.formatSize))
            mappings.append(mapping[0])

        mdsCollapseMap = MDSCollapseMap(mappings)

        return mdsCollapseMap

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        for i in range(0, len(self.mappings)):

            file.write(struct.pack(MDSCollapseMap.format, self.mappings[i]))


class MDSTriangle:

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

        indices = struct.unpack(MDSTriangle.format, \
            file.read(MDSTriangle.formatSize))

        mdsTriangle = MDSTriangle(indices)

        return mdsTriangle

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSTriangle.format, self.indices[0], \
            self.indices[1], self.indices[2]))


class MDSWeight:

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
        = struct.unpack(MDSWeight.format, file.read(MDSWeight.formatSize))

        offsetLocation = (offsetX, offsetY, offsetZ)
        mdsWeight = MDSWeight(boneIndex, boneWeight, offsetLocation)

        return mdsWeight

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSWeight.format, self.boneIndex, \
            self.boneWeight, self.offsetLocation[0], self.offsetLocation[1], \
            self.offsetLocation[2]))


class MDSVertex:

    """Vertex information. The vertex normal is used for lightning (see Gouraud
    Shading). The texture coordinate is used for the UV Map. The list of weights
    defines the vertexes position in relation to bones.
    """

    format = '<fffffiif'
    formatSize = struct.calcsize(format)
    maxVertices = 6000
    maxWeights = 3

    def __init__(self, normal, texCoords, numWeights, fixedParent, fixedDist):

        self.normal = normal
        self.texCoords = texCoords
        self.numWeights = numWeights
        self.fixedParent = fixedParent
        self.fixedDist = fixedDist

        self.weights = [] # int (numWeights)

    def read(file, fileOfs):

        file.seek(fileOfs)

        normalX, normalY, normalZ, texCoordU, texCoordV, numWeights, \
        fixedParent, fixedDist \
        = struct.unpack(MDSVertex.format, file.read(MDSVertex.formatSize))

        mdsVertex = MDSVertex((normalX, normalY, normalZ), \
            (texCoordU, texCoordV), numWeights, fixedParent, fixedDist)

        # mdsVertex.weights
        fileOfs = fileOfs + MDSVertex.formatSize

        for i in range(mdsVertex.numWeights):

            mdsWeight = MDSWeight.read(file, fileOfs)
            mdsVertex.weights.append(mdsWeight)

            fileOfs = fileOfs + MDSWeight.formatSize

        return mdsVertex

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSVertex.format, self.normal[0], \
            self.normal[1], self.normal[2], self.texCoords[0], \
            self.texCoords[1], self.numWeights, self.fixedParent, \
            self.fixedDist))

        # self.weights
        fileOfs = fileOfs + MDSVertex.formatSize

        for weight in self.weights:

            weight.write(file, fileOfs)

            fileOfs = fileOfs + MDSWeight.formatSize


class MDSSurfaceHeader:

    """General information about this surface.
    """

    format = '<4s64s64siiiiiiiiiii'
    formatSize = struct.calcsize(format)
    ident = b'\x09\x00\x00\x00'
    nameLen = 64
    shaderNameLen = 64
    shaderIndex = 0

    def __init__(self, ident, name, shader, shaderIndex, minLod, ofsHeader, \
        numVertices, ofsVertices, numTriangles, ofsTriangles, ofsCollapseMap, \
        numBoneRefs, ofsBoneRefs, ofsEnd):

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
        = struct.unpack(MDSSurfaceHeader.format, \
            file.read(MDSSurfaceHeader.formatSize))

        mdsSurfaceHeader = MDSSurfaceHeader(ident, name, shader, shaderIndex, \
            minLod, ofsHeader, numVertices, ofsVertices, numTriangles, \
            ofsTriangles, ofsCollapseMap, numBoneRefs, ofsBoneRefs, ofsEnd)

        return mdsSurfaceHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSSurfaceHeader.format, self.ident, self.name, \
            self.shader, self.shaderIndex, self.minLod, self.ofsHeader,
            self.numVertices, self.ofsVertices, self.numTriangles, \
            self.ofsTriangles, self.ofsCollapseMap, self.numBoneRefs, \
            self.ofsBoneRefs, self.ofsEnd))


class MDSSurface:

    """Represents a surface. A surface is defined as a polygon mesh (triangle
    mesh). Because this format uses skeletal animation, each vertex is weighted
    against all of its associated bones in order to get its current frame
    position. The collapse map is used for creating different levels of detail
    (LOD) of the model during runtime (for the particular method used see
    "A Simple, Fast, and Effective Polygon Reduction Algorithm - Stan Melax".
    """

    formatCollapseMap = '<i'
    formatCollapseMapSize = struct.calcsize(formatCollapseMap)

    maxSurfaces = 32

    def __init__(self):

        self.header = {}         # MDSSurfaceHeader
        self.vertices = []       # MDSVertex (numVertices)
        self.triangles = []      # MDSTriangle (numTriangles)
        self.collapseMap = None  # MDSCollapseMap
        self.boneRefs = None     # MDSBoneRefs

    def read(file, fileOfs):

        mdsSurface = MDSSurface()

        mdsSurfaceOfs = fileOfs

        # mdsSurface.header
        mdsSurface.header = MDSSurfaceHeader.read(file, fileOfs)

        # mdsSurface.vertices
        fileOfs = mdsSurfaceOfs + mdsSurface.header.ofsVertices
        for i in range(mdsSurface.header.numVertices):

            mdsVertex = MDSVertex.read(file, fileOfs)
            mdsSurface.vertices.append(mdsVertex)

            fileOfs = fileOfs + MDSVertex.formatSize + \
                mdsVertex.numWeights * MDSWeight.formatSize

        # mdsSurface.triangles
        fileOfs = mdsSurfaceOfs + mdsSurface.header.ofsTriangles
        for i in range(mdsSurface.header.numTriangles):

            mdsTriangle = MDSTriangle.read(file, fileOfs)
            mdsSurface.triangles.append(mdsTriangle)

            fileOfs = fileOfs + MDSTriangle.formatSize

        # mdsSurface.collapseMap
        fileOfs = mdsSurfaceOfs + mdsSurface.header.ofsCollapseMap
        mdsSurface.collapseMap = MDSCollapseMap.read(file, fileOfs, \
            mdsSurface.header.numVertices)

        # mdsSurface.boneRefs
        fileOfs = mdsSurfaceOfs + mdsSurface.header.ofsBoneRefs
        mdsSurface.boneRefs = MDSBoneRefs.read(file, fileOfs, \
            mdsSurface.header.numBoneRefs)

        return mdsSurface

    def write(self, file, fileOfs):

        mdsSurfaceOfs = fileOfs

        # self.header
        self.header.write(file, fileOfs)

        # self.vertices
        fileOfs = mdsSurfaceOfs + self.header.ofsVertices
        for vertex in self.vertices:

            vertex.write(file, fileOfs)

            fileOfs = fileOfs + MDSVertex.formatSize + \
                vertex.numWeights * MDSWeight.formatSize

        # self.triangles
        fileOfs = mdsSurfaceOfs + self.header.ofsTriangles
        for triangle in self.triangles:

            triangle.write(file, fileOfs)

            fileOfs = fileOfs + MDSTriangle.formatSize

        # self.collapseMap
        fileOfs = mdsSurfaceOfs + self.header.ofsCollapseMap
        self.collapseMap.write(file, fileOfs)

        # self.boneRefs
        fileOfs = mdsSurfaceOfs + self.header.ofsBoneRefs
        self.boneRefs.write(file, fileOfs)


class MDSBoneInfo:

    """Frame independent bone information.
    """

    format = '<64siffi'
    formatSize = struct.calcsize(format)

    flagsDefaultValue = 0

    nameLen = 64
    minTorsoWeight = 0.0
    maxTorsoWeight = 1.0

    def __init__(self, name, parent, torsoWeight, parentDist, flags):

        self.name = name
        self.parent = parent
        self.torsoWeight = torsoWeight
        self.parentDist = parentDist
        self.flags = flags

    def read(file, fileOfs):

        file.seek(fileOfs)

        name, parent, torsoWeight, parentDist, flags \
        = struct.unpack(MDSBoneInfo.format, file.read(MDSBoneInfo.formatSize))

        mdsBoneInfo = MDSBoneInfo(name, parent, torsoWeight, parentDist, flags)

        return mdsBoneInfo

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSBoneInfo.format, self.name, self.parent, \
            self.torsoWeight, self.parentDist, self.flags))


class MDSBoneFrameCompressed:

    """Bone location and orientation in this frame.
    """

    format = '<hhhhhh'
    formatSize = struct.calcsize(format)

    angleScale = 360 / 65536.0
    offAngleScale = 360 / 4095.0

    angleNoneDefaultValue = 777

    def __init__(self, angles, offsetAngles):

        self.angles = angles # pitch, yaw, roll, none
        self.offsetAngles = offsetAngles # pitch, yaw

    def read(file, fileOfs):

        file.seek(fileOfs)

        anglePitch, angleYaw, angleRoll, angleNone, offAnglePitch, offAngleYaw \
        = struct.unpack(MDSBoneFrameCompressed.format, \
            file.read(MDSBoneFrameCompressed.formatSize))

        angles = (anglePitch, angleYaw, angleRoll, angleNone)
        offsetAngles = (offAnglePitch, offAngleYaw)
        mdsBoneFrameCompressed = MDSBoneFrameCompressed(angles, offsetAngles)

        return mdsBoneFrameCompressed

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSBoneFrameCompressed.format, \
            self.angles[0], self.angles[1], self.angles[2], self.angles[3], \
            self.offsetAngles[0], self.offsetAngles[1]))


class MDSFrameHeader:

    """General information about a frame.
    """

    format = '<fffffffffffff'
    formatSize = struct.calcsize(format)

    def __init__(self, minBounds, maxBounds, localOrigin, radius, parentOffset):

        self.minBounds = minBounds
        self.maxBounds = maxBounds
        self.localOrigin = localOrigin
        self.radius = radius
        self.parentOffset = parentOffset

    def read(file, fileOfs):

        file.seek(fileOfs)

        minBoundsX, minBoundsY, minBoundsZ, \
        maxBoundsX, maxBoundsY, maxBoundsZ, \
        localOriginX, localOriginY, localOriginZ, \
        radius, \
        parentOffX, parentOffY, parentOffZ \
        = struct.unpack(MDSFrameHeader.format, \
            file.read(MDSFrameHeader.formatSize))

        mdsFrameHeader = MDSFrameHeader((minBoundsX, minBoundsY, minBoundsZ), \
            (maxBoundsX, maxBoundsY, maxBoundsZ), \
            (localOriginX, localOriginY, localOriginZ), \
            radius, \
            (parentOffX, parentOffY, parentOffZ))

        return mdsFrameHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSFrameHeader.format, \
            self.minBounds[0], self.minBounds[1], self.minBounds[2], \
            self.maxBounds[0], self.maxBounds[1], self.maxBounds[2], \
            self.localOrigin[0], self.localOrigin[1], self.localOrigin[2], \
            self.radius, \
            self.parentOffset[0], self.parentOffset[1], self.parentOffset[2]))


class MDSFrame:

    """Represents an animation frame. Holds references to general frame
    information, as well as each bones location and rotation values.
    """

    def __init__(self):

        self.header = {}                # MDSFrameHeader
        self.boneFramesCompressed = []  # MDSBoneFrameCompressed (numBones)

    def read(file, fileOfs, numBones):

        mdsFrame = MDSFrame()

        # mdsFrame.header
        mdsFrame.header = MDSFrameHeader.read(file, fileOfs)

        # mdsFrame.boneFramesCompressed
        fileOfs = fileOfs + MDSFrameHeader.formatSize

        for i in range(0, numBones):

            boneFrameCompressed = MDSBoneFrameCompressed.read(file, fileOfs)
            mdsFrame.boneFramesCompressed.append(boneFrameCompressed)

            fileOfs = fileOfs + MDSBoneFrameCompressed.formatSize

        return mdsFrame

    def write(self, file, fileOfs):

        # self.header
        self.header.write(file, fileOfs)

        # self.boneFramesCompressed
        fileOfs = fileOfs + MDSFrameHeader.formatSize

        for boneFrameCompressed in self.boneFramesCompressed:

            file.seek(fileOfs)

            boneFrameCompressed.write(file, fileOfs)

            fileOfs = fileOfs + MDSBoneFrameCompressed.formatSize


class MDSFileHeader:

    """General information about this file.
    """

    format = '<4si64sffiiiiiiiiii'
    formatSize = struct.calcsize(format)
    ident = b'MDSW'
    version = 4
    nameLen = 64

    def __init__(self, ident, version, name, lodScale, lodBias, numFrames, \
        numBones, ofsFrames, ofsBoneInfos, torsoParent, numSurfaces, \
        ofsSurfaces, numTags, ofsTags, ofsEnd):

        self.ident = ident
        self.version = version
        self.name = name

        self.lodScale = lodScale
        self.lodBias = lodBias

        self.numFrames = numFrames
        self.numBones = numBones

        self.ofsFrames = ofsFrames
        self.ofsBoneInfos = ofsBoneInfos

        self.torsoParent = torsoParent

        self.numSurfaces = numSurfaces
        self.ofsSurfaces = ofsSurfaces
        self.numTags = numTags
        self.ofsTags = ofsTags

        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, version, name, lodScale, lodBias, numFrames, numBones, \
        ofsFrames, ofsBoneInfos, torsoParent, numSurfaces, ofsSurfaces, \
        numTags, ofsTags, ofsEnd \
        = struct.unpack(MDSFileHeader.format, \
            file.read(MDSFileHeader.formatSize))

        mdsFileHeader = MDSFileHeader(ident, version, name, lodScale, lodBias, \
            numFrames, numBones, ofsFrames, ofsBoneInfos, torsoParent, \
            numSurfaces, ofsSurfaces, numTags, ofsTags, ofsEnd)

        return mdsFileHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDSFileHeader.format, self.ident, self.version, \
            self.name, self.lodScale, self.lodBias, self.numFrames, \
            self.numBones, self.ofsFrames, self.ofsBoneInfos, \
            self.torsoParent, self.numSurfaces, self.ofsSurfaces, \
            self.numTags, self.ofsTags, self.ofsEnd))


class MDSFile:

    """Holds references to all MDS file data. Provides public file read and
    write functions.
    """

    def __init__(self):

        self.header = {}        # MDSFileHeader
        self.frames = []        # MDSFrame (numFrames)
        self.boneInfos = []     # MDSBoneInfo (numBones)
        self.surfaces = []      # MDSSurface (numSurfaces)
        self.tags = []          # MDSTag (numTags)

    def read(filepath):
        with open(filepath, 'rb') as file:

            """Reads MDS file to MDSFile object.
            """

            mdsFile = MDSFile()

            # mdsFile.header
            fileOfs = 0
            mdsFile.header = MDSFileHeader.read(file, fileOfs)

            # mdsFile.frames
            fileOfs = mdsFile.header.ofsFrames
            for i in range(0, mdsFile.header.numFrames):

                mdsFrame = MDSFrame.read(file, fileOfs, mdsFile.header.numBones)
                mdsFile.frames.append(mdsFrame)

                fileOfs = fileOfs + MDSFrameHeader.formatSize + \
                    mdsFile.header.numBones * MDSBoneFrameCompressed.formatSize

            # mdsFile.boneInfos
            fileOfs = mdsFile.header.ofsBoneInfos
            for i in range(0, mdsFile.header.numBones):

                mdsBoneInfo = MDSBoneInfo.read(file, fileOfs)
                mdsFile.boneInfos.append(mdsBoneInfo)

                fileOfs = fileOfs + MDSBoneInfo.formatSize

            # mdsFile.surfaces
            fileOfs = mdsFile.header.ofsSurfaces
            for i in range(0, mdsFile.header.numSurfaces):

                mdsSurface = MDSSurface.read(file, fileOfs)
                mdsFile.surfaces.append(mdsSurface)

                fileOfs = fileOfs + mdsSurface.header.ofsEnd

            # mdsFile.tags
            fileOfs = mdsFile.header.ofsTags
            for i in range(0, mdsFile.header.numTags):

                mdsTag = MDSTag.read(file, fileOfs)
                mdsFile.tags.append(mdsTag)

                fileOfs = fileOfs + MDSTag.formatSize

            return mdsFile

    def write(self, filepath):
        with open(filepath, 'wb') as file:

            """Writes MDSFile object to MDS file.
            """

            # self.header
            fileOfs = 0
            self.header.write(file, fileOfs)

            # self.frames
            fileOfs = self.header.ofsFrames
            for frame in self.frames:

                frame.write(file, fileOfs)

                fileOfs = fileOfs + MDSFrameHeader.formatSize + \
                    self.header.numBones * MDSBoneFrameCompressed.formatSize

            # self.boneInfos
            fileOfs = self.header.ofsBoneInfos
            for boneInfo in self.boneInfos:

                boneInfo.write(file, fileOfs)

                fileOfs = fileOfs + MDSBoneInfo.formatSize

            # self.surfaces
            fileOfs = self.header.ofsSurfaces
            for surface in self.surfaces:

                surface.write(file, fileOfs)

                fileOfs = fileOfs + surface.header.ofsEnd

            # self.tags
            fileOfs = self.header.ofsTags
            for tag in self.tags:

                tag.write(file, fileOfs)

                fileOfs = fileOfs + MDSTag.formatSize


# HELP
# ==============================================================================

import os
import sys
import bpy

def settings():

    mdsFilepathIn = dir + "\\import\\body.mds"
    mdsFilepathOut = dir + "\\export\\body.mds"

    xmlMdsFilepathOut = dir + "\\export\\body.mds.xml"
    #bindPoseFrame = 32
    #collapseMapFrame = 4274
    bindPoseFrame = 0
    collapseMapFrame = 1

    return (mdsFilepathIn, mdsFilepathOut, xmlMdsFilepathOut, bindPoseFrame, \
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

mdsFilepathIn, mdsFilepathOut, \
xmlMdsFilepathOut, \
bindPoseFrame, collapseMapFrame \
= settings()

mdsFile = MDSFile.read(mdsFilepathIn)
mdsFile.write(mdsFilepathOut)

XMLWriter.writeMDS(mdsFile, xmlMdsFilepathOut)

print("SUCCESS")
