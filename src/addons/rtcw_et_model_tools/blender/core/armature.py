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

"""Reading, writing and converting an armature object. Armatures are primarily
used to animate meshes (see skeletal animation).
"""

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.blender.core.fcurve as fcurve_m
import rtcw_et_model_tools.blender.util as blender_util_m
import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


# =====================================
# READ
# =====================================

def _read_pose_bone_lr(armature_object, bone_name, frame_start=0, frame_end=0):
    """Read pose bone location and rotation values. If not animated, return
    static values across frames. The values are returned in bind pose space.
    Scale is not supported.

    Args:

        armature_object
        bone_name
        frame_start
        frame_end

    Returns:

        (locations, rotations)
    """

    # find out if its animated by searching for the fcurve of an action
    fcurves = None
    if armature_object.animation_data:

        action = armature_object.animation_data.action
        if action:

            fcurves = action.fcurves
            if not fcurves:

                reporter_m.warning("Action found with no fcurves on armature"
                                   " '{}' and pose bone '{}"
                                   .format(armature_object.name, bone_name))

        else:

            reporter_m.warning("Animation data with no action found on"
                               " armature '{}'"
                               .format(armature_object.name))

    locations = []
    rotations = []
    if fcurves:

        # locations
        data_path = fcurve_m.DP_BONE_LOCATION.format(bone_name)
        locations = fcurve_m.read_locations(fcurves,
                                            data_path,
                                            frame_start,
                                            frame_end)

        # rotations
        rotation_mode = armature_object.pose.bones[bone_name].rotation_mode
        rotations = fcurve_m.read_rotation_matrices(fcurves,
                                                    rotation_mode,
                                                    frame_start,
                                                    frame_end,
                                                    bone_name)

    if not locations:

        location = mathutils.Vector((0, 0, 0))
        locations = [location] * (frame_end + 1 - frame_start)

    if not rotations:

        rotation = mathutils.Matrix.Identity(3)
        rotations = [rotation] * (frame_end + 1 - frame_start)

    return (locations, rotations)

def read(armature_object, frame_start, frame_end):
    """Read armature object and convert to mdi.

    Args:

        armature_object
        frame_start
        frame_end

    Returns:

        mdi_skeleton
    """

    if not armature_object:
        return None

    mdi_skeleton = mdi_m.MDISkeleton()

    mdi_skeleton.name = armature_object.name
    mdi_skeleton.torso_parent_bone = 0  # calculated later

    # bones
    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='EDIT')

    # extract and tmp store all bones bind pose locations and orientations
    # for faster access
    bind_pose_locations = []
    bind_pose_orientations = []
    for edit_bone in armature_object.data.edit_bones:

        bl_ms, bo_ms, _ = edit_bone.matrix.decompose()
        bo_ms = bo_ms.to_matrix()

        bind_pose_locations.append(bl_ms)
        bind_pose_orientations.append(bo_ms)

    # create the mdi bones
    for num_bone, edit_bone in enumerate(armature_object.data.edit_bones):

        cbl_ms = bind_pose_locations[num_bone]
        cbo_ms = bind_pose_orientations[num_bone]

        mdi_bone = mdi_m.MDIBone()

        mdi_bone.name = edit_bone.name

        parent_index = -1
        if edit_bone.parent:
            parent_index = \
                armature_object.data.edit_bones.find(edit_bone.parent.name)
        mdi_bone.parent_bone = parent_index

        # parent_dist
        if parent_index >= 0:

            pbl_ms = bind_pose_locations[parent_index]
            mdi_bone.parent_dist = (cbl_ms - pbl_ms).length

        else:  # root bone

            cbl_ms = bind_pose_locations[num_bone]
            mdi_bone.parent_dist = cbl_ms.length

        # torso_weight
        try:
            torso_weight = edit_bone['Torso Weight']
            mdi_bone.torso_weight = torso_weight
        except:
            pass  # it's ok

        # sneak in check for torso parent
        try:
            _ = edit_bone['Torso Parent']
            mdi_skeleton.torso_parent_bone = num_bone
        except:
            pass  # it's ok

        locations, rotations = \
            _read_pose_bone_lr(armature_object,
                               mdi_bone.name,
                               frame_start,
                               frame_end)

        # calculate locations and orientations based on extracted offsets
        if mdi_bone.parent_bone >= 0:

            # use already calculated parent for faster access
            mdi_parent_bone = mdi_skeleton.bones[mdi_bone.parent_bone]

            pbl_ms = bind_pose_locations[mdi_bone.parent_bone]
            pbo_ms = bind_pose_orientations[mdi_bone.parent_bone]

            for num_frame in range(len(locations)):

                location_off = locations[num_frame]
                rotation_off = rotations[num_frame]

                pfl_ms = mdi_parent_bone.locations[num_frame]
                pfo_ms = mdi_parent_bone.orientations[num_frame]

                # express the childs bind pose in parent space
                cbl_ps = pbo_ms.transposed() @ (cbl_ms - pbl_ms)
                cbo_ps = pbo_ms.transposed() @ cbo_ms

                # calculate the model space coordinates of the child in
                # blenders bind pose
                cbl_dash_ms = pfl_ms + pfo_ms @ cbl_ps
                cbo_dash_ms = pfo_ms @ cbo_ps

                # calculate model space values for frame
                location = cbl_dash_ms + cbo_dash_ms @ location_off
                orientation = cbo_dash_ms @ rotation_off

                mdi_bone.locations.append(location)
                mdi_bone.orientations.append(orientation)

        else:  # root bone

            for num_frame in range(len(locations)):

                location_off = locations[num_frame]
                rotation_off = rotations[num_frame]

                location = cbl_ms + cbo_ms @ location_off
                orientation = cbo_ms @ rotation_off

                mdi_bone.locations.append(location)
                mdi_bone.orientations.append(orientation)

        mdi_skeleton.bones.append(mdi_bone)

    bpy.ops.object.mode_set(mode='OBJECT')

    return mdi_skeleton

