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


class Transform:

    def __init__(self, blender_object):

        self.blender_object = blender_object

        self.num_parents = 0
        self.parent_transform = None

        self.locs = []
        self.rots = []
        self.scales = []

    @staticmethod
    def get(blender_object, transforms):

        if blender_object == None:
            return None

        transform = None
        for t in transforms:

            if t.blender_object == blender_object:
                transform = t
                break

        return transform

    def calc_parent_props(self, transforms):

        # num_parents
        num_parents = -1

        cur_object = self.blender_object
        while cur_object:

            num_parents += 1

            if isinstance(cur_object, bpy.types.Bone):

                if not cur_object.parent:

                    tmp = Transform.get(cur_object, transforms)
                    cur_object = tmp.parent_armature

                else:

                    cur_object = cur_object.parent

            else:

                if cur_object.parent_type == 'BONE':

                    armature_object = cur_object.parent
                    bone_name = cur_object.parent_bone
                    bone = armature_object.data.bones[bone_name]
                    cur_object = bone

                else:

                    cur_object = cur_object.parent

        self.num_parents = num_parents

        # parent_transform
        parent_transform = None

        blender_object = self.blender_object
        if isinstance(blender_object, bpy.types.Bone):

            if not blender_object.parent:

                # get the armature transform
                bone_transform = \
                    Transform.get(blender_object, transforms)
                parent_transform = \
                    Transform.get(bone_transform.parent_armature, transforms)

            else:

                # get the bone transform
                parent_bone = blender_object.parent
                parent_transform = Transform.get(parent_bone, transforms)

        else:

            if blender_object.parent_type == 'BONE':

                # get the bone transform
                armature_object = blender_object.parent
                bone_name = blender_object.parent_bone
                bone = armature_object.data.bones[bone_name]
                parent_transform = Transform.get(bone, transforms)

            else:

                # it's a normal object
                parent_transform = \
                    Transform.get(blender_object.parent, transforms)

        self.parent_transform = parent_transform

    def read_local(self, frame_start, frame_end):

        import rtcw_et_model_tools.blender.core.armature as armature_m

        if isinstance(self.blender_object, bpy.types.Bone):

            armature_object = self.parent_armature
            bone_name = self.blender_object.name
            self.locs, self.rots = \
                armature_m.read_pose_bone_lr(armature_object,
                                             bone_name,
                                             frame_start,
                                             frame_end)

        else:

            self.locs, self.rots, self.scales = \
                read_object_space_lrs(self.blender_object,
                                      frame_start,
                                      frame_end)


    def transform_world(self, transforms, frame_start, frame_end):

        if isinstance(self.blender_object, bpy.types.Bone):

            armature_object = self.parent_armature
            matrix_local = armature_object.data.bones[self.blender_object.name].matrix_local

            cbl_ms, cbo_ms, cbs_ms = matrix_local.decompose()
            cbo_ms = cbo_ms.to_matrix()

            bone_parent = self.blender_object.parent
            if bone_parent:

                matrix_local = armature_object.data.bones[bone_parent.name].matrix_local

                pbl_ms, pbo_ms, pbs_ms = matrix_local.decompose()
                pbo_ms = pbo_ms.to_matrix()

                for num_frame in range(len(self.locs)):

                    location_off = self.locs[num_frame]
                    rotation_off = self.rots[num_frame]

                    pfl_ms = self.parent_transform.locs[num_frame]
                    pfo_ms = self.parent_transform.rots[num_frame]

                    # express the childs bind pose in parent space
                    cbl_ps = pbo_ms.transposed() * (cbl_ms - pbl_ms)
                    cbo_ps = pbo_ms.transposed() * cbo_ms

                    # calculate the model space coordinates of the child in
                    # blenders bind pose
                    cbl_dash_ms = pfl_ms + pfo_ms * cbl_ps
                    cbo_dash_ms = pfo_ms * cbo_ps

                    # calculate model space values for frame
                    location = cbl_dash_ms + cbo_dash_ms * location_off
                    orientation = cbo_dash_ms * rotation_off

                    self.locs[num_frame] = location
                    self.rots[num_frame] = orientation

            else:  # root bone

                for num_frame in range(len(self.locs)):

                    location_off = self.locs[num_frame]
                    rotation_off = self.rots[num_frame]

                    location = cbl_ms + cbo_ms * location_off
                    orientation = cbo_ms * rotation_off

                    self.locs[num_frame] = location
                    self.rots[num_frame] = orientation

                armature_transform = Transform.get(armature_object, transforms)
                for num_frame in range(len(self.locs)):

                    pfl = armature_transform.locs[num_frame]
                    pfr = armature_transform.rots[num_frame]
                    #pfs = armature_transform.scales[num_frame]

                    cfl = self.locs[num_frame]
                    cfr = self.rots[num_frame]
                    #cfs = transform.scales[num_frame]

                    location = pfl + pfr * cfl
                    orientation = pfr * cfr

                    self.locs[num_frame] = location
                    self.rots[num_frame] = orientation

        else:

            if self.parent_transform:

                if self.blender_object.parent_type == 'BONE':

                    # parented to tail, but we need head
                    off_y = mathutils.Vector((0, -1, 0))

                    for num_frame in range(len(self.locs)):

                        cfl = self.locs[num_frame] - off_y
                        cfr = self.rots[num_frame]
                        #cfs = self.scales[num_frame]

                        pfl = self.parent_transform.locs[num_frame]
                        pfr = self.parent_transform.rots[num_frame]
                        #pfs = self.parent_transform.scales[num_frame]

                        location = pfl + pfr * cfl
                        orientation = pfr * cfr

                        self.locs[num_frame] = location
                        self.rots[num_frame] = orientation

                else:

                    mi = self.blender_object.matrix_parent_inverse
                    pil_ms, pir_ms, pbs_ms = mi.decompose()
                    pir_ms = pir_ms.to_matrix()

                    for num_frame in range(len(self.locs)):

                        cfl_ls = self.locs[num_frame]
                        cfr_ls = self.rots[num_frame]
                        cfs_ls = self.scales[num_frame]

                        pfl_ms = self.parent_transform.locs[num_frame]
                        pfr_ms = self.parent_transform.rots[num_frame]

                        location = pfl_ms + pfr_ms * (pil_ms + pir_ms * cfl_ls)

                        cfr_ls = rotation_matrix_scaled(cfr_ls, cfs_ls)
                        orientation = pfr_ms * pir_ms * cfr_ls

                        self.locs[num_frame] = location
                        self.rots[num_frame] = orientation

            else:

                for num_frame in range(len(self.locs)):

                    cfl_ls = self.locs[num_frame]
                    cfr_ls = self.rots[num_frame]
                    cfs_ls = self.scales[num_frame]

                    cfr_ls = rotation_matrix_scaled(cfr_ls, cfs_ls)
                    self.rots[num_frame] = cfr_ls


