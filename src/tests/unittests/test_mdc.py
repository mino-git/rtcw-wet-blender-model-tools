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

import mdc._mdc


class TestMDC(unittest.TestCase):

    def test_read_write(self):

        file_paths = {
            "./tests/testmodels/in/head.mdc":
                "./tests/testmodels/out/head.mdc",
            "./tests/testmodels/in/helmut.mdc":
                "./tests/testmodels/out/helmut.mdc",
            "./tests/testmodels/in/thompson.mdc":
                "./tests/testmodels/out/thompson.mdc"
        }

        for file_path_in, file_path_out in file_paths.items():

            file_path_in = os.path.abspath(file_path_in)
            file_path_out = os.path.abspath(file_path_out)

            mdc_model = mdc._mdc.MDC.read(file_path_in)
            mdc_model.write(file_path_out)

            hasher = hashlib.new('sha1')
            with open(file_path_in, 'rb') as file:

                hasher.update(file.read())
                hash_sum_in = hasher.hexdigest()

            hasher = hashlib.new('sha1')
            with open(file_path_out, 'rb') as file:

                hasher.update(file.read())
                hash_sum_out = hasher.hexdigest()

            self.assertEqual(hash_sum_in, hash_sum_out)