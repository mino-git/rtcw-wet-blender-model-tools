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

"""Read/Write Tests.
"""


import unittest
import hashlib
import os

import rtcw_et_model_tools.md3._md3 as md3
import rtcw_et_model_tools.mdc._mdc as mdc
import rtcw_et_model_tools.mds._mds as mds
import rtcw_et_model_tools.mdmmdx._mdm as mdm
import rtcw_et_model_tools.mdmmdx._mdx as mdx


class TestReadWrite(unittest.TestCase):
    """Read/Write Tests.
    """

    test_directory = ""

    def setUp(self):

        if not self.test_directory:
            self.test_directory = "."

        self.test_directory = os.path.abspath(self.test_directory)

        self.old_working_directory = os.getcwd()
        os.chdir(self.test_directory)

    def tearDown(self):

        os.chdir(self.old_working_directory)

    def test_binary_read_write(self):
        """Tests the modules binary read/write functions.

        The model definitions are located in a test directory. The test scans
        this directory for any files specified in the test_settings. Then it
        reads the found files to memory and immediately writes them back to a
        new file. The actual test then compares hash values of the original and
        written files.
        """
        print("----------------------------------------")
        print("Running test: test_binary_read_write.")

        test_settings = {
            ".md3": md3.MD3,
            ".mdc": mdc.MDC,
            ".mds": mds.MDS,
            ".mdm": mdm.MDM,
            ".mdx": mdx.MDX,
        }

        dir_list = os.listdir(self.test_directory)

        num_input_file_found = 0
        for suffix, model_handler in test_settings.items():

            # find all test files ending with suffix
            test_files = []
            for file in dir_list:

                file_path = os.path.abspath(file)

                if file_path.endswith(suffix) and os.path.isfile(file_path):

                        test_files.append(file_path)

            # test the files
            for test_file in test_files:

                print("test_binary_read_write={}".format(test_file))
                num_input_file_found += 1

                file_path_in = test_file
                file_path_out = "{}.out".format(test_file)

                # read/write
                model = model_handler.read(file_path_in)
                model.write(file_path_out)

                # compare hash values
                hasher = hashlib.new('sha1')
                with open(file_path_in, 'rb') as file:

                    hasher.update(file.read())
                    hash_sum_in = hasher.hexdigest()

                hasher = hashlib.new('sha1')
                with open(file_path_out, 'rb') as file:

                    hasher.update(file.read())
                    hash_sum_out = hasher.hexdigest()

                with self.subTest(file_path=file_path_in):
                    self.assertEqual(hash_sum_in, hash_sum_out)

        if num_input_file_found == 0:
            print("test_binary_read_write: no input files in directory '{}'" \
                    .format(self.test_directory))

        print("----------------------------------------")
