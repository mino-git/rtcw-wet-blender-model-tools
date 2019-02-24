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

import mathutils
import math

def offAnglesToOffset(offAngleYaw, offAnglePitch):

      # TODO recheck with source
    location_dir_scale = 360 / 4095.0

    # quantization, angles (short) to degrees (float)
    yaw = (offAngleYaw >> 4) * location_dir_scale
    pitch = (offAnglePitch >> 4) * location_dir_scale

    yaw = math.radians(yaw)
    pitch = math.radians(pitch)

    sp = math.sin(pitch)
    cp = math.cos(pitch)
    sy = math.sin(yaw)
    cy = math.cos(yaw)

    # construct a rotation matrix
    # first pitch, then yaw (intrinsic)
    # +x = forward, +y = left, +z = up, right handed
    # active transform of forward vector gives offset direction in object space
    x = cy * cp
    y = sy * cp
    z = -sp

    offset = mathutils.Vector((x, y, z))

    return offset


def anglesToMatrix(angleYaw, anglePitch, angleRoll):

    orientation_scale = 360 / 65536.0  # TODO recheck with source

    # quantization, angles (short) to degrees (float)
    yaw = angleYaw * orientation_scale
    pitch = anglePitch * orientation_scale
    roll = angleRoll * orientation_scale

    yaw = math.radians(yaw)
    pitch = math.radians(pitch)
    roll = math.radians(roll)

    sy = math.sin(yaw)
    cy = math.cos(yaw)

    sp = math.sin(pitch)
    cp = math.cos(pitch)

    sr = math.sin(roll)
    cr = math.cos(roll)

    # construct a rotation matrix
    # first roll, then pitch, then yaw (intrinsic)
    # +x = forward, +y = left, +z = up, right handed
    # the result is a passive transform matrix expressed in object space
    forwardX = cy * cp
    forwardY = sy * cp
    forwardZ = -sp

    leftX = cy * sp * sr + (-sy) * cr
    leftY = sy * sp * sr + cy * cr
    leftZ = cp * sr

    upX = cy * sp * cr + (-sy) * (-sr)
    upY = sy * sp * cr + cy * (-sr)
    upZ = cp * cr

    matrix = mathutils.Matrix().Identity(3)
    matrix[0][0:3] = forwardX, leftX, upX # first row
    matrix[1][0:3] = forwardY, leftY, upY # second row
    matrix[2][0:3] = forwardZ, leftZ, upZ # third row

    # transform passive to active
    matrix = matrix.transposed() # orthonormal => inverse == transpose

    return matrix


def utf_8_string_to_c_string(utf_8_string):

    b = utf_8_string.encode('ASCII')

    # check for extended ASCII Codes, replace any chars with _
    # to_bytes
    # from_bytes
    # bytes(len=10)
    # isascii
    # bytearray
    # test it

    return b

def c_string_to_utf_8_string(c_string):

    trim_index = c_string.find(b"\x00")
    if trim_index != -1:
        c_string = c_string[0:trim_index]

    utf_string = str(object = c_string, encoding = 'utf-8', errors = 'strict')

    return utf_string
