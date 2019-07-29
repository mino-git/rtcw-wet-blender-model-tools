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

"""Blender utils.
"""

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.blender.core.fcurve as fcurve_m
import rtcw_et_model_tools.common.reporter as reporter_m

def read_object_space_lrs(blender_object, frame_start = 0, frame_end = 0,
                          read_locs = True, read_rots = True,
                          read_scales = True):
    """Read object space location, rotation and scale values of an object. If
    not animated, return static values across frames. The returned values are
    assumed to be given without constraints, parents or modifiers applied.

    Args:

        blender_object
        frame_start
        frame_end
        read_locs
        read_rots
        read_scales

    Returns:

        (locations, rotations, scales)
    """

    # find out if its animated by searching for the fcurve of an action
    # TODO nla
    fcurves = None
    if blender_object.animation_data:

        action = blender_object.animation_data.action
        if action:

            fcurves = action.fcurves
            if not fcurves:

                reporter_m.warning("Action found with no fcurves on blender"
                                   " object '{}'"
                                   .format(blender_object.name))

        else:

            reporter_m.warning("Animation data with no action found on"
                               " blender object '{}'"
                               .format(blender_object.name))

    locations = []
    rotations = []
    scales = []
    if fcurves:

        # locations
        if read_locs:

            data_path = fcurve_m.DP_LOCATION
            locations = fcurve_m.read_locations(fcurves,
                                                data_path,
                                                frame_start,
                                                frame_end)

        # rotations
        if read_rots:

            rotation_mode = blender_object.rotation_mode

            if rotation_mode == 'XYZ' or rotation_mode == 'XZY' or \
               rotation_mode == 'YXZ' or rotation_mode == 'YZX' or \
               rotation_mode == 'ZXY' or rotation_mode == 'ZYX':

                data_path = fcurve_m.DP_EULER
                eulers = fcurve_m.read_eulers(fcurves,
                                              data_path,
                                              rotation_mode,
                                              frame_start,
                                              frame_end)

                if eulers:

                    for euler in eulers:

                        rotation = euler.to_matrix()
                        rotations.append(rotation)

            elif rotation_mode == 'AXIS_ANGLE':

                data_path = fcurve_m.DP_AXIS_ANGLE
                axis_angles = fcurve_m.read_axis_angles(fcurves,
                                                        data_path,
                                                        frame_start,
                                                        frame_end)

                if axis_angles:

                    for axis_angle in axis_angles:

                        rotation = axis_angle_to_matrix(axis_angle)
                        rotations.append(rotation)

            elif rotation_mode == 'QUATERNION':

                data_path = fcurve_m.DP_QUATERNION
                quaternions = fcurve_m.read_quaternions(fcurves,
                                                        data_path,
                                                        frame_start,
                                                        frame_end)

                if quaternions:

                    for quaternion in quaternions:

                        rotation = quaternion.to_matrix()
                        rotations.append(rotation)

            else:

                exception_string = "Unknown rotation mode found on blender" \
                                   " object '{}'".format(blender_object.name)
                raise Exception(exception_string)

        # scales
        if read_scales:

            data_path = fcurve_m.DP_SCALE
            scales = fcurve_m.read_scales(fcurves,
                                          data_path,
                                          frame_start,
                                          frame_end)

    if not locations and read_locs:

        loc, _, _ = blender_object.matrix_basis.decompose()
        locations = [loc] * (frame_end + 1 - frame_start)

    if not rotations and read_rots:

        _, rot, _ = blender_object.matrix_basis.decompose()
        rotations = [rot] * (frame_end + 1 - frame_start)

    if not scales and read_scales:

        _, _, scale = blender_object.matrix_basis.decompose()
        scales = [scale] * (frame_end + 1 - frame_start)

    return (locations, rotations, scales)

