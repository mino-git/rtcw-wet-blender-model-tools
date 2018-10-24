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

"""File backend for MDX file format. MDX contains skeletal animation data.
"""

import struct


class MDXBoneInfo:

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
        = struct.unpack(MDXBoneInfo.format, file.read(MDXBoneInfo.formatSize))

        mdxBoneInfo = MDXBoneInfo(name, parent, torsoWeight, parentDist, flags)

        return mdxBoneInfo

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDXBoneInfo.format, \
                               self.name, self.parent, self.torsoWeight, \
                               self.parentDist, self.flags))


class MDXBoneFrameCompressed:

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
        = struct.unpack(MDXBoneFrameCompressed.format, \
            file.read(MDXBoneFrameCompressed.formatSize))

        angles = (anglePitch, angleYaw, angleRoll, angleNone)
        offsetAngles = (offAnglePitch, offAngleYaw)

        mdxBoneFrameCompressed = MDXBoneFrameCompressed(angles, offsetAngles)

        return mdxBoneFrameCompressed

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDXBoneFrameCompressed.format, \
            self.angles[0], self.angles[1], self.angles[2], self.angles[3], \
            self.offsetAngles[0], self.offsetAngles[1]))


class MDXFrameHeader:

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

        minBoundsX, minBoundsY, minBoundsZ, maxBoundsX, maxBoundsY, \
        maxBoundsZ, localOriginX, localOriginY, localOriginZ, radius, \
        parentOffX, parentOffY, parentOffZ \
        = struct.unpack(MDXFrameHeader.format, \
            file.read(MDXFrameHeader.formatSize))

        mdxFrameHeader = MDXFrameHeader((minBoundsX, minBoundsY, minBoundsZ), \
            (maxBoundsX, maxBoundsY, maxBoundsZ), (localOriginX, localOriginY, \
            localOriginZ), radius, (parentOffX, parentOffY, parentOffZ))

        return mdxFrameHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDXFrameHeader.format, self.minBounds[0], \
            self.minBounds[1], self.minBounds[2], self.maxBounds[0], \
            self.maxBounds[1], self.maxBounds[2], self.localOrigin[0], \
            self.localOrigin[1], self.localOrigin[2], self.radius, \
            self.parentOffset[0], self.parentOffset[1], self.parentOffset[2]))


class MDXFrame:

    """Represents an animation frame. Holds references to general frame
    information, as well as each bones location and rotation values.
    """

    def __init__(self):

        self.header = {}                # MDXFrameHeader
        self.boneFramesCompressed = []  # MDXBoneFrameCompressed (numBones)

    def read(file, fileOfs, numBones):

        mdxFrame = MDXFrame()

        # mdxFrame.header
        mdxFrame.header = MDXFrameHeader.read(file, fileOfs)

        # mdxFrame.boneFramesCompressed
        fileOfs = fileOfs + MDXFrameHeader.formatSize

        for i in range(numBones):

            boneFrameCompressed = MDXBoneFrameCompressed.read(file, fileOfs)
            mdxFrame.boneFramesCompressed.append(boneFrameCompressed)

            fileOfs = fileOfs + MDXBoneFrameCompressed.formatSize

        return mdxFrame

    def write(self, file, fileOfs):

        # self.header
        self.header.write(file, fileOfs)

        # self.boneFramesCompressed
        fileOfs = fileOfs + MDXFrameHeader.formatSize

        for boneFrameCompressed in self.boneFramesCompressed:

            file.seek(fileOfs)

            boneFrameCompressed.write(file, fileOfs)

            fileOfs = fileOfs + MDXBoneFrameCompressed.formatSize


