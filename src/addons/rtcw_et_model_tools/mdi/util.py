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

"""MDI utility functions, mostly strings and math.
"""

import math
import mathutils


# =====================================
# string
# =====================================

def to_c_string_padded(src_str, target_len):
    """Converts to a padded c string.

    Args:

        TODO

    Returns:

        TODO
    """

    if len(src_str) < target_len:

        num_chars_to_pad = target_len - len(src_str)
        zeros = '\0' * num_chars_to_pad
        src_str += zeros

    c_string_padded = src_str.encode(encoding = 'ascii', errors = 'strict')
    return c_string_padded

def from_c_string_padded(c_string_padded):
    """Converts to a python string.

    Args:

        TODO

    Returns:

        TODO
    """

    pad_start = c_string_padded.find(b"\x00")
    if pad_start != -1:
        c_string_padded = c_string_padded[0:pad_start]

    return str(object = c_string_padded, encoding = 'utf-8', errors = 'strict')

# =====================================
# direction
# =====================================

def rotate_up_vector(yaw, pitch):
    """Rotate the up vector. First pitch, then yaw (intrinsic).

    Args:

        yaw (int): yaw angle in degrees.
        pitch (int): pitch angle in degrees.

    Returns:

        _ (tuple): coordinates of rotated up vector.
    """

    yaw = math.radians(yaw)
    pitch = math.radians(pitch)

    sp = math.sin(pitch)
    cp = math.cos(pitch)
    sy = math.sin(yaw)
    cy = math.cos(yaw)

    x = cy * sp
    y = sy * sp
    z = cp

    return (x, y, z)


def rotate_forward_vector(yaw, pitch):
    """Rotate the forward vector. First pitch, then yaw (intrinsic).

    Args:

        yaw (int): yaw angle in degrees.
        pitch (int): pitch angle in degrees.

    Returns:

        _ (tuple): coordinates of rotated forward vector.
    """

    yaw = math.radians(yaw)
    pitch = math.radians(pitch)

    sp = math.sin(pitch)
    cp = math.cos(pitch)
    sy = math.sin(yaw)
    cy = math.cos(yaw)

    x = cy * cp
    y = sy * cp
    z = -sp

    return (x, y, z)

def angles_from_up_vector(vec):
    """Determine pitch and yaw rotation from up vector to target vector.
    First pitch, then yaw (intrinsic).

    Args:

        vec (int): target vector.

    Returns:

        _ (tuple): angles in degrees from up vector to target vector.
        Index 0 = yaw, index 1 = pitch.
    """

    yaw = 0
    pitch = 0

    vec = vec.normalized()

    yaw = math.degrees(yaw)
    pitch = math.degrees(pitch)

    # we can read cos pitch directly from the direction vector
    cp = vec[2]

    if cp <= -1.0:

        yaw = 0
        pitch = math.pi

    elif cp >= 1.0:

        yaw = 0
        pitch = 0

    else:

        off_x = vec[0]
        off_y = vec[1]

        yaw = math.atan2(off_y, off_x)
        pitch = math.acos(cp)

    yaw = math.degrees(yaw)
    pitch = math.degrees(pitch)

    return (yaw, pitch)

