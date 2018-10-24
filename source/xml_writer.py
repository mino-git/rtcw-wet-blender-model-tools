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


"""XML serializer for md3, mdc, mdm/mdx, mds model formats.
"""

from util import *

import xml.etree.ElementTree as et

class XMLWriter:

        def writeMDS(mdsFile, filePath, frameRange=None):

            # this won't work if a surface has a different frame range than
            # the one given in the file header
            frameStart = 0
            frameEnd = md3File.header.numFrames
            if frameRange != None:
                frameStart = frameRange[0]
                frameEnd = frameRange[1]

            treeMDSFile = et.Element("MDSFile")

            # header
            treeHeader = et.SubElement(treeMDSFile, "header")

            treeMDSFileHeader = et.SubElement(treeHeader, "MDSFileHeader")

            et.SubElement(treeMDSFileHeader, "ident").text \
            = str(mdsFile.header.ident)

            et.SubElement(treeMDSFileHeader, "version").text \
            = str(mdsFile.header.version)

            et.SubElement(treeMDSFileHeader, "name").text \
            = str(Util.cleanupString(mdsFile.header.name))

            et.SubElement(treeMDSFileHeader, "lodScale").text \
            = str(mdsFile.header.lodScale)

            et.SubElement(treeMDSFileHeader, "lodBias").text \
            = str(mdsFile.header.lodBias)

            et.SubElement(treeMDSFileHeader, "numFrames").text \
            = str(mdsFile.header.numFrames)

            et.SubElement(treeMDSFileHeader, "numBones").text \
            = str(mdsFile.header.numBones)

            et.SubElement(treeMDSFileHeader, "ofsFrames").text \
            = str(mdsFile.header.ofsFrames)

            et.SubElement(treeMDSFileHeader, "ofsBoneInfos").text \
            = str(mdsFile.header.ofsBoneInfos)

            et.SubElement(treeMDSFileHeader, "torsoParent").text \
            = str(mdsFile.header.torsoParent)

            et.SubElement(treeMDSFileHeader, "numSurfaces").text \
            = str(mdsFile.header.numSurfaces)

            et.SubElement(treeMDSFileHeader, "ofsSurfaces").text \
            = str(mdsFile.header.ofsSurfaces)

            et.SubElement(treeMDSFileHeader, "numTags").text \
            = str(mdsFile.header.numTags)

            et.SubElement(treeMDSFileHeader, "ofsTags").text \
            = str(mdsFile.header.ofsTags)

            et.SubElement(treeMDSFileHeader, "ofsEnd").text \
            = str(mdsFile.header.ofsEnd)

            # frames
            treeFrames = et.SubElement(treeMDSFile, "frames")

            for i in range(frameStart, frameEnd):

                mdsFrame = mdsFile.frames[i]

                treeMDSFrame \
                = et.SubElement(treeFrames, "MDSFrame", frameNum=str(i))

                # header
                treeHeader = et.SubElement(treeMDSFrame, "header")

                treeMDSFrameHeader = et.SubElement(treeHeader, \
                    "MDSFrameHeader")

                et.SubElement(treeMDSFrameHeader, "minBounds").text \
                = str(mdsFrame.header.minBounds)

                et.SubElement(treeMDSFrameHeader, "maxBounds").text \
                = str(mdsFrame.header.maxBounds)

                et.SubElement(treeMDSFrameHeader, "localOrigin").text \
                = str(mdsFrame.header.localOrigin)

                et.SubElement(treeMDSFrameHeader, "radius").text \
                = str(mdsFrame.header.radius)

                et.SubElement(treeMDSFrameHeader, "parentOffset").text \
                = str(mdsFrame.header.parentOffset)

                # boneFramesCompressed
                treeBoneFramesCompressed = et.SubElement(treeMDSFrame, \
                    "boneFramesCompressed")

                for j in range(0, mdsFile.header.numBones):

                    mdsBoneFrameCompressed = mdsFrame.boneFramesCompressed[j]

                    treeMdsBoneFrameCompressed = et.SubElement( \
                        treeBoneFramesCompressed, "MDSBoneFrameCompressed", \
                        boneNum=str(j))

                    anglesStr = "({}, {}, {}, {})".format( \
                        mdsBoneFrameCompressed.angles[0], \
                        mdsBoneFrameCompressed.angles[1], \
                        mdsBoneFrameCompressed.angles[2], \
                        mdsBoneFrameCompressed.angles[3])
                    et.SubElement(treeMdsBoneFrameCompressed, "angles").text \
                    = anglesStr

                    offsetAnglesStr = "({}, {})".format( \
                        mdsBoneFrameCompressed.offsetAngles[0], \
                        mdsBoneFrameCompressed.offsetAngles[1])
                    et.SubElement(treeMdsBoneFrameCompressed, "offsetAngles") \
                    .text = offsetAnglesStr

            # boneInfos
            treeBoneInfos = et.SubElement(treeMDSFile, "boneInfos")
            for i in range(0, mdsFile.header.numBones):

                mdsBoneInfo = mdsFile.boneInfos[i]

                treeMDSBoneInfo = et.SubElement(treeBoneInfos, "MDSBoneInfo", \
                    boneNum=str(i))

                et.SubElement(treeMDSBoneInfo, "name").text \
                = Util.cleanupString((mdsBoneInfo.name))

                et.SubElement(treeMDSBoneInfo, "parent").text \
                = str(mdsBoneInfo.parent)

                et.SubElement(treeMDSBoneInfo, "torsoWeight").text \
                = str(mdsBoneInfo.torsoWeight)

                et.SubElement(treeMDSBoneInfo, "parentDist").text \
                = str(mdsBoneInfo.parentDist)

                et.SubElement(treeMDSBoneInfo, "flags").text \
                = str(mdsBoneInfo.flags)

            # surfaces
            treeSurfaces = et.SubElement(treeMDSFile, "surfaces")
            for i in range(0, mdsFile.header.numSurfaces):

                mdsSurface = mdsFile.surfaces[i]

                treeMDSSurface = et.SubElement(treeSurfaces, "MDSSurface", \
                    surfaceNum=str(i))

                # header
                treeHeader = et.SubElement(treeMDSSurface, "header")

                et.SubElement(treeHeader, "ident").text \
                = str(mdsSurface.header.ident)

                et.SubElement(treeHeader, "name").text \
                = str(Util.cleanupString(mdsSurface.header.name))

                et.SubElement(treeHeader, "shader").text \
                = str(Util.cleanupString(mdsSurface.header.shader))

                et.SubElement(treeHeader, "shaderIndex").text \
                = str(mdsSurface.header.shaderIndex)

                et.SubElement(treeHeader, "minLod").text \
                = str(mdsSurface.header.minLod)

                et.SubElement(treeHeader, "ofsHeader").text \
                = str(mdsSurface.header.ofsHeader)

                et.SubElement(treeHeader, "numVertices").text \
                = str(mdsSurface.header.numVertices)

                et.SubElement(treeHeader, "ofsVertices").text \
                = str(mdsSurface.header.ofsVertices)

                et.SubElement(treeHeader, "numTriangles").text \
                = str(mdsSurface.header.numTriangles)

                et.SubElement(treeHeader, "ofsTriangles").text \
                = str(mdsSurface.header.ofsTriangles)

                et.SubElement(treeHeader, "ofsCollapseMap").text \
                = str(mdsSurface.header.ofsCollapseMap)

                et.SubElement(treeHeader, "numBoneRefs").text \
                = str(mdsSurface.header.numBoneRefs)

                et.SubElement(treeHeader, "ofsBoneRefs").text \
                = str(mdsSurface.header.ofsBoneRefs)

                et.SubElement(treeHeader, "ofsEnd").text \
                = str(mdsSurface.header.ofsEnd)

                # vertices
                treeVertices = et.SubElement(treeMDSSurface, "vertices")

                for j in range(0, mdsSurface.header.numVertices):

                    mdsVertex = mdsSurface.vertices[j]

                    treeMDSVertex = et.SubElement(treeVertices, "MDSVertex", \
                        vertexNum=str(j))

                    et.SubElement(treeMDSVertex, "normal").text \
                    = str(mdsVertex.normal)

                    et.SubElement(treeMDSVertex, "texCoords").text \
                    = str(mdsVertex.texCoords)

                    et.SubElement(treeMDSVertex, "numWeights").text \
                    = str(mdsVertex.numWeights)

                    et.SubElement(treeMDSVertex, "fixedParent").text \
                    = str(mdsVertex.fixedParent)

                    et.SubElement(treeMDSVertex, "fixedDist").text \
                    = str(mdsVertex.fixedDist)

                    # weights
                    treeWeights = et.SubElement(treeMDSVertex, "weights")

                    for k in range(0, len(mdsVertex.weights)):

                        mdsWeight = mdsVertex.weights[k]

                        treeMDSWeight = et.SubElement(treeWeights, \
                            "MDSWeight", weightNum=str(k))

                        et.SubElement(treeMDSWeight, "boneIndex").text \
                        = str(mdsWeight.boneIndex)

                        et.SubElement(treeMDSWeight, "boneWeight").text \
                        = str(mdsWeight.boneWeight)

                        et.SubElement(treeMDSWeight, "offsetLocation").text \
                        = str(mdsWeight.offsetLocation)

                # triangles
                treeTriangles = et.SubElement(treeMDSSurface, "triangles")

                for j in range(0, mdsSurface.header.numTriangles):

                    mdsTriangle = mdsSurface.triangles[j]

                    treeMDSTriangle = et.SubElement(treeTriangles, \
                        "MDSTriangle")

                    et.SubElement(treeMDSTriangle, "indices").text \
                    = str(mdsTriangle.indices)

                # collapseMap
                treeMDSCollapseMap = et.SubElement(treeMDSSurface, \
                    "collapseMap")

                for j in range(0, mdsSurface.header.numVertices):

                    treeMapping = et.SubElement(treeMDSCollapseMap, "mapping", \
                        vertexNum=str(j)).text \
                    = str(mdsSurface.collapseMap.mappings[j])

                # boneRefs
                treeBoneRefs = et.SubElement(treeMDSSurface, "boneRefs")

                for j in range(0, mdsSurface.header.numBoneRefs):

                    treeMapping = et.SubElement(treeBoneRefs, "boneRef").text \
                    = str(mdsSurface.boneRefs.boneRefs[j])

            # tags
            treeTags = et.SubElement(treeMDSFile, "tags")
            for i in range(0, mdsFile.header.numTags):

                mdsTag = mdsFile.tags[i]

                treeMDSTag = et.SubElement(treeTags, "MDSTag", tagNum=str(i))

                et.SubElement(treeMDSTag, "name").text \
                = Util.cleanupString((mdsTag.name))

                et.SubElement(treeMDSTag, "torsoWeight").text \
                = str(mdsTag.torsoWeight)

                et.SubElement(treeMDSTag, "parentBoneIndex").text \
                = str(mdsTag.parentBoneIndex)

            tree = et.ElementTree(treeMDSFile)
            tree.write(filePath)

        def writeMDM(mdmFile, filePath):

            treeMDMFile = et.Element("MDMFile")

            # header
            treeHeader = et.SubElement(treeMDMFile, "header")

            treeMDMFileHeader = et.SubElement(treeHeader, "MDMFileHeader")

            et.SubElement(treeMDMFileHeader, "ident").text \
            = str(mdmFile.header.ident)

            et.SubElement(treeMDMFileHeader, "version").text \
            = str(mdmFile.header.version)

            et.SubElement(treeMDMFileHeader, "name").text = \
            str(Util.cleanupString(mdmFile.header.name))

            et.SubElement(treeMDMFileHeader, "lodScale").text \
            = str(mdmFile.header.lodScale)

            et.SubElement(treeMDMFileHeader, "lodBias").text \
            = str(mdmFile.header.lodBias)

            et.SubElement(treeMDMFileHeader, "numSurfaces").text \
            = str(mdmFile.header.numSurfaces)

            et.SubElement(treeMDMFileHeader, "ofsSurfaces").text \
            = str(mdmFile.header.ofsSurfaces)

            et.SubElement(treeMDMFileHeader, "numTags").text \
            = str(mdmFile.header.numTags)

            et.SubElement(treeMDMFileHeader, "ofsTags").text \
            = str(mdmFile.header.ofsTags)

            et.SubElement(treeMDMFileHeader, "ofsEnd").text \
            = str(mdmFile.header.ofsEnd)

            # surfaces
            treeSurfaces = et.SubElement(treeMDMFile, "surfaces")
            for i in range(0, mdmFile.header.numSurfaces):

                mdmSurface = mdmFile.surfaces[i]

                treeMDMSurface = et.SubElement(treeSurfaces, "MDMSurface", \
                    surfaceNum=str(i))

                # header
                treeHeader = et.SubElement(treeMDMSurface, "header")

                et.SubElement(treeHeader, "ident").text \
                = str(mdmSurface.header.ident)

                et.SubElement(treeHeader, "name").text \
                = str(Util.cleanupString(mdmSurface.header.name))

                et.SubElement(treeHeader, "shader").text \
                = str(Util.cleanupString(mdmSurface.header.shader))

                et.SubElement(treeHeader, "shaderIndex").text \
                = str(mdmSurface.header.shaderIndex)

                et.SubElement(treeHeader, "minLod").text \
                = str(mdmSurface.header.minLod)

                et.SubElement(treeHeader, "ofsHeader").text \
                = str(mdmSurface.header.ofsHeader)

                et.SubElement(treeHeader, "numVertices").text \
                = str(mdmSurface.header.numVertices)

                et.SubElement(treeHeader, "ofsVertices").text \
                = str(mdmSurface.header.ofsVertices)

                et.SubElement(treeHeader, "numTriangles").text \
                = str(mdmSurface.header.numTriangles)

                et.SubElement(treeHeader, "ofsTriangles").text \
                = str(mdmSurface.header.ofsTriangles)

                et.SubElement(treeHeader, "ofsCollapseMap").text \
                = str(mdmSurface.header.ofsCollapseMap)

                et.SubElement(treeHeader, "numBoneRefs").text \
                = str(mdmSurface.header.numBoneRefs)

                et.SubElement(treeHeader, "ofsBoneRefs").text \
                = str(mdmSurface.header.ofsBoneRefs)

                et.SubElement(treeHeader, "ofsEnd").text \
                = str(mdmSurface.header.ofsEnd)

                # vertices
                treeVertices = et.SubElement(treeMDMSurface, "vertices")

                for j in range(0, mdmSurface.header.numVertices):

                    mdmVertex = mdmSurface.vertices[j]

                    treeMDMVertex = et.SubElement(treeVertices, "MDMVertex", \
                        vertexNum=str(j))

                    et.SubElement(treeMDMVertex, "normal").text \
                    = str(mdmVertex.normal)

                    et.SubElement(treeMDMVertex, "texCoords").text \
                    = str(mdmVertex.texCoords)

                    et.SubElement(treeMDMVertex, "numWeights").text \
                    = str(mdmVertex.numWeights)

                    # weights
                    treeWeights = et.SubElement(treeMDMVertex, "weights")

                    for k in range(0, len(mdmVertex.weights)):

                        mdmWeight = mdmVertex.weights[k]

                        treeMDMWeight = et.SubElement(treeWeights, \
                            "MDMWeight", weightNum=str(k))

                        et.SubElement(treeMDMWeight, "boneIndex").text \
                        = str(mdmWeight.boneIndex)

                        et.SubElement(treeMDMWeight, "boneWeight").text \
                        = str(mdmWeight.boneWeight)

                        et.SubElement(treeMDMWeight, "offsetLocation").text \
                        = str(mdmWeight.offsetLocation)

                # triangles
                treeTriangles = et.SubElement(treeMDMSurface, "triangles")

                for j in range(0, mdmSurface.header.numTriangles):

                    mdmTriangle = mdmSurface.triangles[j]

                    treeMDMTriangle = et.SubElement(treeTriangles, \
                        "MDMTriangle")

                    et.SubElement(treeMDMTriangle, "indices").text \
                    = str(mdmTriangle.indices)

                # collapseMap
                treeCollapseMap = et.SubElement(treeMDMSurface, \
                    "collapseMap")

                for j in range(0, mdmSurface.header.numVertices):

                    treeMapping = et.SubElement(treeCollapseMap, "mapping", \
                        vertexNum=str(j)).text \
                    = str(mdmSurface.collapseMap.mappings[j])

                # boneRefs
                treeBoneRefs = et.SubElement(treeMDMSurface, "boneRefs")

                for j in range(0, mdmSurface.header.numBoneRefs):

                    treeMapping = et.SubElement(treeBoneRefs, "boneRef").text \
                    = str(mdmSurface.boneRefs.boneRefs[j])

            # tags
            treeTags = et.SubElement(treeMDMFile, "tags")
            for i in range(0, mdmFile.header.numTags):

                mdmTag = mdmFile.tags[i]

                treeMDMTag = et.SubElement(treeTags, "MDMTag", tagNum=str(i))

                et.SubElement(treeMDMTag, "name").text \
                = Util.cleanupString((mdmTag.name))

                rotationMatrixStr = "({}, {}, {}),({}, {}, {}), \
                    ({}, {}, {}))".format(mdmTag.rotationMatrix[0][0], \
                    mdmTag.rotationMatrix[0][1], mdmTag.rotationMatrix[0][2], \
                    mdmTag.rotationMatrix[1][0], mdmTag.rotationMatrix[1][1], \
                    mdmTag.rotationMatrix[1][2], mdmTag.rotationMatrix[2][0], \
                    mdmTag.rotationMatrix[2][1], mdmTag.rotationMatrix[2][2])
                et.SubElement(treeMDMTag, "rotationMatrix").text \
                = rotationMatrixStr

                et.SubElement(treeMDMTag, "parentBoneIndex").text \
                = str(mdmTag.parentBoneIndex)

                et.SubElement(treeMDMTag, "offsetLocation").text \
                = str(mdmTag.offsetLocation)

                et.SubElement(treeMDMTag, "numBoneRefs").text \
                = str(mdmTag.numBoneRefs)

                et.SubElement(treeMDMTag, "ofsBoneRefs").text \
                = str(mdmTag.ofsBoneRefs)

                et.SubElement(treeMDMTag, "ofsEnd").text \
                = str(mdmTag.ofsEnd)

                # boneRefs
                treeBoneRefs = et.SubElement(treeMDMTag, "boneRefs")

                for j in range(0, mdmTag.numBoneRefs):

                    treeMapping = et.SubElement(treeBoneRefs, "boneRef").text \
                    = str(mdmTag.boneRefs.boneRefs[j])

            tree = et.ElementTree(treeMDMFile)
            tree.write(filePath)

        def writeMDX(mdxFile, filePath, frameRange=None):

            # this won't work if a surface has a different frame range than
            # the one given in the file header
            frameStart = 0
            frameEnd = md3File.header.numFrames
            if frameRange != None:
                frameStart = frameRange[0]
                frameEnd = frameRange[1]

            treeMDXFile = et.Element("MDXFile")

            # header
            treeHeader = et.SubElement(treeMDXFile, "header")

            treeMDXFileHeader = et.SubElement(treeHeader, "MDXFileHeader")

            et.SubElement(treeMDXFileHeader, "ident").text \
            = str(mdxFile.header.ident)

            et.SubElement(treeMDXFileHeader, "version").text \
            = str(mdxFile.header.version)

            et.SubElement(treeMDXFileHeader, "name").text = \
            str(Util.cleanupString(mdxFile.header.name))

            et.SubElement(treeMDXFileHeader, "numFrames").text = \
            str(mdxFile.header.numFrames)

            et.SubElement(treeMDXFileHeader, "numBones").text = \
            str(mdxFile.header.numBones)

            et.SubElement(treeMDXFileHeader, "ofsFrames").text = \
            str(mdxFile.header.ofsFrames)

            et.SubElement(treeMDXFileHeader, "ofsBoneInfos").text = \
            str(mdxFile.header.ofsBoneInfos)

            et.SubElement(treeMDXFileHeader, "torsoParent").text = \
            str(mdxFile.header.torsoParent)

            et.SubElement(treeMDXFileHeader, "ofsEnd").text = \
            str(mdxFile.header.ofsEnd)

            # frames
            treeFrames = et.SubElement(treeMDXFile, "frames")

            for i in range(frameStart, frameEnd):

                mdxFrame = mdxFile.frames[i]

                treeMDXFrame \
                = et.SubElement(treeFrames, "MDXFrame", frameNum=str(i))

                # header
                treeHeader = et.SubElement(treeMDXFrame, "header")

                treeMDXFrameHeader = et.SubElement(treeHeader, \
                    "MDXFrameHeader")

                et.SubElement(treeMDXFrameHeader, "minBounds").text \
                = str(mdxFrame.header.minBounds)

                et.SubElement(treeMDXFrameHeader, "maxBounds").text \
                = str(mdxFrame.header.maxBounds)

                et.SubElement(treeMDXFrameHeader, "localOrigin").text \
                = str(mdxFrame.header.localOrigin)

                et.SubElement(treeMDXFrameHeader, "radius").text \
                = str(mdxFrame.header.radius)

                et.SubElement(treeMDXFrameHeader, "parentOffset").text \
                = str(mdxFrame.header.parentOffset)

                # boneFramesCompressed
                treeBoneFramesCompressed = et.SubElement(treeMDXFrame, \
                    "boneFramesCompressed")

                for j in range(0, mdxFile.header.numBones):

                    mdxBoneFrameCompressed = mdxFrame.boneFramesCompressed[j]

                    treeMdxBoneFrameCompressed = et.SubElement( \
                        treeBoneFramesCompressed, "MDXBoneFrameCompressed", \
                        boneNum=str(j))

                    anglesStr = "({}, {}, {}, {})".format( \
                        mdxBoneFrameCompressed.angles[0], \
                        mdxBoneFrameCompressed.angles[1], \
                        mdxBoneFrameCompressed.angles[2], \
                        mdxBoneFrameCompressed.angles[3])
                    et.SubElement(treeMdxBoneFrameCompressed, "angles").text \
                    = anglesStr

                    offsetAnglesStr = "({}, {})".format( \
                        mdxBoneFrameCompressed.offsetAngles[0], \
                        mdxBoneFrameCompressed.offsetAngles[1])
                    et.SubElement(treeMdxBoneFrameCompressed, "offsetAngles") \
                    .text = offsetAnglesStr

            # boneInfos
            treeBoneInfos = et.SubElement(treeMDXFile, "boneInfos")
            for i in range(0, mdxFile.header.numBones):

                mdxBoneInfo = mdxFile.boneInfos[i]

                treeMDXBoneInfo = et.SubElement(treeBoneInfos, "MDXBoneInfo", \
                    boneNum=str(i))

                et.SubElement(treeMDXBoneInfo, "name").text \
                = Util.cleanupString((mdxBoneInfo.name))

                et.SubElement(treeMDXBoneInfo, "parent").text \
                = str(mdxBoneInfo.parent)

                et.SubElement(treeMDXBoneInfo, "torsoWeight").text \
                = str(mdxBoneInfo.torsoWeight)

                et.SubElement(treeMDXBoneInfo, "parentDist").text \
                = str(mdxBoneInfo.parentDist)

                et.SubElement(treeMDXBoneInfo, "flags").text \
                = str(mdxBoneInfo.flags)

            tree = et.ElementTree(treeMDXFile)
            tree.write(filePath)

        def writeMD3(md3File, filePath, frameRange=None):

            # this won't work if a surface has a different frame range than
            # the one given in the file header
            frameStart = 0
            frameEnd = md3File.header.numFrames
            if frameRange != None:
                frameStart = frameRange[0]
                frameEnd = frameRange[1]

            treeMD3File = et.Element("MD3File")

            # header
            treeHeader = et.SubElement(treeMD3File, "header")

            treeMD3FileHeader = et.SubElement(treeHeader, "MD3FileHeader")

            et.SubElement(treeMD3FileHeader, "ident").text \
            = str(md3File.header.ident)

            et.SubElement(treeMD3FileHeader, "version").text \
            = str(md3File.header.version)

            et.SubElement(treeMD3FileHeader, "name").text = \
            str(Util.cleanupString(md3File.header.name))

            et.SubElement(treeMD3FileHeader, "flags").text \
            = str(md3File.header.version)

            et.SubElement(treeMD3FileHeader, "numFrames").text \
            = str(md3File.header.numFrames)

            et.SubElement(treeMD3FileHeader, "numTags").text \
            = str(md3File.header.numTags)

            et.SubElement(treeMD3FileHeader, "numSurfaces").text \
            = str(md3File.header.numSurfaces)

            et.SubElement(treeMD3FileHeader, "numSkins").text \
            = str(md3File.header.numSkins)

            et.SubElement(treeMD3FileHeader, "ofsFrameHeaders").text \
            = str(md3File.header.ofsFrameHeaders)

            et.SubElement(treeMD3FileHeader, "ofsTags").text \
            = str(md3File.header.ofsTags)

            et.SubElement(treeMD3FileHeader, "ofsSurfaces").text \
            = str(md3File.header.ofsSurfaces)

            et.SubElement(treeMD3FileHeader, "ofsEnd").text \
            = str(md3File.header.ofsEnd)

            # frameHeaders
            treeFrames = et.SubElement(treeMD3File, "frameHeaders")

            for i in range(frameStart, frameEnd):

                md3FrameHeader = md3File.frameHeaders[i]

                treeMD3FrameHeader \
                = et.SubElement(treeFrames, "MD3FrameHeader", frameNum=str(i))

                et.SubElement(treeMD3FrameHeader, "minBounds").text \
                = str(md3FrameHeader.minBounds)

                et.SubElement(treeMD3FrameHeader, "maxBounds").text \
                = str(md3FrameHeader.maxBounds)

                et.SubElement(treeMD3FrameHeader, "localOrigin").text \
                = str(md3FrameHeader.localOrigin)

                et.SubElement(treeMD3FrameHeader, "radius").text \
                = str(md3FrameHeader.radius)

                et.SubElement(treeMD3FrameHeader, "name").text \
                = str(Util.cleanupString(md3FrameHeader.name))

            # tags
            treeTags = et.SubElement(treeMD3File, "tags")

            for i in range(frameStart, frameEnd):

                frameTags = md3File.tags[i]

                treeFrameTags = et.SubElement(treeTags, "frameTags", \
                    frameNum=str(i))

                for j in range(0, md3File.header.numTags):

                    md3Tag = frameTags[j]

                    treeMD3Tag \
                    = et.SubElement(treeFrameTags, "MD3Tag", tagNum=str(j))

                    et.SubElement(treeMD3Tag, "name").text \
                    = str(Util.cleanupString(md3Tag.name))

                    et.SubElement(treeMD3Tag, "location").text \
                    = str(md3Tag.location)

                    rotationMatrixStr = "({}, {}, {}),({}, {}, {}), \
                        ({}, {}, {}))".format(md3Tag.rotationMatrix[0][0], \
                        md3Tag.rotationMatrix[0][1], \
                        md3Tag.rotationMatrix[0][2], \
                        md3Tag.rotationMatrix[1][0], \
                        md3Tag.rotationMatrix[1][1], \
                        md3Tag.rotationMatrix[1][2], \
                        md3Tag.rotationMatrix[2][0], \
                        md3Tag.rotationMatrix[2][1], \
                        md3Tag.rotationMatrix[2][2])
                    et.SubElement(treeMD3Tag, "rotationMatrix").text \
                    = rotationMatrixStr

            # surfaces
            treeSurfaces = et.SubElement(treeMD3File, "surfaces")

            for i in range(0, md3File.header.numSurfaces):

                md3Surface = md3File.surfaces[i]

                treeMD3Surface = et.SubElement(treeSurfaces, "MD3Surface", \
                    surfaceNum=str(i))

                # header
                treeHeader = et.SubElement(treeMD3Surface, "header")

                et.SubElement(treeHeader, "ident").text \
                = str(md3Surface.header.ident)

                et.SubElement(treeHeader, "name").text \
                = str(Util.cleanupString(md3Surface.header.name))

                et.SubElement(treeHeader, "flags").text \
                = str(md3Surface.header.flags)

                et.SubElement(treeHeader, "numFrames").text \
                = str(md3Surface.header.numFrames)

                et.SubElement(treeHeader, "numShaders").text \
                = str(md3Surface.header.numShaders)

                et.SubElement(treeHeader, "numVertices").text \
                = str(md3Surface.header.numVertices)

                et.SubElement(treeHeader, "numTriangles").text \
                = str(md3Surface.header.numTriangles)

                et.SubElement(treeHeader, "ofsTriangles").text \
                = str(md3Surface.header.ofsTriangles)

                et.SubElement(treeHeader, "ofsShaders").text \
                = str(md3Surface.header.ofsShaders)

                et.SubElement(treeHeader, "ofsTexCoords").text \
                = str(md3Surface.header.ofsTexCoords)

                et.SubElement(treeHeader, "ofsVertices").text \
                = str(md3Surface.header.ofsVertices)

                et.SubElement(treeHeader, "ofsEnd").text \
                = str(md3Surface.header.ofsEnd)

                # triangles
                treeTriangles = et.SubElement(treeMD3Surface, "triangles")

                for j in range(0, md3Surface.header.numTriangles):

                    md3Triangle = md3Surface.triangles[j]

                    treeMD3Triangle = et.SubElement(treeTriangles, \
                        "MD3Triangle")

                    et.SubElement(treeMD3Triangle, "indices").text \
                    = str(md3Triangle.indices)

                # shaders
                treeShaders = et.SubElement(treeMD3Surface, "shaders")

                for j in range(0, md3Surface.header.numShaders):

                    md3Shader = md3Surface.shaders[j]

                    treeMD3Shader = et.SubElement(treeShaders, \
                        "MD3Shader")

                    et.SubElement(treeMD3Shader, "name").text \
                    = str(Util.cleanupString(md3Shader.name))

                    et.SubElement(treeMD3Shader, "shaderIndex").text \
                    = str(md3Shader.shaderIndex)

                # texCoords
                treeTexCoords = et.SubElement(treeMD3Surface, "texCoords")

                for j in range(0, md3Surface.header.numVertices):

                    md3TexCoords = md3Surface.texCoords[j]

                    treeMD3TexCoords = et.SubElement(treeTexCoords, \
                        "MD3TexCoords")

                    et.SubElement(treeMD3TexCoords, "texCoords", \
                        vertexNum=str(j)).text \
                    = str(md3TexCoords.texCoords)

                # vertices
                treeVertices = et.SubElement(treeMD3Surface, "vertices")

                for j in range(frameStart, frameEnd):

                    frameVertices = md3Surface.vertices[j]

                    treeFrameVertices = et.SubElement(treeVertices, \
                        "frameVertices", frameNum=str(j))

                    for k in range(0, md3Surface.header.numVertices):

                        md3Vertex = frameVertices[k]

                        treeMD3Vertex = et.SubElement(treeFrameVertices, \
                            "MD3Vertex", vertexNum=str(k))

                        et.SubElement(treeMD3Vertex, "location").text \
                        = str(md3Vertex.location)

                        et.SubElement(treeMD3Vertex, "normal").text \
                        = str(md3Vertex.normal)

            tree = et.ElementTree(treeMD3File)
            tree.write(filePath)

        def writeMDC(mdcFile, filePath, frameRange=None):

            treeMDCFile = et.Element("MDCFile")

            # header
            treeHeader = et.SubElement(treeMDCFile, "header")

            treeMDCFileHeader = et.SubElement(treeHeader, "MDCFileHeader")

            et.SubElement(treeMDCFileHeader, "ident").text \
            = str(mdcFile.header.ident)

            et.SubElement(treeMDCFileHeader, "version").text \
            = str(mdcFile.header.version)

            et.SubElement(treeMDCFileHeader, "name").text = \
            str(Util.cleanupString(mdcFile.header.name))

            et.SubElement(treeMDCFileHeader, "flags").text \
            = str(mdcFile.header.version)

            et.SubElement(treeMDCFileHeader, "numFrames").text \
            = str(mdcFile.header.numFrames)

            et.SubElement(treeMDCFileHeader, "numTags").text \
            = str(mdcFile.header.numTags)

            et.SubElement(treeMDCFileHeader, "numSurfaces").text \
            = str(mdcFile.header.numSurfaces)

            et.SubElement(treeMDCFileHeader, "numSkins").text \
            = str(mdcFile.header.numSkins)

            et.SubElement(treeMDCFileHeader, "ofsFrameHeaders").text \
            = str(mdcFile.header.ofsFrameHeaders)

            et.SubElement(treeMDCFileHeader, "ofsTagHeaders").text \
            = str(mdcFile.header.ofsTagHeaders)

            et.SubElement(treeMDCFileHeader, "ofsTags").text \
            = str(mdcFile.header.ofsTags)

            et.SubElement(treeMDCFileHeader, "ofsSurfaces").text \
            = str(mdcFile.header.ofsSurfaces)

            et.SubElement(treeMDCFileHeader, "ofsEnd").text \
            = str(mdcFile.header.ofsEnd)

            # frameHeaders
            treeFrames = et.SubElement(treeMDCFile, "frameHeaders")

            for i in range(0, mdcFile.header.numFrames):

                mdcFrameHeader = mdcFile.frameHeaders[i]

                treeMDCFrameHeader \
                = et.SubElement(treeFrames, "MDCFrameHeader", frameNum=str(i))

                et.SubElement(treeMDCFrameHeader, "minBounds").text \
                = str(mdcFrameHeader.minBounds)

                et.SubElement(treeMDCFrameHeader, "maxBounds").text \
                = str(mdcFrameHeader.maxBounds)

                et.SubElement(treeMDCFrameHeader, "localOrigin").text \
                = str(mdcFrameHeader.localOrigin)

                et.SubElement(treeMDCFrameHeader, "radius").text \
                = str(mdcFrameHeader.radius)

                et.SubElement(treeMDCFrameHeader, "name").text \
                = str(Util.cleanupString(mdcFrameHeader.name))

            # tagHeaders
            treeTagHeaders = et.SubElement(treeMDCFile, "tagHeaders")

            for i in range(0, mdcFile.header.numTags):

                mdcTagHeader = mdcFile.tagHeaders[i]

                treeMDCTagHeader \
                = et.SubElement(treeTagHeaders, "MDCTagHeader", tagNum=str(i))

                et.SubElement(treeMDCTagHeader, "name").text \
                = str(Util.cleanupString(mdcTagHeader.name))

            # tags
            treeTags = et.SubElement(treeMDCFile, "tags")

            for i in range(0, mdcFile.header.numFrames):

                frameTags = mdcFile.tags[i]

                treeFrameTags = et.SubElement(treeTags, "frameTags", \
                    frameNum=str(i))

                for j in range(0, mdcFile.header.numTags):

                    mdcTag = frameTags[j]

                    treeMDCTag \
                    = et.SubElement(treeFrameTags, "MDCTag", tagNum=str(j))

                    et.SubElement(treeMDCTag, "location").text \
                    = str(mdcTag.location)

                    et.SubElement(treeMDCTag, "angles").text \
                    = str(mdcTag.angles)

            # surfaces
            treeSurfaces = et.SubElement(treeMDCFile, "surfaces")

            for i in range(0, mdcFile.header.numSurfaces):

                mdcSurface = mdcFile.surfaces[i]

                treeMDCSurface = et.SubElement(treeSurfaces, "MDCSurface", \
                    surfaceNum=str(i))

                # header
                treeHeader = et.SubElement(treeMDCSurface, "header")

                et.SubElement(treeHeader, "ident").text \
                = str(mdcSurface.header.ident)

                et.SubElement(treeHeader, "name").text \
                = str(Util.cleanupString(mdcSurface.header.name))

                et.SubElement(treeHeader, "flags").text \
                = str(mdcSurface.header.flags)

                et.SubElement(treeHeader, "numCompFrames").text \
                = str(mdcSurface.header.numCompFrames)

                et.SubElement(treeHeader, "numBaseFrames").text \
                = str(mdcSurface.header.numBaseFrames)

                et.SubElement(treeHeader, "numShaders").text \
                = str(mdcSurface.header.numShaders)

                et.SubElement(treeHeader, "numVertices").text \
                = str(mdcSurface.header.numVertices)

                et.SubElement(treeHeader, "numTriangles").text \
                = str(mdcSurface.header.numTriangles)

                et.SubElement(treeHeader, "ofsTriangles").text \
                = str(mdcSurface.header.ofsTriangles)

                et.SubElement(treeHeader, "ofsShaders").text \
                = str(mdcSurface.header.ofsShaders)

                et.SubElement(treeHeader, "ofsTexCoords").text \
                = str(mdcSurface.header.ofsTexCoords)

                et.SubElement(treeHeader, "ofsVerticesBase").text \
                = str(mdcSurface.header.ofsVerticesBase)

                et.SubElement(treeHeader, "ofsVerticesComp").text \
                = str(mdcSurface.header.ofsVerticesComp)

                et.SubElement(treeHeader, "ofsBaseFrameIndices").text \
                = str(mdcSurface.header.ofsBaseFrameIndices)

                et.SubElement(treeHeader, "ofsCompFrameIndices").text \
                = str(mdcSurface.header.ofsCompFrameIndices)

                et.SubElement(treeHeader, "ofsEnd").text \
                = str(mdcSurface.header.ofsEnd)

                # triangles
                treeTriangles = et.SubElement(treeMDCSurface, "triangles")

                for j in range(0, mdcSurface.header.numTriangles):

                    mdcTriangle = mdcSurface.triangles[j]

                    treeMDCTriangle = et.SubElement(treeTriangles, \
                        "MDCTriangle")

                    et.SubElement(treeMDCTriangle, "indices").text \
                    = str(mdcTriangle.indices)

                # shaders
                treeShaders = et.SubElement(treeMDCSurface, "shaders")

                for j in range(0, mdcSurface.header.numShaders):

                    mdcShader = mdcSurface.shaders[j]

                    treeMDCShader = et.SubElement(treeShaders, \
                        "MDCShader")

                    et.SubElement(treeMDCShader, "name").text \
                    = str(Util.cleanupString(mdcShader.name))

                    et.SubElement(treeMDCShader, "shaderIndex").text \
                    = str(mdcShader.shaderIndex)

                # texCoords
                treeTexCoords = et.SubElement(treeMDCSurface, "texCoords")

                for j in range(0, mdcSurface.header.numVertices):

                    mdcTexCoords = mdcSurface.texCoords[j]

                    treeMDCTexCoords = et.SubElement(treeTexCoords, \
                        "MDCTexCoords")

                    et.SubElement(treeMDCTexCoords, "texCoords", \
                        vertexNum=str(j)).text \
                    = str(mdcTexCoords.texCoords)

                # verticesBase
                treeVerticesBase = et.SubElement(treeMDCSurface, "verticesBase")

                for j in range(0, mdcSurface.header.numBaseFrames):

                    frameVertices = mdcSurface.verticesBase[j]

                    treeFrameVertices = et.SubElement(treeVerticesBase, \
                        "frameVertices", baseFrameNum=str(j))

                    for k in range(0, mdcSurface.header.numVertices):

                        mdcVertexBase = frameVertices[k]

                        treeMDCVertexBase = et.SubElement(treeFrameVertices, \
                            "MDCVertexBase", vertexNum=str(k))

                        et.SubElement(treeMDCVertexBase, "location").text \
                        = str(mdcVertexBase.location)

                        et.SubElement(treeMDCVertexBase, "normal").text \
                        = str(mdcVertexBase.normal)

                # verticesComp
                treeVerticesComp = et.SubElement(treeMDCSurface, "verticesComp")

                for j in range(0, mdcSurface.header.numCompFrames):

                    frameVertices = mdcSurface.verticesComp[j]

                    treeFrameVertices = et.SubElement(treeVerticesComp, \
                        "frameVertices", compFrameNum=str(j))

                    for k in range(0, mdcSurface.header.numVertices):

                        mdcVertexComp = frameVertices[k]

                        treeMDCVertexComp \
                        = et.SubElement(treeFrameVertices, \
                            "MDCVertexComp", vertexNum=str(k))

                        et.SubElement(treeMDCVertexComp, \
                            "offsetLocation") .text \
                        = str(mdcVertexComp.offsetLocation)

                        et.SubElement(treeMDCVertexComp, "normal") \
                        .text = str(mdcVertexComp.normal)

                # baseFrameIndices
                treeBaseFrameIndices = et.SubElement(treeMDCSurface, \
                    "baseFrameIndices")

                numFrames = mdcSurface.header.numCompFrames \
                    + mdcSurface.header.numBaseFrames
                for j in range(0, numFrames):

                    treeBaseFrameIndex = et.SubElement(treeBaseFrameIndices, \
                    "baseFrameIndex", frameNum=str(j)).text \
                    = str(mdcSurface.baseFrameIndices.indices[j])

                # compFrameIndices
                treeCompFrameIndices = et.SubElement(treeMDCSurface, \
                    "compFrameIndices")

                numFrames = mdcSurface.header.numCompFrames \
                    + mdcSurface.header.numBaseFrames
                for j in range(0, numFrames):

                    treeCompFrameIndex = et.SubElement(treeCompFrameIndices, \
                    "compFrameIndex", frameNum=str(j)).text \
                    = str(mdcSurface.compFrameIndices.indices[j])

            tree = et.ElementTree(treeMDCFile)
            tree.write(filePath)
