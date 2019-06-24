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
import os

import rtcw_et_model_tools.md3.facade as md3_facade
import rtcw_et_model_tools.mdc.facade as mdc_facade
import rtcw_et_model_tools.mds.facade as mds_facade
import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade
import rtcw_et_model_tools.blender.scene as blender_scene

import rtcw_et_model_tools.tests.test_manager as test_manager


class TestDirectConversion(unittest.TestCase):
    """Direct Conversion Test.
    """

    def setUp(self):

        test_directory = test_manager.TestParameters.parameters.test_directory
        if not test_directory:
            test_directory = "."
        test_directory = os.path.abspath(test_directory)
        test_manager.TestParameters.parameters.test_directory = test_directory

        self.old_working_directory = os.getcwd()
        os.chdir(test_manager.TestParameters.parameters.test_directory)

    def tearDown(self):

        os.chdir(self.old_working_directory)

    def test_direct_conversion(self):
        """Tests direct conversion.

        The model definitions are located in a test directory. The test scans
        this directory for any files specified in the suffix_handler_dict. Then
        it reads the found files, converts them to mdi, and converts them back
        to all possible formats. The results will land in a directory. After
        this is done, the results will be loaded into blender for visual
        comparison.
        """

        test_directory = test_manager.TestParameters.parameters.test_directory
        to_md3 = test_manager.TestParameters.parameters.to_md3
        to_mdc = test_manager.TestParameters.parameters.to_mdc
        to_mds = test_manager.TestParameters.parameters.to_mds
        to_mdmmdx = test_manager.TestParameters.parameters.to_mdmmdx

        dir_list = \
            os.listdir(test_manager.TestParameters.parameters.test_directory)

        out_dir = os.path.join(test_directory, "out")
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        for file in dir_list:

            file_path = os.path.abspath(file)

            if file_path.endswith(".md3") and os.path.isfile(file_path):

                # to md3
                if to_md3:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".md3"
                    file_path_out = os.path.join(out_dir, file_out)
                    md3_facade.write(mdi_model, file_path_out)

                # to mdc
                if to_mdc:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".mdc"
                    file_path_out = os.path.join(out_dir, file_out)
                    mdc_facade.write(mdi_model, file_path_out)

                # to mds
                pass  # not supported

                # to mdm/mdx
                pass  # not supported

            elif file_path.endswith(".mdc") and os.path.isfile(file_path):

                # to md3
                if to_md3:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".md3"
                    file_path_out = os.path.join(out_dir, file_out)
                    md3_facade.write(mdi_model, file_path_out)

                # to mdc
                if to_mdc:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".mdc"
                    file_path_out = os.path.join(out_dir, file_out)
                    mdc_facade.write(mdi_model, file_path_out)

                # to mds
                pass  # not supported

                # to mdm/mdx
                pass  # not supported

            elif file_path.endswith(".mds") and os.path.isfile(file_path):

                # to md3
                if to_md3:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".md3"
                    file_path_out = os.path.join(out_dir, file_out)
                    md3_facade.write(mdi_model, file_path_out)

                # to mdc
                if to_mdc:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".mdc"
                    file_path_out = os.path.join(out_dir, file_out)
                    mdc_facade.write(mdi_model, file_path_out)

                # to mds
                if to_mds:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".mds"
                    file_path_out = os.path.join(out_dir, file_out)
                    mds_facade.write(mdi_model, file_path_out)

                # to mdm/mdx
                if to_mdmmdx:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out_mdm = file[0:-4] + ".mdm"
                    file_out_mdx = file[0:-4] + ".mdx"
                    file_path_out_mdm = os.path.join(out_dir, file_out_mdm)
                    file_path_out_mdx = os.path.join(out_dir, file_out_mdx)
                    mdmmdx_facade.write(mdi_model, file_path_out_mdx,
                                        file_path_out_mdm)

            elif file_path.endswith(".mdm") and os.path.isfile(file_path):

                # to md3
                if to_md3:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".md3"
                    file_path_out = os.path.join(out_dir, file_out)
                    md3_facade.write(mdi_model, file_path_out)

                # to mdc
                if to_mdc:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".mdc"
                    file_path_out = os.path.join(out_dir, file_out)
                    mdc_facade.write(mdi_model, file_path_out)

                # to mds
                if to_mds:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out = file[0:-4] + ".mds"
                    file_path_out = os.path.join(out_dir, file_out)
                    mds_facade.write(mdi_model, file_path_out)

                # to mdm/mdx
                if to_mdmmdx:
                    mdi_model = mds_facade.read(file_path, 0)
                    file_out_mdm = file[0:-4] + ".mdm"
                    file_out_mdx = file[0:-4] + ".mdx"
                    file_path_out_mdm = os.path.join(out_dir, file_out_mdm)
                    file_path_out_mdx = os.path.join(out_dir, file_out_mdx)
                    mdmmdx_facade.write(mdi_model, file_path_out_mdx,
                                        file_path_out_mdm)