def angles_from_forward_vector(vec):
    """Determine pitch and yaw rotation from forward vector to target vector.
    First pitch, then yaw (intrinsic).

    Args:

        vec (int): target vector.

    Returns:

        _ (tuple): angles in degrees from forward vector to target vector.
        Index 0 = yaw, index 1 = pitch.
    """

    yaw = 0
    pitch = 0

    vec = vec.normalized()

    # we can read sin pitch directly from the direction vector
    sp = -(vec[2])

    # fp arithmetic can cause slight imprecision
    if sp <= -1.0:

        pitch = -math.pi / 2

    elif sp >= 1.0:

        pitch = math.pi / 2

    else:

        pitch = math.asin(sp)

    # pitch is known, we can calculate cos pitch
    cp = math.cos(pitch) # [0, 1]

    # TODO math.fabs()
    if cp > 0.00001: # catch fp arithmetic imprecision

        # with known cos pitch, we can calculate yaw
        off_x = vec[0]
        off_y = vec[1]
        # we can avoid division by cp by using properties of atan2
        # and the given range of values el. [0, 1]
        yaw = math.atan2(off_y, off_x) # yaw = math.atan2(offY/cp, offX/cp)

    else: # because of division by zero we can not use cos pitch here

        # if cp == 0 => pitch either +90 or -90
        yaw = 0 # just set yaw to 0, since it does not affect the direction

    yaw = math.degrees(yaw)
    pitch = math.degrees(pitch)

    return (yaw, pitch)

# =====================================
# orientation
# =====================================

def matrix_to_tuple(matrix):

    # TODO
    # forward_x, left_x, up_x = matrix[0]
    # forward_y, left_y, up_y = matrix[1]
    # forward_z, left_z, up_z = matrix[2]

    forward_x = matrix[0][0]
    forward_y = matrix[1][0]
    forward_z = matrix[2][0]

    left_x = matrix[0][1]
    left_y = matrix[1][1]
    left_z = matrix[2][1]

    up_x = matrix[0][2]
    up_y = matrix[1][2]
    up_z = matrix[2][2]

    return (forward_x, forward_y, forward_z,
            left_x, left_y, left_z,
            up_x, up_y, up_z)

def tuple_to_matrix(orientation):

    forward_x = orientation[0]
    forward_y = orientation[1]
    forward_z = orientation[2]

    left_x = orientation[3]
    left_y = orientation[4]
    left_z = orientation[5]

    up_x = orientation[6]
    up_y = orientation[7]
    up_z = orientation[8]

    matrix = mathutils.Matrix.Identity(3)
    matrix[0][0:3] = forward_x, left_x, up_x
    matrix[1][0:3] = forward_y, left_y, up_y
    matrix[2][0:3] = forward_z, left_z, up_z

    return matrix

def angles_to_matrix(yaw, pitch, roll):
    """Construct a rotation matrix from Tait-Bryan angles. Rotation order is:
    roll, pitch, yaw (intrinsic).

    Notes:

        Coordinate space handedness: right handed, x = forward (roll axis),
        y = left (pitch axis), z = up = (yaw axis)

        The resulting matrix represents an active rotation matrix and is meant
        to pre-multiply column vectors. Also see:
        https://en.wikipedia.org/wiki/Euler_angles#Rotation_matrix

    Attributes:

        yaw (int): yaw angle in degrees.
        pitch (int): pitch angle in degrees.
        roll (int): roll angle in degrees.

    Args:

        matrix (mathutils.Matrix): rotational difference to the target
            orientation given in model space coordinates. It's columns
            represent the basis vectors of another coordinate system.
    """

    yaw = math.radians(yaw)
    pitch = math.radians(pitch)
    roll = math.radians(roll)

    sy = math.sin(yaw)
    cy = math.cos(yaw)

    sp = math.sin(pitch)
    cp = math.cos(pitch)

    sr = math.sin(roll)
    cr = math.cos(roll)

    forward_x = cp * cy
    forward_y = cr * (-sy) + sr * sp * cy
    forward_z = (-sr) * (-sy) + cr * sp * cy

    left_x = cp * sy
    left_y = cr * cy + sr * sp * sy
    left_z = (-sr) * cy + cr * sp * sy

    up_x = (-sp)
    up_y = sr * cp
    up_z = cr * cp

    matrix = mathutils.Matrix.Identity(3)
    matrix[0][0:3] = forward_x, left_x, up_x # first row
    matrix[1][0:3] = forward_y, left_y, up_y # second row
    matrix[2][0:3] = forward_z, left_z, up_z # third row

    return matrix

