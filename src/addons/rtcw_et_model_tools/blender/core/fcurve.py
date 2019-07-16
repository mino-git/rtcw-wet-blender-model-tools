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

import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


dp_location = 'location'
dp_quaternion = 'rotation_quaternion'
dp_euler = 'rotation_euler'
dp_axis_angle = 'rotation_axis_angle'

dp_bone_location = 'pose.bones["{}"].location'
dp_bone_quaternion = 'pose.bones["{}"].rotation_quaternion'
dp_bone_euler = 'pose.bones["{}"].rotation_euler'
dp_bone_axis_angle = 'pose.bones["{}"].rotation_axis_angle'


# =====================================
# READ
# =====================================

def read_fcurves_locations(action, data_path):
    """Read fcurve location values across a number of frames.

    Args:

        action
        data_path

    Returns:

        locations (list<mathutils.Vector>): location values per frame.
    """

    locations = []

    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    fcurve_x = action.fcurves.find(data_path, index=0)
    fcurve_y = action.fcurves.find(data_path, index=1)
    fcurve_z = action.fcurves.find(data_path, index=2)

    if fcurve_x and fcurve_y and fcurve_z:

        for num_frame in range(frame_start, frame_end + 1):

            x = fcurve_x.evaluate(num_frame)
            y = fcurve_y.evaluate(num_frame)
            z = fcurve_z.evaluate(num_frame)

            location = mathutils.Vector((x, y, z))
            locations.append(location)

    return locations

def read_fcurves_quaternions(action, data_path):
    """Read fcurve quaternion values across a number of frames.

    Args:

        action
        data_path

    Returns:

        rotations (list<mathutils.Matrix>): rotation matrix values per frame.
    """

    rotations = []

    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    fcurve_w = action.fcurves.find(data_path, index=0)
    fcurve_x = action.fcurves.find(data_path, index=1)
    fcurve_y = action.fcurves.find(data_path, index=2)
    fcurve_z = action.fcurves.find(data_path, index=3)

    if fcurve_w and fcurve_x and fcurve_y and fcurve_z:

        for num_frame in range(frame_start, frame_end + 1):

            qw = fcurve_w.evaluate(num_frame)
            qx = fcurve_x.evaluate(num_frame)
            qy = fcurve_y.evaluate(num_frame)
            qz = fcurve_z.evaluate(num_frame)

            rotation = mathutils.Quaternion((qw, qx, qy, qz)).to_matrix()
            rotations.append(rotation)

    return rotations

def read_fcurves_eulers(action, data_path):

    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    # TODO
    rotations = []
    return rotations

def read_fcurves_axis_angles(action, data_path):

    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    # TODO
    rotations = []
    return rotations

def read_pose_bone(armature_object, bone_name):
    """Read fcurve data from a pose bone.

    Args:

        armature_object
        bone_name

    Returns:

        locations (list<mathutils.Vector>): list of locations per frame.
        rotations (list<mathutils.Matrix>): list of rotation matrices per
            frame.
    """

    locations = None
    rotations = None

    is_animated = armature_object.animation_data and \
                  armature_object.animation_data.action
    if not is_animated:
        return (locations, rotations)

    data_path_loc = dp_bone_location.format(bone_name)
    data_path_rot = dp_bone_quaternion.format(bone_name)

    action = armature_object.animation_data.action

    # locations
    locations = read_fcurves_locations(action, data_path_loc)

    # rotations
    rotation_mode = armature_object.pose.bones[bone_name].rotation_mode
    if rotation_mode == 'XYZ' or rotation_mode == 'XZY' or \
        rotation_mode == 'YXZ' or rotation_mode == 'YZX' or \
        rotation_mode == 'ZXY' or rotation_mode == 'ZYX':

        # fcurve_euler_x = action.fcurves.find(dp_euler, index=0)
        # fcurve_euler_y = action.fcurves.find(dp_euler, index=1)
        # fcurve_euler_z = action.fcurves.find(dp_euler, index=2)

        pass  # TODO

    elif rotation_mode == 'AXIS_ANGLE':

        # fcurve_axis_angle_w = \
        #     action.fcurves.find(dp_axis_angle, index=0)
        # fcurve_axis_angle_x = \
        #     action.fcurves.find(dp_axis_angle, index=1)
        # fcurve_axis_angle_y = \
        #     action.fcurves.find(dp_axis_angle, index=2)
        # fcurve_axis_angle_z = \
        #     action.fcurves.find(dp_axis_angle, index=3)

        pass  # TODO

    elif rotation_mode == 'QUATERNION':

        rotations = read_fcurves_quaternions(action, data_path_rot)

    else:

        pass  # TODO

    return (locations, rotations)