def build_transforms_ws(blender_scene, frame_start, frame_end):

    transforms = []

    # initial reading
    for blender_object in blender_scene.objects:

        transform = Transform(blender_object)
        transforms.append(transform)

        if blender_object.type == 'ARMATURE':

            # need an extra run for the bones
            for bone in blender_object.data.bones:

                transform = Transform(bone)
                transforms.append(transform)

                # hack this in, so we have access to it later
                transform.parent_armature = blender_object

    # sort them based on num_parents
    for transform in transforms:
        transform.calc_parent_props(transforms)

    transforms.sort(key=lambda x: x.num_parents)

    # read local transforms: locs, rots, scales
    for transform in transforms:
        transform.read_local(frame_start, frame_end)

    # transform to world space
    for transform in transforms:
        transform.transform_world(transforms, frame_start, frame_end)

    return transforms

def get_active_action_fcurves(blender_object):

    fcurves = None

    if blender_object.animation_data and \
       blender_object.animation_data.action and \
       blender_object.animation_data.action.fcurves:

       fcurves = blender_object.animation_data.action.fcurves

    return fcurves

def rotation_matrix_scaled(matrix, scale):

    new_matrix = matrix.copy()

    new_matrix[0][0] *= scale[0]
    new_matrix[1][0] *= scale[0]
    new_matrix[2][0] *= scale[0]

    new_matrix[0][1] *= scale[1]
    new_matrix[1][1] *= scale[1]
    new_matrix[2][1] *= scale[1]

    new_matrix[0][2] *= scale[2]
    new_matrix[1][2] *= scale[2]
    new_matrix[2][2] *= scale[2]

    return new_matrix