# =====================================
# WRITE
# =====================================

def _write_pose_bone_lr(armature_object, bone_name, locations, rotations,
                        frame_start):
    """Write pose bone location and rotation values. The values should be given
    in bind pose space. Scale is not supported.

    Args:

        armature_object
        bone_name
        locations
        rotations
        frame_start
    """

    num_frames = len(locations)
    num_rotations = len(rotations)
    if num_frames != num_rotations:

        exception_string = "Unequal frame count found when writing pose bone" \
                           " '{}' for armature '{}'" \
                           .format(bone_name, armature_object.name)
        raise Exception(exception_string)

    if num_frames == 1:

        pass  # no need to animate

    elif num_frames > 1:

        if not armature_object.animation_data:
            armature_object.animation_data_create()

        if not armature_object.animation_data.action:
            armature_object.animation_data.action = \
                bpy.data.actions.new(name=armature_object.name)

        fcurves = armature_object.animation_data.action.fcurves

        # locations
        data_path = fcurve_m.DP_BONE_LOCATION.format(bone_name)
        fcurve_m.write_locations(fcurves, data_path, locations)

        # rotations
        fcurve_m.write_rotation_matrices(fcurves,
                                         rotations,
                                         "QUATERNION",
                                         frame_start,
                                         bone_name)

        fcurve_m.set_interpolation_mode(fcurves, 'LINEAR')

    else:  # nothing to write

        pass

def _set_constraints(mdi_skeleton, armature_object):

    timer = timer_m.Timer()
    reporter_m.debug("Setting contraints ...")

    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='POSE')

    for mdi_bone in mdi_skeleton.bones:

        mdi_bone_parent_name = mdi_skeleton.bones[mdi_bone.parent_bone].name

        if mdi_bone.parent_bone >= 0:

            pose_bone = armature_object.pose.bones[mdi_bone.name]

            pose_bone.constraints.new(type="LIMIT_DISTANCE")

            pose_bone.constraints["Limit Distance"].target = \
                armature_object
            pose_bone.constraints["Limit Distance"].subtarget = \
                armature_object.data.bones[mdi_bone_parent_name].name
            pose_bone.constraints["Limit Distance"].use_transform_limit \
                = False
            pose_bone.constraints["Limit Distance"].limit_mode \
                = "LIMITDIST_ONSURFACE"

    bpy.ops.object.mode_set(mode='OBJECT')

    time = timer.time()
    reporter_m.debug("Setting contraints DONE (time={})".format(time))

