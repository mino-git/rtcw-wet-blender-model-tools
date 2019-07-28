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

import math

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.blender.core.arrow as arrow_m
import rtcw_et_model_tools.blender.core.fcurve as fcurve_m
import rtcw_et_model_tools.common.reporter as reporter_m


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

def read_object_locations(blender_object, frame_start, frame_end,
                          bone_name = None):
    """Read location values of an object (transforms). If not animated, return
    static values across frames.

    Args:

        blender_object
        frame_start
        frame_end
        bone_name

    Returns:

        locations
    """

    locations = []

    if blender_object.animation_data:

        action = blender_object.animation_data.action
        if action:

            fcurves = action.fcurves
            if not fcurves:

                reporter_m.warning("Action found with no fcurves")

            else:

                locations = fcurve_m.read_locations(fcurves,
                                                    frame_start,
                                                    frame_end,
                                                    bone_name)

        else:  # no action

            reporter_m.warning("Animation data with no action found")

    else:  # no animation_data

        pass

    if not locations:  # create static values

        if bone_name:  # values are in bind pose space for bones

            location = mathutils.Vector((0, 0, 0))
            locations = [location] * (frame_end + 1 - frame_start)

        else:  # values are in local space for all other objects

            location, _, _ = blender_object.matrix_world.decompose()
            locations = [location] * (frame_end + 1 - frame_start)

    return locations

def read_object_rotations(blender_object, frame_start, frame_end,
                          bone_name = None):
    """Read rotation values of an object (transforms). If not animated, return
    static values across frames.

    Args:

        blender_object
        frame_start
        frame_end
        bone_name

    Returns:

        rotations
    """

    rotations = []

    if blender_object.animation_data:

        action = blender_object.animation_data.action
        if action:

            fcurves = action.fcurves
            if not fcurves:

                reporter_m.warning("Action found with no fcurves")

            else:

                if bone_name:

                    pose_bone = blender_object.pose.bones[bone_name]
                    rotation_mode = pose_bone.rotation_mode

                else:

                    rotation_mode = blender_object.rotation_mode

                if rotation_mode == 'XYZ' or rotation_mode == 'XZY' or \
                   rotation_mode == 'YXZ' or rotation_mode == 'YZX' or \
                   rotation_mode == 'ZXY' or rotation_mode == 'ZYX':

                    eulers = fcurve_m.read_eulers(fcurves,
                                                  frame_start,
                                                  frame_end,
                                                  bone_name,
                                                  rotation_mode)

                    if eulers:

                        for euler in eulers:

                            rotation = euler.to_matrix()
                            rotations.append(rotation)

                elif rotation_mode == 'AXIS_ANGLE':

                    axis_angles = fcurve_m.read_axis_angles(fcurves,
                                                            frame_start,
                                                            frame_end,
                                                            bone_name)

                    if axis_angles:

                        for axis_angle in axis_angles:

                            rotation = axis_angle_to_matrix(axis_angle)
                            rotations.append(rotation)

                elif rotation_mode == 'QUATERNION':

                    quaternions = fcurve_m.read_quaternions(fcurves,
                                                            frame_start,
                                                            frame_end,
                                                            bone_name)

                    if quaternions:

                        for quaternion in quaternions:

                            rotation = quaternion.to_matrix()
                            rotations.append(rotation)

                else:

                    raise Exception("Unknown rotation mode")

        else:  # no action

            reporter_m.warning("Animation data with no action found")

    else:  # no animation_data

        pass

    if not rotations:  # create static values

        if bone_name:  # values are in bind pose space for bones

            rotation = mathutils.Matrix.Identity(3)
            rotations = [rotation] * (frame_end + 1 - frame_start)

        else:  # values are in local space for all other objects

            _, rotation, _ = blender_object.matrix_world.decompose()
            rotation = rotation.to_matrix()
            rotations = [rotation] * (frame_end + 1 - frame_start)

    return rotations

def read_object_scales(blender_object, frame_start, frame_end,
                       bone_name = None):
    """Read scale values of an object (transforms). If not animated, return
    static values across frames.

    Args:

        blender_object
        frame_start
        frame_end
        bone_name

    Returns:

        locations
    """

    scales = []

    if blender_object.animation_data:

        action = blender_object.animation_data.action
        if action:

            fcurves = action.fcurves
            if not fcurves:

                reporter_m.warning("Action found with no fcurves")

            else:

                scales = fcurve_m.read_scales(fcurves,
                                              frame_start,
                                              frame_end,
                                              bone_name)

        else:  # no action

            reporter_m.warning("Animation data with no action found")

    else:  # no animation_data

        pass

    if not scales:  # create static values

        if bone_name:  # values are in bind pose space for bones

            scale = mathutils.Vector((1, 1, 1))
            scales = [scale] * (frame_end + 1 - frame_start)

        else:  # values are in local space for all other objects

            _, _, scale = blender_object.matrix_world.decompose()
            scales = [scale] * (frame_end + 1 - frame_start)

    return scales

