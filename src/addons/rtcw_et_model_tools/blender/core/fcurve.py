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

"""Reading, writing fcurves.
"""

import bpy
import mathutils

import rtcw_et_model_tools.blender.util as blender_util_m  # TODO remove
import rtcw_et_model_tools.common.reporter as reporter_m


# =====================================
# DATAPATHS
# =====================================

DP_LOCATION = 'location'
DP_QUATERNION = 'rotation_quaternion'
DP_EULER = 'rotation_euler'
DP_AXIS_ANGLE = 'rotation_axis_angle'
DP_SCALE = 'scale'

DP_BONE_LOCATION = 'pose.bones["{}"].location'
DP_BONE_QUATERNION = 'pose.bones["{}"].rotation_quaternion'
DP_BONE_EULER = 'pose.bones["{}"].rotation_euler'
DP_BONE_AXIS_ANGLE = 'pose.bones["{}"].rotation_axis_angle'
DP_BONE_SCALE = 'pose.bones["{}"].scale'

# =====================================
# READ
# =====================================

def read_locations(fcurves, data_path, frame_start, frame_end):
    """Read fcurve location values across frames.

    Args:

        fcurves
        data_path
        frame_start
        frame_end

    Returns:

        locations (list<mathutils.Vector>): location values per frame.
    """

    fcurve_x = fcurves.find(data_path, index=0)
    fcurve_y = fcurves.find(data_path, index=1)
    fcurve_z = fcurves.find(data_path, index=2)

    if not fcurve_x or not fcurve_y or not fcurve_z:

        if fcurve_x or fcurve_y or fcurve_z:

            reporter_m.warning("Location fcurve animation data not used. Make"
                               " sure to animate all values x, y, z. Single"
                               " values are not supported.")

        return None

    locations = []
    for num_frame in range(frame_start, frame_end + 1):

        x = fcurve_x.evaluate(num_frame)
        y = fcurve_y.evaluate(num_frame)
        z = fcurve_z.evaluate(num_frame)

        location = mathutils.Vector((x, y, z))
        locations.append(location)

    return locations

def read_quaternions(fcurves, data_path, frame_start, frame_end):
    """Read fcurve quaternion values across frames.

    Args:

        fcurves
        data_path
        frame_start
        frame_end

    Returns:

        quaternions (list<mathutils.Quaternion>): quaternion values per frame.
    """

    fcurve_w = fcurves.find(data_path, index=0)
    fcurve_x = fcurves.find(data_path, index=1)
    fcurve_y = fcurves.find(data_path, index=2)
    fcurve_z = fcurves.find(data_path, index=3)

    if not fcurve_w or not fcurve_x or not fcurve_y or not fcurve_z:

        if fcurve_w or fcurve_x or fcurve_y or fcurve_z:

            reporter_m.warning("Quaternion fcurve animation data not used."
                               " Make sure to animate all values w, x, y, z."
                               " Single values are not supported.")

        return None

    quaternions = []
    for num_frame in range(frame_start, frame_end + 1):

        qw = fcurve_w.evaluate(num_frame)
        qx = fcurve_x.evaluate(num_frame)
        qy = fcurve_y.evaluate(num_frame)
        qz = fcurve_z.evaluate(num_frame)

        quaternion = mathutils.Quaternion((qw, qx, qy, qz))
        quaternions.append(quaternion)

    return quaternions

def read_eulers(fcurves, data_path, rotation_mode, frame_start, frame_end):
    """Read fcurve euler values across frames.

    Args:

        fcurves
        data_path
        rotation_mode
        frame_start
        frame_end

    Returns:

        eulers (list<mathutils.Euler>): euler values per frame.
    """

    fcurve_x = fcurves.find(data_path, index=0)
    fcurve_y = fcurves.find(data_path, index=1)
    fcurve_z = fcurves.find(data_path, index=2)

    if not fcurve_x or not fcurve_y or not fcurve_z:

        if fcurve_x or fcurve_y or fcurve_z:

            reporter_m.warning("Euler fcurve animation data not used. Make"
                               " sure to animate all values x, y, z. Single"
                               " values are not supported.")

        return None

    eulers = []
    for num_frame in range(frame_start, frame_end + 1):

        ex = fcurve_x.evaluate(num_frame)
        ey = fcurve_y.evaluate(num_frame)
        ez = fcurve_z.evaluate(num_frame)

        euler = mathutils.Euler((ex, ey, ez), rotation_mode)
        eulers.append(euler)

    return eulers

