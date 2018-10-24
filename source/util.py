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


"""Some random utility functions.
"""

import math
import re

class Util:

    nums = re.compile(r'\.\d{3}$')

    def cleanupString(str):
        str = str.decode('utf-8', errors='ignore')
        i = str.find('\x00')
        if i != -1:
            str = str[0:i]
        return str

    def prepare_name(name, suffixChar, intendedNameLen):

        if Util.nums.findall(name):

            name = name[:-4] # cut off blender's .001 .002 etc

        if suffixChar != None and len(name) < intendedNameLen:

            lenToEnd = intendedNameLen - len(name)
            suffix = suffixChar * lenToEnd

            name = name + suffix

        name = name.encode('utf-8')

        # TODO if name too big

        return name

    def getOrthogonal(v):

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