def is_object_supported(mdi_object, blender_object):
    """Checks for constraints, modifiers, object space animation.
    """

    import rtcw_et_model_tools.mdi.mdi as mdi_m
    import rtcw_et_model_tools.blender.core.fcurve as fcurve_m
    import rtcw_et_model_tools.common.reporter as reporter_m

    is_supported = True

    # constraints not supported
    if len(blender_object.constraints) > 0:

        reporter_m.warning("Constraints for objects '{}' are generally not"
                            " supported"
                            .format(mdi_object.name))
        is_supported = False

    # modifiers
    # only armature modifier for rigged meshes
    if len(blender_object.modifiers) > 0:

        if isinstance(mdi_object, mdi_m.MDISurface):

            has_armature_modifier = False
            try:
                blender_object.modifiers['Armature']
                has_armature_modifier = True
            except:
                pass

            sample_vertex = mdi_object.vertices[0]
            if isinstance(sample_vertex, mdi_m.MDIMorphVertex):

                reporter_m.warning("Modifiers for mesh objects '{}' are"
                                   " generally not supported except the"
                                   " armature modifier"
                                   .format(mdi_object.name))
                is_supported = False

            elif isinstance(sample_vertex, mdi_m.MDIRiggedVertex):

                if has_armature_modifier:

                    if len(blender_object.modifiers) > 1:

                        reporter_m.warning("Found multiple modifiers for"
                                        " object '{}', but only armature"
                                        " modifier supported"
                                        .format(mdi_object.name))
                        is_supported = False

                else:

                    reporter_m.warning("Could not find armature modifier for"
                                       " object '{}'"
                                       .format(mdi_object.name))
                    is_supported = False

        else:

            reporter_m.warning("Modifiers for this type of object '{}' are"
                               " generally not supported"
                                .format(mdi_object.name))
            is_supported = False

    else:

        pass  # ok

    # object space animation
    if isinstance(mdi_object, mdi_m.MDISurface):

        if mdi_object.vertices:

            sample_vertex = mdi_object.vertices[0]
            if isinstance(sample_vertex, mdi_m.MDIMorphVertex):

                pass  # ok

            elif isinstance(sample_vertex, mdi_m.MDIRiggedVertex):

                animation_found = False

                fcurves = get_active_action_fcurves(blender_object)
                if fcurves:

                    animation_found = \
                        fcurve_m.is_animated(fcurves,
                                             rotation_mode = \
                                                 blender_object.rotation_mode,
                                             check_loc=True,
                                             check_rot=True,
                                             check_scale=True)

                if animation_found:

                    reporter_m.warning("Object space animation of rigged"
                                        " mesh object '{}' not supported"
                                    .format(mdi_object.name))
                    is_supported = False

            else:

                raise Exception("Found unknown object type")

    elif isinstance(mdi_object, mdi_m.MDIBoneTag) or \
         isinstance(mdi_object, mdi_m.MDIBoneTagOff):

        animation_found = False

        fcurves = get_active_action_fcurves(blender_object)
        if fcurves:

            animation_found = \
                fcurve_m.is_animated(fcurves,
                                     rotation_mode = \
                                        blender_object.rotation_mode,
                                     check_loc=True,
                                     check_rot=True,
                                     check_scale=True)

        if animation_found:

            reporter_m.warning("Arrow object '{}' object space animation"
                                " not supported for arrow objects parented"
                                " to a bone. They can only be animated by"
                                " animating the bone"
                                .format(mdi_object.name))
            is_supported = False

    return is_supported

def read_object_space_lrs(blender_object, frame_start=0, frame_end=0,
                          read_locs=True, read_rots=True,
                          read_scales=True):
    """Read object space location, rotation and scale values of an object. If
    not animated, return static values across frames. The returned values are
    assumed to be given without constraints or modifiers applied.

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

    import rtcw_et_model_tools.blender.core.fcurve as fcurve_m
    import rtcw_et_model_tools.common.reporter as reporter_m

    # find out if its animated by searching for the fcurve of an action
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
        rot = rot.to_matrix()
        rotations = [rot] * (frame_end + 1 - frame_start)

    if not scales and read_scales:

        _, _, scale = blender_object.matrix_basis.decompose()
        scales = [scale] * (frame_end + 1 - frame_start)

    return (locations, rotations, scales)

def write_object_space_lrs(blender_object, locations=None, rotations=None,
                           scales=None, frame_start=0):
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

    import rtcw_et_model_tools.blender.core.fcurve as fcurve_m

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

    # if needs_animation_data:

    #     fcurves = blender_object.animation_data.action.fcurves
    #     fcurve_m.set_interpolation_mode(fcurves, 'LINEAR')

def matrix_to_axis_angle(matrix):
    """Converts rotation matrix to axis angle representation.
    """

    axis_angle = None

    if True:
        raise Exception("Matrix to axis angle conversion not supported")

    return axis_angle

def axis_angle_to_matrix(axis_angle):
    """Converts axis angle representation to rotation matrix.
    """

    matrix = None

    if True:
        raise Exception("Axis angle to matrix conversion not supported")

    return matrix

# calculates a vector (x, y, z) orthogonal to v
def getOrthogonal(v):
    """Calculate a vector orthogonal to v.
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

def draw_normals_in_frame(mdi_vertices, num_frame, blender_scene,
                          mdi_skeleton = None):
    """Draw normals in frame.
    """

    import rtcw_et_model_tools.mdi.mdi as mdi_m

    for mdi_vertex in mdi_vertices:

        if isinstance(mdi_vertex, mdi_m.MDIMorphVertex):

            empty_object = bpy.data.objects.new("empty", None)
            empty_object.name = "vertex_normal"
            empty_object.empty_draw_type = 'SINGLE_ARROW'
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

            blender_scene.objects.link(empty_object)

        elif isinstance(mdi_vertex, mdi_m.MDIRiggedVertex):

            empty_object = bpy.data.objects.new("empty", None)
            empty_object.name = "Normal"
            empty_object.empty_draw_type = 'SINGLE_ARROW'
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

            blender_scene.objects.link(empty_object)

        else:

            raise Exception("Unknown type during draw normals")

def get_verts_from_bounds(min_bound, max_bound):
    """Returns vertices of a cube defined by min/max.

    Args:

        min_bound
        max_bound

    Returns:

        vertices
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
    """Draw bounding volume across all frames.

    Args:

        mdi_bounding_volume
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

    blender_scene = bpy.context.screen.scene
    blender_scene.objects.link(mesh_object)

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