def read_object(blender_object):
    """Read fcurve data from a blender object.

    Args:

        blender_object (Object(ID)): a blender object.

    Returns:

        locations (list<mathutils.Vector>): list of locations per frame.
        rotations (list<mathutils.Matrix>): list of rotation matrices per
            frame.
    """

    # TODO scales?

    locations = None
    rotations = None

    is_animated = \
        blender_object.animation_data and blender_object.animation_data.action
    if not is_animated:
        return (locations, rotations)

    action = blender_object.animation_data.action

    # locations
    locations = read_fcurves_locations(action, dp_location)

    # rotations
    rotation_mode = blender_object.rotation_mode

    if rotation_mode == 'XYZ' or rotation_mode == 'XZY' or \
        rotation_mode == 'YXZ' or rotation_mode == 'YZX' or \
        rotation_mode == 'ZXY' or rotation_mode == 'ZYX':

        # fcurve_euler_x = action.fcurves.find(dp_euler, index=0)
        # fcurve_euler_y = action.fcurves.find(dp_euler, index=1)
        # fcurve_euler_z = action.fcurves.find(dp_euler, index=2)

        pass  # TODO

    elif rotation_mode == 'AXIS_ANGLE':

        # fcurve_axis_angle_w = \
        #     action.fcurves.find(dp_axis_angle, index=0)
        # fcurve_axis_angle_x = \
        #     action.fcurves.find(dp_axis_angle, index=1)
        # fcurve_axis_angle_y = \
        #     action.fcurves.find(dp_axis_angle, index=2)
        # fcurve_axis_angle_z = \
        #     action.fcurves.find(dp_axis_angle, index=3)

        pass  # TODO

    elif rotation_mode == 'QUATERNION':

        rotations = read_fcurves_quaternions(action, dp_quaternion)

    else:

        pass  # TODO

    return (locations, rotations)

# =====================================
# WRITE
# =====================================

def write_fcurves_locations(action, data_path, locations):
    """Write fcurve location values across a number of frames.

    Args:

        action
        data_path
        locations (list<mathutils.Vector>): location values per frame.
    """

    fcurve_x = action.fcurves.new(data_path=data_path, index=0)
    fcurve_y = action.fcurves.new(data_path=data_path, index=1)
    fcurve_z = action.fcurves.new(data_path=data_path, index=2)

    frame_len = len(locations)

    fcurve_x.keyframe_points.add(count=frame_len)
    fcurve_y.keyframe_points.add(count=frame_len)
    fcurve_z.keyframe_points.add(count=frame_len)

    for num_frame, location in enumerate(locations):

        fcurve_x.keyframe_points[num_frame].co = num_frame, location.x
        fcurve_y.keyframe_points[num_frame].co = num_frame, location.y
        fcurve_z.keyframe_points[num_frame].co = num_frame, location.z

def write_fcurves_quaternions(action, data_path, rotations):
    """Write fcurve quaternion values across a number of frames.

    Args:

        action
        data_path
        rotations<mathutils.Matrix>: rotation matrix values per frame.
    """

    fcurve_w = action.fcurves.new(data_path=data_path, index=0)
    fcurve_x = action.fcurves.new(data_path=data_path, index=1)
    fcurve_y = action.fcurves.new(data_path=data_path, index=2)
    fcurve_z = action.fcurves.new(data_path=data_path, index=3)

    frame_len = len(rotations)

    fcurve_w.keyframe_points.add(count=frame_len)
    fcurve_x.keyframe_points.add(count=frame_len)
    fcurve_z.keyframe_points.add(count=frame_len)
    fcurve_y.keyframe_points.add(count=frame_len)

    for num_frame, rotation in enumerate(rotations):

        quaternion = rotation.to_quaternion()
        fcurve_w.keyframe_points[num_frame].co = num_frame, quaternion.w
        fcurve_x.keyframe_points[num_frame].co = num_frame, quaternion.x
        fcurve_y.keyframe_points[num_frame].co = num_frame, quaternion.y
        fcurve_z.keyframe_points[num_frame].co = num_frame, quaternion.z

def write_fcurves_eulers(action, data_path):

    # TODO
    pass

def write_fcurves_axis_angles(action, data_path):

    # TODO
    pass

def write_pose_bone(pose_bone, action, locations, rotations):
    """Write fcurve data for a pose bone.

    Args:

        armature_object
        bone_name
        action
        locations (list<mathutils.Vector>): location values per frame.
        rotations (list<mathutils.Matrix>): rotation matrices per frame.
    """
    # TODO maybe check rotation mode or provide it as default parameter
    # TODO num_frames mismatch locations rotations

    dp_bone_loc = dp_bone_location.format(pose_bone.name)
    dp_bone_rot = dp_bone_quaternion.format(pose_bone.name)

    pose_bone.rotation_mode = 'QUATERNION'

    write_fcurves_locations(action, dp_bone_loc, locations)
    write_fcurves_quaternions(action, dp_bone_rot, rotations)

def write_object(blender_object, action, locations, rotations):
    """Write fcurve data for a blender object.

    Args:

        blender_object
        action
        locations (list<mathutils.Vector>): location values per frame.
        rotations (list<mathutils.Matrix>): rotation matrices per frame.
    """

    # TODO maybe check rotation mode or provide it as default parameter
    # TODO num_frames mismatch locations rotations

    blender_object.rotation_mode = 'QUATERNION'

    write_fcurves_locations(action, dp_location, locations)
    write_fcurves_quaternions(action, dp_quaternion, rotations)