def read_axis_angles(fcurves, data_path, frame_start, frame_end):
    """Read fcurve axis angle values across frames.

    Args:

        fcurves
        data_path
        frame_start
        frame_end

    Returns:

        axis_angles (list<mathutils.Vector>): axis angle values per frame.
    """

    fcurve_a = fcurves.find(data_path, index=0)
    fcurve_x = fcurves.find(data_path, index=1)
    fcurve_y = fcurves.find(data_path, index=2)
    fcurve_z = fcurves.find(data_path, index=3)

    if not fcurve_a or not fcurve_x or not fcurve_y or not fcurve_z:

        if fcurve_a or fcurve_x or fcurve_y or fcurve_z:

            reporter_m.warning("Axis angle fcurve animation data not used."
                               " Make sure to animate all values x, y, z."
                               " Single values are not supported.")

        return None

    axis_angles = []
    for num_frame in range(frame_start, frame_end + 1):

        aa = fcurve_a.evaluate(num_frame)
        ax = fcurve_x.evaluate(num_frame)
        ay = fcurve_y.evaluate(num_frame)
        az = fcurve_z.evaluate(num_frame)

        axis_angle = mathutils.Vector((aa, ax, ay, az))
        axis_angles.append(axis_angle)

    return axis_angles

def read_scales(fcurves, data_path, frame_start, frame_end):
    """Read fcurve scale values across frames.

    Args:

        fcurves
        data_path
        frame_start
        frame_end

    Returns:

        scales (list<mathutils.Vector>): scale values per frame.
    """

    fcurve_x = fcurves.find(data_path, index=0)
    fcurve_y = fcurves.find(data_path, index=1)
    fcurve_z = fcurves.find(data_path, index=2)

    if not fcurve_x or not fcurve_y or not fcurve_z:

        if fcurve_x or fcurve_y or fcurve_z:

            reporter_m.warning("Scale fcurve animation data not used."
                               " Make sure to animate all values x, y, z."
                               " Single values are not supported.")

        return None

    scales = []
    for num_frame in range(frame_start, frame_end + 1):

        x = fcurve_x.evaluate(num_frame)
        y = fcurve_y.evaluate(num_frame)
        z = fcurve_z.evaluate(num_frame)

        scale = mathutils.Vector((x, y, z))
        scales.append(scale)

    return scales

def read_rotation_matrices(fcurves, rotation_mode, frame_start, frame_end,
                           bone_name = None):
    """Convencience function. Reads fcurve rotation matrix values across
    frames.

    Args:

        fcurves
        rotation_mode
        frame_start
        frame_end
        bone_name

    Returns:

        matrices (list<mathutils.Matrix>): rotation matrix values per frame.
    """

    rotations = []

    if rotation_mode == 'XYZ' or rotation_mode == 'XZY' or \
       rotation_mode == 'YXZ' or rotation_mode == 'YZX' or \
       rotation_mode == 'ZXY' or rotation_mode == 'ZYX':

        if bone_name:
            data_path = DP_BONE_EULER.format(bone_name)
        else:
            data_path = DP_EULER

        eulers = read_eulers(fcurves,
                             data_path,
                             rotation_mode,
                             frame_start,
                             frame_end)

        if eulers:

            for euler in eulers:

                rotation = euler.to_matrix()
                rotations.append(rotation)

    elif rotation_mode == 'AXIS_ANGLE':

        if bone_name:
            data_path = DP_BONE_AXIS_ANGLE.format(bone_name)
        else:
            data_path = DP_AXIS_ANGLE.format

        axis_angles = read_axis_angles(fcurves,
                                       data_path,
                                       frame_start,
                                       frame_end)

        if axis_angles:

            for axis_angle in axis_angles:

                rotation = blender_util_m.axis_angle_to_matrix(axis_angle)
                rotations.append(rotation)

    elif rotation_mode == 'QUATERNION':

        if bone_name:
            data_path = DP_BONE_QUATERNION.format(bone_name)
        else:
            data_path = DP_QUATERNION

        quaternions = read_quaternions(fcurves,
                                       data_path,
                                       frame_start,
                                       frame_end)

        if quaternions:

            for quaternion in quaternions:

                rotation = quaternion.to_matrix()
                rotations.append(rotation)

    else:

        exception_string = "Unknown rotation mode found"
        raise Exception(exception_string)

    return rotations

