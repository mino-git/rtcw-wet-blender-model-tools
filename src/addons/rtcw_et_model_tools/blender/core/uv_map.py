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
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.common.reporter as reporter_m


def create_zero_map(mesh_object):

    mdi_uv_map = mdi_m.MDIUVMapBijective()

    for _ in range(len(mesh_object.data.vertices)):

        u = 0.0
        v = 0.0
        mdi_uv = mdi_m.MDIUV(u, v)
        mdi_uv_map.uvs.append(mdi_uv)

    return mdi_uv_map

# =====================================
# READ
# =====================================

def read(mesh_object):
    """Read UV map.

    Args:
        TODO
    """

    if len(mesh_object.data.uv_layers) > 1:
        reporter_m.warning("Found multiple uv maps. Picking active one.")

    uv_layer = mesh_object.data.uv_layers.active
    if not uv_layer:

        reporter_m.warning("UV map not found. Defaulting to zero map")
        mdi_uv_map_bijective = create_zero_map(mesh_object)
        return mdi_uv_map_bijective

    num_vertices = len(mesh_object.data.vertices)
    mdi_uv_map_surjective = mdi_m.MDIUVMapSurjective(num_vertices)

    for polygon_index, polygon in enumerate(mesh_object.data.polygons):

        for loop_index in polygon.loop_indices:

            vertex_index = mesh_object.data.loops[loop_index].vertex_index
            uv_coordinates = uv_layer.data[loop_index].uv

            mdi_uv_map_surjective.add(vertex_index,
                                      uv_coordinates,
                                      polygon_index)

    # find unmapped vertices
    for num_vertex, uvs in enumerate(mdi_uv_map_surjective.uvs):

        if not uvs:

            reporter_m.warning("Found unmapped vertex: num_vertex='{}',"
                                " mesh='{}'."
                                .format(num_vertex, mesh_object.name))

    return mdi_uv_map_surjective

# =====================================
# WRITE
# =====================================

def write(mdi_uv_map, mesh_object):
    """Write UV map.

    Args:

        mdi_uv_map
        mesh_object
    """

    if isinstance(mdi_uv_map, mdi_m.MDIUVMapSurjective):

        raise Exception("Surjective UV map not supported")

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

        raise TypeError("Unknown UV map type")