# def angles_to_matrix(yaw, pitch, roll):
#     """Construct a rotation matrix from Tait-Bryan angles. Rotation order is:
#     roll, pitch, yaw (intrinsic).

#     Notes:

#         Coordinate space handedness: right handed, x = forward (roll axis),
#         y = left (pitch axis), z = up = (yaw axis)

#         The resulting matrix represents an active rotation matrix and is meant
#         to pre-multiply column vectors. Also see:
#         https://en.wikipedia.org/wiki/Euler_angles#Rotation_matrix

#     Attributes:

#         yaw (int): yaw angle in degrees.
#         pitch (int): pitch angle in degrees.
#         roll (int): roll angle in degrees.

#     Args:

#         matrix (mathutils.Matrix): rotational difference to the target
#             orientation given in model space coordinates. It's columns
#             represent the basis vectors of another coordinate system.
#     """

#     yaw = math.radians(yaw)
#     pitch = math.radians(pitch)
#     roll = math.radians(roll)

#     sy = math.sin(yaw)
#     cy = math.cos(yaw)

#     sp = math.sin(pitch)
#     cp = math.cos(pitch)

#     sr = math.sin(roll)
#     cr = math.cos(roll)

#     forward_x = cy * cp
#     forward_y = sy * cp
#     forward_z = -sp

#     left_x = cy * sp * sr + (-sy) * cr
#     left_y = sy * sp * sr + cy * cr
#     left_z = cp * sr

#     up_x = cy * sp * cr + (-sy) * (-sr)
#     up_y = sy * sp * cr + cy * (-sr)
#     up_z = cp * cr

#     matrix = mathutils.Matrix.Identity(3)
#     matrix[0][0:3] = forward_x, left_x, up_x # first row
#     matrix[1][0:3] = forward_y, left_y, up_y # second row
#     matrix[2][0:3] = forward_z, left_z, up_z # third row

#     matrix = matrix.transposed()  # TODO

#     return matrix

def matrix_to_angles(matrix):
    """TODO

    Huge thanks to Fletcher Dunn and Ian Parberry for their method
    For a full explanation, see their book:
    3D math primer for graphics and game development, 2nd edition, p. 278
    """

    roll = 0
    pitch = 0
    yaw = 0

    # we can read sin pitch directly from the matrix
    sp = -(matrix[0][2])

    # fp arithmetic can cause slight imprecision
    if sp <= -1.0:

        pitch = -math.pi / 2

    elif sp >= 1.0:

        pitch = math.pi / 2

    else:

        pitch = math.asin(sp)

    # pitch is known, we can calculate cos pitch
    cp = math.cos(pitch) # [0, 1]

    # TODO math.fabs()
    if cp > 0.00001: # catch fp arithmetic imprecision

        # with known cos pitch, we can calculate yaw
        m00 = matrix[0][0]
        m01 = matrix[0][1]
        # we can avoid division by cp by using properties of atan2
        # and the given range of values el. [0, 1]
        yaw = math.atan2(m01, m00) # yaw = math.atan2(m01/cp, m00/cp)

        # with known cos pitch, we can calculate roll
        m12 = matrix[1][2]
        m22 = matrix[2][2]
        roll = math.atan2(m12, m22) # roll = math.atan2(m12/cp, m22/cp)

    else: # because of division by zero we can not use cos pitch here

        # if cp == 0 => pitch either +90 or - 90 => gimbal lock situation
        roll = 0 # just set roll to 0

        # sin yaw and cos yaw can be read directly from the matrix
        # after the parameters are plugged in: cp == 0 => sr == 0, cr == 1
        m10 = matrix[1][0]
        m11 = matrix[1][1]
        yaw = math.atan2(-m10, m11)

    yaw = math.degrees(yaw)
    pitch = math.degrees(pitch)
    roll = math.degrees(roll)

    return (yaw, pitch, roll)

# =====================================
# normal
# =====================================

# TODO