# =====================================
# WRITE
# =====================================

def write_locations(fcurves, data_path, locations, frame_start = 0):
    """Write fcurve location values across frames. Location values are assumed
    to be sequential in the number of frames (step size 1).

    Args:

        fcurves
        data_path
        locations
        frame_start
    """

    fcurve_x = fcurves.new(data_path=data_path, index=0)
    fcurve_y = fcurves.new(data_path=data_path, index=1)
    fcurve_z = fcurves.new(data_path=data_path, index=2)

    frame_len = len(locations)

    fcurve_x.keyframe_points.add(count=frame_len)
    fcurve_y.keyframe_points.add(count=frame_len)
    fcurve_z.keyframe_points.add(count=frame_len)

    for num_frame, location in enumerate(locations, frame_start):

        fcurve_x.keyframe_points[num_frame].co = num_frame, location.x
        fcurve_y.keyframe_points[num_frame].co = num_frame, location.y
        fcurve_z.keyframe_points[num_frame].co = num_frame, location.z

def write_quaternions(fcurves, data_path, quaternions, frame_start = 0):
    """Write fcurve quaternion values across frames. Quaternion values are
    assumed to be sequential in the number of frames (step size 1).

    Args:

        fcurves
        data_path
        quaternions
        frame_start
    """

    fcurve_w = fcurves.new(data_path=data_path, index=0)
    fcurve_x = fcurves.new(data_path=data_path, index=1)
    fcurve_y = fcurves.new(data_path=data_path, index=2)
    fcurve_z = fcurves.new(data_path=data_path, index=3)

    frame_len = len(quaternions)

    fcurve_w.keyframe_points.add(count=frame_len)
    fcurve_x.keyframe_points.add(count=frame_len)
    fcurve_z.keyframe_points.add(count=frame_len)
    fcurve_y.keyframe_points.add(count=frame_len)

    for num_frame, quaternion in enumerate(quaternions, frame_start):

        fcurve_w.keyframe_points[num_frame].co = num_frame, quaternion.w
        fcurve_x.keyframe_points[num_frame].co = num_frame, quaternion.x
        fcurve_y.keyframe_points[num_frame].co = num_frame, quaternion.y
        fcurve_z.keyframe_points[num_frame].co = num_frame, quaternion.z

def write_eulers(fcurves, data_path, eulers, frame_start = 0):
    """Write fcurve euler values across frames. Euler values are
    assumed to be sequential in the number of frames (step size 1).

    Args:

        fcurves
        data_path
        eulers
        frame_start
    """

    fcurve_x = fcurves.new(data_path=data_path, index=0)
    fcurve_y = fcurves.new(data_path=data_path, index=1)
    fcurve_z = fcurves.new(data_path=data_path, index=2)

    frame_len = len(eulers)

    fcurve_x.keyframe_points.add(count=frame_len)
    fcurve_z.keyframe_points.add(count=frame_len)
    fcurve_y.keyframe_points.add(count=frame_len)

    for num_frame, euler in enumerate(eulers, frame_start):

        fcurve_x.keyframe_points[num_frame].co = num_frame, euler.x
        fcurve_y.keyframe_points[num_frame].co = num_frame, euler.y
        fcurve_z.keyframe_points[num_frame].co = num_frame, euler.z