def write_object_space_lrs(blender_object, locations = None, rotations = None,
                           scales = None, frame_start = 0):
    """Write object space location, rotation and scale values of an object. The
    values are assumed to be given without constraints, parents or modifiers
    applied.

    Args:

        blender_object
        locations
        rotations
        scales
        frame_start
    """

    # ensure there is animation data to write to
    needs_animation_data = False
    if locations and len(locations) > 1:
            needs_animation_data = True
    if rotations and len(rotations) > 1:
            needs_animation_data = True
    if scales and len(scales) > 1:
            needs_animation_data = True

    if needs_animation_data:

        if not blender_object.animation_data:
            blender_object.animation_data_create()

        if not blender_object.animation_data.action:
            blender_object.animation_data.action = \
                bpy.data.actions.new(name=blender_object.name)

        # TODO check for fcurves?

    # locations
    if locations:

        num_frames = len(locations)
        if num_frames > 1:

            fcurves = blender_object.animation_data.action.fcurves
            data_path = fcurve_m.DP_LOCATION
            fcurve_m.write_locations(fcurves,
                                     data_path,
                                     locations,
                                     frame_start)

        elif num_frames == 1:

            blender_object.matrix_basis.translation = locations[0]

        else:

            pass  # nothing to write

    if rotations:

        num_frames = len(rotations)
        if num_frames > 1:

            fcurves = blender_object.animation_data.action.fcurves
            data_path = fcurve_m.DP_QUATERNION

            quaternions = []
            for rotation in rotations:

                quaternion = rotation.to_quaternion()
                quaternions.append(quaternion)

            fcurve_m.write_quaternions(fcurves,
                                       data_path,
                                       quaternions,
                                       frame_start)

        elif num_frames == 1:

            rotation_matrix = rotations[0]
            matrix_basis = blender_object.matrix_basis
            matrix_basis[0][0:3] = rotation_matrix[0][0:3]
            matrix_basis[1][0:3] = rotation_matrix[1][0:3]
            matrix_basis[2][0:3] = rotation_matrix[2][0:3]

        else:

            pass  # nothing to write

    if scales:

        num_frames = len(scales)
        if num_frames > 1:

            fcurves = blender_object.animation_data.action.fcurves
            data_path = fcurve_m.DP_SCALE
            fcurve_m.write_scales(fcurves, data_path, scales, frame_start)

        elif num_frames == 1:

            scale = scales[0]
            matrix_basis = blender_object.matrix_basis
            matrix_basis[0][0] = scale[0]
            matrix_basis[1][1] = scale[1]
            matrix_basis[2][2] = scale[2]

        else:

            pass  # nothing to write

def matrix_to_axis_angle(matrix):
    """TODO
    """

    axis_angle = None

    if True:
        raise Exception("Matrix to axis angle conversion not supported")

    return axis_angle

def axis_angle_to_matrix(axis_angle):
    """TODO
    """

    matrix = None

    if True:
        raise Exception("Axis angle to matrix conversion not supported")

    return matrix


# calculates a vector (x, y, z) orthogonal to v
def getOrthogonal(v):
    """TODO
    """

    x = 0
    y = 0
    z = 0

    if v[0] == 0: # x-axis is 0 => yz-plane

        x = 1
        y = 0
        z = 0

    else:

        if v[1] == 0: # y-axis is 0 => xz-plane

            x = 0
            y = 1
            z = 0

        else:

            if v[2] == 0: # z-axis is 0 => xy-plane

                x = 0
                y = 0
                z = 1

            else:

                # x*v0 + y*v1 + z*v2 = 0
                x = 1 / v[0]
                y = 1 / v[1]
                z = -((1/v[2]) * 2)

    return (x, y, z)

