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

import unittest

import rtcw_et_model_tools.tests.unittests.test_md3 as test_md3
import rtcw_et_model_tools.tests.unittests.test_mdc as test_mdc
import rtcw_et_model_tools.tests.unittests.test_mds as test_mds
import rtcw_et_model_tools.tests.unittests.test_mdm as test_mdm
import rtcw_et_model_tools.tests.unittests.test_mdx as test_mdx
import rtcw_et_model_tools.tests.unittests.test_misc as test_misc


def run():

    def create_standard_test_suite():

        suite = unittest.TestSuite()

        suite.addTest(test_misc.TestMisc('test_rand'))

        '''
        suite.addTest(test_md3.TestMD3('test_read_write'))
        suite.addTest(test_mdc.TestMDC('test_read_write'))
        suite.addTest(test_mds.TestMDS('test_read_write'))
        suite.addTest(test_mdm.TestMDM('test_read_write'))
        suite.addTest(test_mdx.TestMDX('test_read_write'))
        suite.addTest(test_misc.TestMisc('test_allied_engineer'))
        suite.addTest(test_mds.TestMDS('test_mds_vertex_fixed'))
        '''

        return suite

    # TODO check if the working directory contains a cfg
    # if present, run tests based on cfg

    runner = unittest.TextTestRunner()
    runner.run(create_standard_test_suite())
