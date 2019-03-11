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


class Status:
    """Used for reporting back warnings and errors.

    Attributes:

        was_canceled (bool): indicates an error.
        cancel_msg (str): cancel message.
        warning_msgs (list): a list of strings for warnings.
    """

    def __init__(self):

        self.was_canceled = False
        self.cancel_msg = ""
        self.warning_msgs = []

    def set_canceled(self, cancel_msg):

        self.was_canceled = True
        self.cancel_msg = cancel_msg

    def add_warning_msg(self, warning_msg):

        self.warning_msgs.append(warning_msg)

    def prepare_report(self):

        cancel_report = ""
        if self.was_canceled:
            cancel_report = "Cancelled. Reason: {}.".format(self.cancel_msg)

        warning_report = ""
        for warning_msg in self.warning_msgs:
            warning_report = \
                "{} Warning: {}.".format(warning_report, warning_msg)

        return (cancel_report, warning_report)


def angles_to_vector(yaw, pitch):

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

    vector = mathutils.Vector((x, y, z))

    return vector

def euler_to_matrix(yaw, pitch, roll):

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
    forward_x = cy * cp
    forward_y = sy * cp
    forward_z = -sp

    left_x = cy * sp * sr + (-sy) * cr
    left_y = sy * sp * sr + cy * cr
    left_z = cp * sr

    up_x = cy * sp * cr + (-sy) * (-sr)
    up_y = sy * sp * cr + cy * (-sr)
    up_z = cp * cr

    matrix = mathutils.Matrix().Identity(3)
    matrix[0][0:3] = forward_x, left_x, up_x # first row
    matrix[1][0:3] = forward_y, left_y, up_y # second row
    matrix[2][0:3] = forward_z, left_z, up_z # third row

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