def write_object_locations(blender_object, locations, frame_start = 0,
                           bone_name = None):
    """Write location values of an object (transforms).

    Args:

        blender_object
        locations
        frame_start
        bone_name
    """

    num_frames = len(locations)
    if num_frames == 1:

        # TODO maybe support this another time, for now its not needed
        reporter_m.warning("Setting location handled elsewhere")

    elif num_frames > 1:

        if not blender_object.animation_data:
            blender_object.animation_data_create()

        if not blender_object.animation_data.action:
            blender_object.animation_data.action = \
                bpy.data.actions.new(name=blender_object.name)

        fcurves = blender_object.animation_data.action.fcurves
        fcurve_m.write_locations(fcurves, locations, frame_start, bone_name)

    else:  # nothing to write

        pass

def write_object_rotations(blender_object, rotations, rotation_mode = 'XYZ',
                           frame_start = 0, bone_name = None):
    """Write rotation values of an object (transforms).

    Args:

        blender_object
        rotations
        rotation_mode
        frame_start
        bone_name
    """

    num_frames = len(rotations)
    if num_frames == 1:

        # TODO maybe support this another time, for now its not needed
        reporter_m.warning("Setting rotation handled elsewhere")

    elif num_frames > 1:

        if not blender_object.animation_data:
            blender_object.animation_data_create()

        if not blender_object.animation_data.action:
            blender_object.animation_data.action = \
                bpy.data.actions.new(name=blender_object.name)

        fcurves = blender_object.animation_data.action.fcurves

        if rotation_mode == 'XYZ' or rotation_mode == 'XZY' or \
            rotation_mode == 'YXZ' or rotation_mode == 'YZX' or \
            rotation_mode == 'ZXY' or rotation_mode == 'ZYX':

            eulers = []
            for rotation in rotations:
                euler = rotation.to_euler(rotation_mode)
                eulers.append(euler)

            fcurve_m.write_eulers(fcurves, eulers, frame_start, bone_name)

        elif rotation_mode == 'AXIS_ANGLE':

            axis_angles = []
            for rotation in rotations:
                axis_angle = axis_angle_to_matrix(rotation)
                axis_angles.append(axis_angle)

            fcurve_m.write_axis_angles(fcurves, axis_angles, frame_start,
                                       bone_name)

        elif rotation_mode == 'QUATERNION':

            quaternions = []
            for rotation in rotations:
                quaternion = rotation.to_quaternion()
                quaternions.append(quaternion)

            fcurve_m.write_quaternions(fcurves, quaternions, frame_start,
                                       bone_name)

    else:  # nothing to write

        pass

def apply_parent_transforms(mdi_model, mesh_objects, armature_object,
                            arrow_objects):
    """TODO
    """

    pass

def apply_object_transforms(mdi_model, mesh_objects, armature_object,
                            arrow_objects, frame_start, frame_end):
    """TODO
    """

    # mesh_objects
    for mesh_object in mesh_objects:

        mdi_vertices = None
        for mdi_surface in mdi_model.surfaces:
            if mdi_surface.name == mesh_object.name:
                mdi_vertices = mdi_surface.vertices
                break

        if not mdi_vertices:

            reporter_m.warning("Could not find mdi vertices for mesh object"
                               " '{}' during object transforming."
                               .format(mesh_object.name))
            continue

        locations_os = \
            read_object_locations(mesh_object, frame_start, frame_end)
        rotations_os = \
            read_object_rotations(mesh_object, frame_start, frame_end)
        scales_os = \
            read_object_scales(mesh_object, frame_start, frame_end)

        for mdi_vertex in mdi_vertices:

            # only for morph vertices
            if isinstance(mdi_vertex, mdi_m.MDIMorphVertex):

                for num_frame in range(len(locations_os)):

                    location_cs = mdi_vertex.locations[num_frame]
                    normal_cs = mdi_vertex.normals[num_frame]
                    location_os = locations_os[num_frame]
                    rotation_os = rotations_os[num_frame]
                    scale_os = scales_os[num_frame]

                    # we can't do this inplace since some mdi_vertex objects
                    # might be duplicated during uv map pass, so just create
                    # a new vector
                    sx = location_cs[0] * scale_os[0]
                    sy = location_cs[1] * scale_os[1]
                    sz = location_cs[2] * scale_os[2]
                    location_scaled = mathutils.Vector((sx, sy, sz))

                    mdi_vertex.locations[num_frame] = \
                        location_os + rotation_os @ location_scaled

                    mdi_vertex.normals[num_frame] = rotation_os @ normal_cs

    # armature_object
    if armature_object:

        if not mdi_model.skeleton:

            reporter_m.warning("Could not apply skeleton object transforms.")

        else:

            locations_os = \
                read_object_locations(armature_object, frame_start, frame_end)
            orientations_os = \
                read_object_rotations(armature_object, frame_start, frame_end)
            # scale not supported for skeleton object transforms,
            # because of fixed dist constraint

            for mdi_bone in mdi_model.skeleton.bones:

                for num_frame in range(len(locations_os)):

                    location_cs = mdi_bone.locations[num_frame]
                    orientation_cs = mdi_bone.orientations[num_frame]
                    location_os = locations_os[num_frame]
                    orientation_os = orientations_os[num_frame]

                    mdi_bone.locations[num_frame] = \
                        location_os + orientation_os @ location_cs
                    mdi_bone.orientations[num_frame] = \
                        (orientation_os @ orientation_cs)

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