def draw_normals_in_frame(mdi_vertices, num_frame, collection,
                          mdi_skeleton = None):
    """TODO
    """

    for mdi_vertex in mdi_vertices:

        if isinstance(mdi_vertex, mdi_m.MDIMorphVertex):

            empty_object = bpy.data.objects.new("empty", None)
            empty_object.name = "vertex_normal"
            empty_object.empty_display_type = 'SINGLE_ARROW'
            empty_object.rotation_mode = 'QUATERNION'

            b3 = mdi_vertex.normals[num_frame]

            # find orthogonal basis vectors
            b2 = mathutils.Vector(getOrthogonal(b3))
            b1 = b2.cross(b3)

            # normalize
            b1.normalize()
            b2.normalize()
            b3.normalize()

            # build transformation matrix
            basis = mathutils.Matrix()
            basis[0].xyz = b1
            basis[1].xyz = b2
            basis[2].xyz = b3
            basis.transpose()
            basis.translation = mdi_vertex.locations[num_frame]

            empty_object.matrix_world = basis

            collection.objects.link(empty_object)

        elif isinstance(mdi_vertex, mdi_m.MDIRiggedVertex):

            empty_object = bpy.data.objects.new("empty", None)
            empty_object.name = "Normal"
            empty_object.empty_display_type = 'SINGLE_ARROW'
            empty_object.rotation_mode = 'QUATERNION'

            b3 = mdi_vertex.calc_normal_ms(mdi_skeleton, num_frame)

            # find orthogonal basis vectors
            b2 = mathutils.Vector(getOrthogonal(b3))
            b1 = b2.cross(b3)

            # normalize
            b1.normalize()
            b2.normalize()
            b3.normalize()

            # build transformation matrix
            basis = mathutils.Matrix()
            basis[0].xyz = b1
            basis[1].xyz = b2
            basis[2].xyz = b3
            basis.transpose()
            basis.translation = mdi_vertex.calc_location_ms(mdi_skeleton,
                                                            num_frame)

            empty_object.matrix_world = basis

            collection.objects.link(empty_object)

        else:

            pass  # TODO

def get_verts_from_bounds(min_bound, max_bound):
    """TODO
    """

    vertices = []

    v0 = (min_bound[0], min_bound[1], min_bound[2])
    v1 = (min_bound[0], max_bound[1], min_bound[2])
    v2 = (min_bound[0], min_bound[1], max_bound[2])
    v3 = (min_bound[0], max_bound[1], max_bound[2])

    v4 = (max_bound[0], max_bound[1], max_bound[2])
    v5 = (max_bound[0], min_bound[1], max_bound[2])
    v6 = (max_bound[0], max_bound[1], min_bound[2])
    v7 = (max_bound[0], min_bound[1], min_bound[2])

    vertices.append(v0)
    vertices.append(v1)
    vertices.append(v2)
    vertices.append(v3)
    vertices.append(v4)
    vertices.append(v5)
    vertices.append(v6)
    vertices.append(v7)

    return vertices

def draw_bounding_volume(mdi_bounding_volume):
    """TODO
    """

    min_bound = mdi_bounding_volume.aabbs[0].min_bound
    max_bound = mdi_bounding_volume.aabbs[0].max_bound

    vertices = get_verts_from_bounds(min_bound, max_bound)

    # faces
    faces = []

    f1 = (0, 1, 3, 2)
    f2 = (4, 5, 7, 6)

    f3 = (2, 3, 4, 5)
    f4 = (0, 1, 6, 7)

    f5 = (0, 2, 5, 7)
    f6 = (1, 3, 4, 6)

    faces.append(f1)
    faces.append(f2)
    faces.append(f3)
    faces.append(f4)
    faces.append(f5)
    faces.append(f6)

    name = "BoundingBox"
    mesh = bpy.data.meshes.new(name)
    mesh_object = bpy.data.objects.new(name, mesh)
    mesh_object.display_type = 'WIRE'

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.validate(verbose=True)

    active_collection = \
        bpy.context.view_layer.active_layer_collection.collection
    active_collection.objects.link(mesh_object)

    num_frames = len(mdi_bounding_volume.aabbs)

    for num_frame in range(num_frames):

        shape_key = mesh_object.shape_key_add(name="Frame", from_mix=False)

        min_bound = mdi_bounding_volume.aabbs[num_frame].min_bound
        max_bound = mdi_bounding_volume.aabbs[num_frame].max_bound
        vertices = get_verts_from_bounds(min_bound, max_bound)

        for num_vertex, vertex in enumerate(vertices):

            x = vertex[0]
            y = vertex[1]
            z = vertex[2]
            shape_key.data[num_vertex].co = (x, y, z)

    mesh_object.data.shape_keys.use_relative = False

    for num_frame in range(num_frames):

        mesh_object.data.shape_keys.eval_time = 10.0 * num_frame
        mesh_object.data.shape_keys. \
            keyframe_insert('eval_time', frame = num_frame)

    mesh_object.data.update()
