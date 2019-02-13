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

# <pep8-80  compliant>

"""Tests using the unittest module.
"""

import unittest
import sys

import rtcw_et_model_tools.tests.unittests.test_read_write


class TestParameters:
    """Used for passing parameters.
    """

    parameters = None

    def __init__(self, test_directory=None):

        self.test_directory = test_directory


class TestManager:
    """Used to coordinate tests.
    """

    @staticmethod
    def run_test(test_name, parameters=None):
        """Runs the specified unit tests.
        """

        TestParameters.parameters = parameters

        suite = unittest.TestSuite()

        if test_name == "":

            pass

        elif test_name == "test_binary_read_write":

            suite.addTest(
               rtcw_et_model_tools.tests.unittests.test_read_write. \
                   TestReadWrite('test_binary_read_write')
            )

        else:

            pass

        unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