def write_axis_angles(fcurves, data_path, axis_angles, frame_start = 0):
    """Write fcurve axis angle values across frames. Axis angle values are
    assumed to be sequential in the number of frames (step size 1).

    Args:

        fcurves
        data_path
        axis_angles
        frame_start
    """

    fcurve_a = fcurves.new(data_path=data_path, index=0)
    fcurve_x = fcurves.new(data_path=data_path, index=1)
    fcurve_y = fcurves.new(data_path=data_path, index=2)
    fcurve_z = fcurves.new(data_path=data_path, index=3)

    frame_len = len(axis_angles)

    fcurve_a.keyframe_points.add(count=frame_len)
    fcurve_x.keyframe_points.add(count=frame_len)
    fcurve_z.keyframe_points.add(count=frame_len)
    fcurve_y.keyframe_points.add(count=frame_len)

    for num_frame, axis_angle in enumerate(axis_angles, frame_start):

        fcurve_a.keyframe_points[num_frame].co = num_frame, axis_angle[0]
        fcurve_x.keyframe_points[num_frame].co = num_frame, axis_angle[1]
        fcurve_y.keyframe_points[num_frame].co = num_frame, axis_angle[2]
        fcurve_z.keyframe_points[num_frame].co = num_frame, axis_angle[3]

def write_scales(fcurves, data_path, scales, frame_start = 0):
    """Write fcurve scale values across frames. Scale values are assumed
    to be sequential in the number of frames (step size 1).

    Args:

        fcurves
        data_path
        scales
        frame_start
    """

    fcurve_x = fcurves.new(data_path=data_path, index=0)
    fcurve_y = fcurves.new(data_path=data_path, index=1)
    fcurve_z = fcurves.new(data_path=data_path, index=2)

    frame_len = len(scales)

    fcurve_x.keyframe_points.add(count=frame_len)
    fcurve_y.keyframe_points.add(count=frame_len)
    fcurve_z.keyframe_points.add(count=frame_len)

    for num_frame, scale in enumerate(scales, frame_start):

        fcurve_x.keyframe_points[num_frame].co = num_frame, scale.x
        fcurve_y.keyframe_points[num_frame].co = num_frame, scale.y
        fcurve_z.keyframe_points[num_frame].co = num_frame, scale.z

def write_rotation_matrices(fcurves, rotations, rotation_mode, frame_start = 0,
                            bone_name = None):
    """Convencience function. Writes rotation matrices to selected fcurves
    across frames.

    Args:

        fcurves
        rotations
        rotation_mode
        frame_start
        bone_name

    Returns:

        matrices (list<mathutils.Matrix>): rotation matrix values per frame.
    """

    if rotation_mode == 'XYZ' or rotation_mode == 'XZY' or \
       rotation_mode == 'YXZ' or rotation_mode == 'YZX' or \
       rotation_mode == 'ZXY' or rotation_mode == 'ZYX':

        if bone_name:
            data_path = DP_BONE_EULER.format(bone_name)
        else:
            data_path = DP_EULER

        eulers = []
        for rotation in rotations:

            euler = rotation.to_euler(rotation_mode)
            eulers.append(euler)

        write_eulers(fcurves, data_path, eulers, frame_start)

    elif rotation_mode == 'AXIS_ANGLE':

        if bone_name:
            data_path = DP_BONE_AXIS_ANGLE.format(bone_name)
        else:
            data_path = DP_AXIS_ANGLE

        axis_angles = []
        for rotation in rotations:

            axis_angle = blender_util_m.matrix_to_axis_angle(rotation)
            axis_angles.append(axis_angle)

        write_axis_angles(fcurves, data_path, axis_angles, frame_start)

    elif rotation_mode == 'QUATERNION':

        if bone_name:
            data_path = DP_BONE_QUATERNION.format(bone_name)
        else:
            data_path = DP_QUATERNION

        quaternions = []
        for rotation in rotations:

            quaternion = rotation.to_quaternion()
            quaternions.append(quaternion)

        write_quaternions(fcurves, data_path, quaternions, frame_start)

    else:

        exception_string = "Unknown rotation mode found"
        raise Exception(exception_string)