def _animate_bones(mdi_skeleton, root_frame, armature_object):

    sample_bone = mdi_skeleton.bones[0]
    if len(sample_bone.locations) == 1:
        reporter_m.info("No bone animations.")
        return

    timer = timer_m.Timer()
    reporter_m.debug("Animating bones ...")

    for mdi_bone in mdi_skeleton.bones:

        # prepare locations, rotations
        locations = []
        rotations = []

        for num_frame in range(len(mdi_bone.locations)):

            # c = child, p = parent
            # b = bind frame, f = current frame
            # l = location, o = orientation
            # _ms = model space, _ps = parent space
            cbl_ms = mdi_bone.locations[root_frame]
            cbo_ms = mdi_bone.orientations[root_frame]
            cfl_ms = mdi_bone.locations[num_frame]
            cfo_ms = mdi_bone.orientations[num_frame]

            if mdi_bone.parent_bone >= 0:

                mdi_parent_bone = mdi_skeleton.bones[mdi_bone.parent_bone]

                pbl_ms = mdi_parent_bone.locations[root_frame]
                pbo_ms = mdi_parent_bone.orientations[root_frame]
                pfl_ms = mdi_parent_bone.locations[num_frame]
                pfo_ms = mdi_parent_bone.orientations[num_frame]

                # blenders bone animations (as we defined them in our
                # settings) are relative to its bind pose space, the bind
                # pose space is nested within parent space, so we need to
                # transform our data which is given in model space

                # express the childs bind pose in parent space
                cbl_ps = pbo_ms.transposed() @ (cbl_ms - pbl_ms)
                cbo_ps = pbo_ms.transposed() @ cbo_ms

                # calculate the model space coordinates of the child in
                # blenders bind pose
                cbl_dash_ms = pfl_ms + pfo_ms @ cbl_ps
                cbo_dash_ms = pfo_ms @ cbo_ps

                # offset from blenders bind pose to our wished model space
                # values
                location_off = cbo_dash_ms.transposed() @ \
                    (cfl_ms - cbl_dash_ms)
                orientation_off = cbo_dash_ms.transposed() @ cfo_ms

            else:

                location_off = cbo_ms.transposed() @ (cfl_ms - cbl_ms)
                orientation_off = cbo_ms.transposed() @ cfo_ms

            locations.append(location_off)
            rotations.append(orientation_off)

        # write locations, rotations
        _write_pose_bone_lr(armature_object,
                            mdi_bone.name,
                            locations,
                            rotations,
                            frame_start=0)

    time = timer.time()
    reporter_m.debug("Animating bones DONE (time={})".format(time))

def _add_edit_bones(mdi_skeleton, root_frame, armature_object):

    timer = timer_m.Timer()
    reporter_m.debug("Adding edit bones ...")

    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='EDIT')

    for num_bone, mdi_bone in enumerate(mdi_skeleton.bones):

        edit_bone = armature_object.data.edit_bones.new(mdi_bone.name)

        edit_bone.head = (0, 0, 0)
        edit_bone.tail = (0, 1, 0)
        edit_bone.use_connect = False
        edit_bone.use_inherit_scale = True
        edit_bone.use_local_location = True
        edit_bone.use_inherit_rotation = True

        bind_pose_location = mdi_bone.locations[root_frame]
        bind_pose_orientation = mdi_bone.orientations[root_frame]

        bind_pose_matrix = \
            mathutils.Matrix.Translation(bind_pose_location) @ \
                bind_pose_orientation.to_4x4()
        edit_bone.matrix = bind_pose_matrix

        edit_bone['Torso Weight'] = mdi_bone.torso_weight

        if num_bone == mdi_skeleton.torso_parent_bone:

            edit_bone['Torso Parent'] = True

    # set parent-child-relationship
    for mdi_bone in mdi_skeleton.bones:

        if mdi_bone.parent_bone >= 0:

            mdi_bone_parent = mdi_skeleton.bones[mdi_bone.parent_bone]

            child = armature_object.data.edit_bones[mdi_bone.name]
            parent = armature_object.data.edit_bones[mdi_bone_parent.name]
            child.parent = parent

    bpy.ops.object.mode_set(mode='OBJECT')

    time = timer.time()
    reporter_m.debug("Adding edit bones DONE (time={})".format(time))

def _create_armature(mdi_skeleton, collection):

    timer = timer_m.Timer()
    reporter_m.debug("Creating armature ...")

    name = mdi_skeleton.name

    armature = bpy.data.armatures.new("{}{}".format(name, "_data"))
    armature_object = bpy.data.objects.new(name, armature)

    collection.objects.link(armature_object)

    time = timer.time()
    reporter_m.debug("Creating armature DONE (time={})".format(time))

    return armature_object

def write(mdi_skeleton, root_frame, collection):
    """Convert mdi skeleton and write to collection.

    Args:

        mdi_model
        collection

    Returns:

        armature_object
    """

    if not mdi_skeleton:
        return None

    timer = timer_m.Timer()
    reporter_m.debug("Writing armature ...")

    armature_object = _create_armature(mdi_skeleton, collection)

    _add_edit_bones(mdi_skeleton, root_frame, armature_object)

    _animate_bones(mdi_skeleton, root_frame, armature_object)

    _set_constraints(mdi_skeleton, armature_object)

    time = timer.time()
    reporter_m.debug("Writing armature DONE (time={})".format(time))

    return armature_object
