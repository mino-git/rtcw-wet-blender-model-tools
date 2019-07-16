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

"""Reading, writing and converting a UV map.
"""

import bpy

import rtcw_et_model_tools.mdi.mdi as mdi_m


def test(mesh_object):

    if mesh_object.name == "eye1":

        for i, polygon in enumerate(mesh_object.data.polygons):

            print('polygon: ', i)

            for i1, loopindex in enumerate(polygon.loop_indices):
                print('meshloop: ', i1, ' index: ',loopindex)

                meshloop = mesh_object.data.loops[i1]
                meshvertex = mesh_object.data.vertices[meshloop.vertex_index]
                meshuvloop = mesh_object.data.uv_layers.active.data[loopindex]

                print('meshuvloop coords: ', meshuvloop.uv)


def read(mesh_object):
    """Read UV map.

    Args:
        TODO
    """

    if len(mesh_object.data.uv_layers) > 1:
        pass # TODO

    uv_layer = mesh_object.data.uv_layers.active

    if uv_layer == None:
        return None # TODO

    # read in all data into tmp_uvs
    tmp_uvs = []
    for _ in range(len(mesh_object.data.vertices)):
        tmp_uvs.append([])

    for polygon in mesh_object.data.polygons:

        for loop_index in polygon.loop_indices:

            loop = mesh_object.data.loops[loop_index]

            loop_index = uv_layer.data[loop.index]
            vertex_index = loop.vertex_index
            uv_coordinates = uv_layer.data[loop.index].uv

            tmp_uvs[vertex_index].append(uv_coordinates)

    # check if data is bijective
    uv_map_is_bijective = True
    for vertex_index, vertex_mappings in enumerate(tmp_uvs):

        if len(vertex_mappings) == 0:
            uv_map_is_bijective = False
            break

        sample_mapping = vertex_mappings[0]
        for mapping in vertex_mappings:
            if mapping != sample_mapping:
                uv_map_is_bijective = False

    if uv_map_is_bijective:

        mdi_uv_map = mdi_m.MDIUVMapBijective()

        for uv in tmp_uvs:

            u = uv[0][0]
            v = uv[0][1]
            mdi_uv = mdi_m.MDIUV(u, v)
            mdi_uv_map.uvs.append(mdi_uv)

    else:

        mdi_uv_map = mdi_m.MDIUVMapSurjective()

    return mdi_uv_map

#
# def read(mesh_object):
#     """Read UV map.

#     Args:

#         TODO
#     """

#     # TODO what if not present

#     UVMap.test(mesh_object)

#     if len(mesh_object.data.uv_layers) > 1:
#         pass # TODO

#     uv_layer = mesh_object.data.uv_layers.active

#     if uv_layer == None:
#         return None # TODO

#     # # read in all data into tmp_uvs
#     # tmp_uvs = []
#     # for _ in range(len(mesh_object.data.vertices)):
#     #     tmp_uvs.append([])

#     # for polygon in mesh_object.data.polygons:

#     #     for loop_index in polygon.loop_indices:

#     #         loop = mesh_object.data.loops[loop_index]

#     #         loop_index = uv_layer.data[loop.index]
#     #         vertex_index = loop.vertex_index
#     #         uv_coordinates = uv_layer.data[loop.index].uv

#     #         tmp_uvs[vertex_index].append(uv_coordinates)

#     uv_coordinates = []
#     for _ in range(len(mesh_object.data.vertices)):
#         uv_coordinates.append([])

#     for polygon in mesh_object.data.polygons:

#         for loop_index in polygon.loop_indices:

#             loop = mesh_object.data.loops[loop_index]

#             loop_index = uv_layer.data[loop.index]
#             vertex_index = loop.vertex_index
#             coordinates = uv_layer.data[loop.index].uv

#             uv_coordinates[vertex_index].append(coordinates)

#     # check if data is bijective
#     uv_map_is_bijective = True
#     for vertex_index, vertex_mappings in enumerate(uv_coordinates):

#         if len(vertex_mappings) == 0:
#             uv_map_is_bijective = False
#             break

#         sample_mapping = vertex_mappings[0]
#         for mapping in vertex_mappings:
#             if mapping != sample_mapping:
#                 uv_map_is_bijective = False

#     if uv_map_is_bijective:

#         mdi_uv_map = mdi_m.MDIUVMapBijective()

#         for uv in uv_coordinates:

#             u = uv[0][0]
#             v = uv[0][1]
#             mdi_uv = mdi_m.MDIUV(u, v)
#             mdi_uv_map.uvs.append(mdi_uv)

#     else:

#         mdi_uv_map = mdi_m.MDIUVMapSurjective()

#         for uvs in uv_coordinates:

#             mdi_uvs = []

#             for uv in uvs:

#                 u = uv[0]
#                 v = uv[1]
#                 mdi_uv = mdi_m.MDIUV(u, v)
#                 mdi_uvs.append(mdi_uv)

#             mdi_uv_map.uvs.append(mdi_uvs)

#     return mdi_uv_map


def write(mdi_uv_map, mesh_object):
    """Write UV map.

    Args:

        mdi_uv_map
        mesh_object
    """

    if isinstance(mdi_uv_map, mdi_m.MDIUVMapSurjective):

        pass  # TODO

    elif isinstance(mdi_uv_map, mdi_m.MDIUVMapBijective):

        mesh_object.data.uv_layers.new(name="UVMap")

        for polygon in mesh_object.data.polygons:

            for loop_index in \
                range(polygon.loop_start,
                        polygon.loop_start + polygon.loop_total):

                vertex_index = \
                    mesh_object.data.loops[loop_index].vertex_index

                mesh_object.data.uv_layers['UVMap'].data[loop_index].uv = \
                    (mdi_uv_map.uvs[vertex_index].u,
                        mdi_uv_map.uvs[vertex_index].v)

    else:

        pass  # TODO
