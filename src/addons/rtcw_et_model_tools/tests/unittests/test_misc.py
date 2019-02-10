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


import unittest
import os
import hashlib

import rtcw_et_model_tools.md3._md3 as md3


class TestMisc(unittest.TestCase):

    working_directory = "."

    def test_rand(self):
        """Random Test
        """

        file_path_in = os.path.abspath("{}/in/{}".format(self.working_directory, "head.md3"))
        file_path_out = os.path.abspath("{}/out/{}".format(self.working_directory, "head.md3"))

        md3_model = md3.MD3.read(file_path_in)
        md3_model.write(file_path_out)


    def test_allied_engineer(self):
        """Test all models of the allied engineer.
        1 pass: read/write.
        2 pass: read from file/convert to mdi/convert back/write back to file.
        3 pass: full cycle from file to blender and back to file.
        """

        pass
