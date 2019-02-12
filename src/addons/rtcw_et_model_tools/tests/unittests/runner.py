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

import rtcw_et_model_tools.tests.unittests.test_read_write


def run():
    """Runs the specified unit tests.
    """

    def create_standard_test_suite():
        """Creates a suite of unit tests.
        """

        suite = unittest.TestSuite()

        suite.addTest(
            rtcw_et_model_tools.tests.unittests. \
                test_read_write.TestReadWrite('test_binary_read_write')
            )

        return suite

    runner = unittest.TextTestRunner()
    runner.run(create_standard_test_suite())
