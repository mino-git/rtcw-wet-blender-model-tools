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

"""Reading, writing shape keys.
"""

import bpy
import mathutils

import rtcw_et_model_tools.blender.core.fcurve as fcurve_m


# =====================================
# READ
# =====================================

def read_shape_keys(blender_object, frame_start=0, frame_end=0):
    '''Read shape key from a blender object and convert list of tuples for
    locations and normals between the frame range.

    Args:

        blender_object
        frame_start
        frame_end

    Returns:

        (vertex_locations, vertex_normals)
    '''

    vertex_locations = []
    vertex_normals = []

    shape_key = blender_object.data.shape_keys
    if not shape_key:
        return (vertex_locations, vertex_normals)

    if not shape_key.animation_data:
        return (vertex_locations, vertex_normals)

    if not shape_key.animation_data.action:
        return (vertex_locations, vertex_normals)

    is_relative_shape_key = shape_key.use_relative
    if not is_relative_shape_key:

        dp_eval_time = "eval_time"
        action = shape_key.animation_data.action
        fcurve_eval_time = action.fcurves.find(dp_eval_time)

        if not fcurve_eval_time:
            return (vertex_locations, vertex_normals)

        num_vertices = len(blender_object.data.vertices)
        for _ in range(num_vertices):
            vertex_locations.append([])
            vertex_normals.append([])

        for num_frame in range(frame_start, frame_end + 1):

            eval_time = fcurve_eval_time.evaluate(num_frame)

            eval_1 = eval_time - (eval_time % 10)
            eval_2 = eval_1 + 10

            percent_eval_1 = (eval_2 - eval_time) / (eval_2 - eval_1)
            percent_eval_2 = 1 - percent_eval_1

            num_key_blocks = len(shape_key.key_blocks)

            num_block_1 = int(eval_time / 10)
            num_block_2 = num_block_1 + 1

            if num_block_2 < num_key_blocks:

                key_block_1 = shape_key.key_blocks[num_block_1]
                key_block_2 = shape_key.key_blocks[num_block_2]

                normals_1 = key_block_1.normals_vertex_get()
                normals_2 = key_block_2.normals_vertex_get()

                for num_vertex in range(num_vertices):

                    # location
                    location_1 = key_block_1.data[num_vertex].co
                    location_2 = key_block_2.data[num_vertex].co

                    location = percent_eval_1 * location_1 + \
                               percent_eval_2 * location_2
                    vertex_locations[num_vertex].append(location)

                    # normal
                    n1_x = normals_1[num_vertex*3]
                    n1_y = normals_1[num_vertex*3+1]
                    n1_z = normals_1[num_vertex*3+2]

                    n2_x = normals_2[num_vertex*3]
                    n2_y = normals_2[num_vertex*3+1]
                    n2_z = normals_2[num_vertex*3+2]

                    n1 = mathutils.Vector((n1_x, n1_y, n1_z))
                    n2 = mathutils.Vector((n2_x, n2_y, n2_z))

                    normal = percent_eval_1 * n1 + percent_eval_2 * n2
                    normal.normalize()
                    vertex_normals[num_vertex].append(normal)

            else:

                key_block = shape_key.key_blocks[-1]

                normals_1 = key_block.normals_vertex_get()

                for num_vertex in range(num_vertices):

                    # location
                    location = key_block.data[num_vertex].co
                    vertex_locations[num_vertex].append(location)

                    # normal
                    nx = normals_1[num_vertex*3]
                    ny = normals_1[num_vertex*3 + 1]
                    nz = normals_1[num_vertex*3 + 2]

                    normal = mathutils.Vector((nx, ny, nz))
                    normal.normalize()
                    vertex_normals[num_vertex].append(normal)

    else:  # relative shape key

        pass  # TODO not supported yet

    return (vertex_locations, vertex_normals)

# =====================================
# WRITE
# =====================================

def write_shape_keys(blender_object, vertex_locations, vertex_normals):

    num_vertices = len(vertex_locations)
    for _ in range(num_vertices):

        for num_frame in range(len(vertex_locations[_])):

            shape_key = blender_object.shape_key_add(name="Frame", from_mix=False)

            for num_vertex in range(num_vertices):

                x = vertex_locations[num_vertex][num_frame][0]
                y = vertex_locations[num_vertex][num_frame][1]
                z = vertex_locations[num_vertex][num_frame][2]
                shape_key.data[num_vertex].co = (x, y, z)

        break

    if blender_object.data.shape_keys:

        blender_object.data.shape_keys.use_relative = False
        blender_object.active_shape_key_index = 0

        num_frames = len(vertex_locations[0])
        for num_frame in range(num_frames):

            blender_object.data.shape_keys.eval_time = 10.0 * num_frame
            blender_object.data.shape_keys. \
                keyframe_insert('eval_time', frame = num_frame)