class MDXFileHeader:

    """General information about this file.
    """

    format = '<4si64siiiiii'
    formatSize = struct.calcsize(format)
    ident = b'MDXW'
    version = 2
    nameLen = 64

    def __init__(self, ident, version, name, numFrames, numBones, ofsFrames, \
        ofsBoneInfos, torsoParent, ofsEnd):

        self.ident = ident
        self.version = version
        self.name = name

        self.numFrames = numFrames
        self.numBones = numBones
        self.ofsFrames = ofsFrames
        self.ofsBoneInfos = ofsBoneInfos

        self.torsoParent = torsoParent

        self.ofsEnd = ofsEnd

    def read(file, fileOfs):

        file.seek(fileOfs)

        ident, version, name, numFrames, numBones, ofsFrames, ofsBoneInfos, \
        torsoParent, ofsEnd \
        = struct.unpack(MDXFileHeader.format, \
            file.read(MDXFileHeader.formatSize))

        mdxFileHeader = MDXFileHeader(ident, version, name, numFrames, \
            numBones, ofsFrames, ofsBoneInfos, torsoParent, ofsEnd)

        return mdxFileHeader

    def write(self, file, fileOfs):

        file.seek(fileOfs)

        file.write(struct.pack(MDXFileHeader.format, self.ident, self.version, \
            self.name, self.numFrames, self.numBones, self.ofsFrames, \
            self.ofsBoneInfos, self.torsoParent, self.ofsEnd))


class MDXFile:

    """Holds references to all MDX file data. Provides public file read and
    write functions.
    """

    def __init__(self):

        self.header = {}        # MDXFileHeader
        self.frames = []        # MDXFrame (numFrames)
        self.boneInfos = []     # MDXBoneInfo (numBones)

    def read(filepath):
        with open(filepath, 'rb') as file:

            """Reads MDX file to MDXFile object.
            """

            mdxFile = MDXFile()

            # mdxFile.header
            fileOfs = 0
            mdxFile.header = MDXFileHeader.read(file, fileOfs)

            # mdxFile.frames
            fileOfs = mdxFile.header.ofsFrames
            for i in range(0, mdxFile.header.numFrames):

                mdxFrame = MDXFrame.read(file, fileOfs, mdxFile.header.numBones)
                mdxFile.frames.append(mdxFrame)

                fileOfs = fileOfs + MDXFrameHeader.formatSize + \
                    mdxFile.header.numBones * MDXBoneFrameCompressed.formatSize

            # mdxFile.boneInfo
            fileOfs = mdxFile.header.ofsBoneInfos
            for i in range(0, mdxFile.header.numBones):

                mdxBoneInfo = MDXBoneInfo.read(file, fileOfs)
                mdxFile.boneInfos.append(mdxBoneInfo)

                fileOfs = fileOfs + MDXBoneInfo.formatSize

            return mdxFile

    def write(self, filepath):
        with open(filepath, 'wb') as file:

            """Writes MDXFile object to MDX file.
            """

            # self.header
            fileOfs = 0
            self.header.write(file, fileOfs)

            # self.frames
            fileOfs = self.header.ofsFrames
            for frame in self.frames:

                frame.write(file, fileOfs)

                fileOfs = fileOfs + MDXFrameHeader.formatSize + \
                    self.header.numBones * MDXBoneFrameCompressed.formatSize

            # self.boneInfo
            fileOfs = self.header.ofsBoneInfos
            for boneInfo in self.boneInfos:

                boneInfo.write(file, fileOfs)

                fileOfs = fileOfs + MDXBoneInfo.formatSize


# HELP
# ==============================================================================

import os
import sys
import bpy

def settings():

    mdxFilepathIn = dir + "\\import\\body.mdx"
    mdxFilepathOut = dir + "\\export\\body.mdx"

    xmlMdxFilepathOut = dir + "\\export\\body.mdx.xml"
    #bindPoseFrame = 32
    #collapseMapFrame = 4274
    bindPoseFrame = 0
    collapseMapFrame = 1

    return (mdxFilepathIn, mdxFilepathOut, xmlMdxFilepathOut, bindPoseFrame, \
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

mdxFilepathIn, mdxFilepathOut, \
xmlMdxFilepathOut, \
bindPoseFrame, collapseMapFrame \
= settings()

mdxFile = MDXFile.read(mdxFilepathIn)
mdxFile.write(mdxFilepathOut)

XMLWriter.writeMDX(mdxFile, xmlMdxFilepathOut)

print("SUCCESS")
