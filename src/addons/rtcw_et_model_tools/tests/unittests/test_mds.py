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

import rtcw_et_model_tools.mds._mds as mds


class TestMDS(unittest.TestCase):

    def test_read_write(self):

        file_path_in = os.path.abspath("tests/testmodels/in/body.mds")
        file_path_out = os.path.abspath("tests/testmodels/out/body.mds")

        mds_model = mds.MDS.read(file_path_in)
        mds_model.write(file_path_out)

        hasher = hashlib.new('sha1')
        with open(file_path_in, 'rb') as file:

            hasher.update(file.read())
            hash_sum_in = hasher.hexdigest()

        hasher = hashlib.new('sha1')
        with open(file_path_out, 'rb') as file:

            hasher.update(file.read())
            hash_sum_out = hasher.hexdigest()

        self.assertEqual(hash_sum_in, hash_sum_out)

    def test_mds_vertex_fixed(self):
        """Test the fixed_parent and fixed_dist value of all vertices, because
        we expect/assume them to be not used and having the same values in all
        models.
        """

        file_paths = \
            [
                "./tests/testmodels/in/mds/beast.mds",
                "./tests/testmodels/in/mds/bj2.mds",
                "./tests/testmodels/in/mds/dark.mds",
                "./tests/testmodels/in/mds/deathshead1.mds",
                "./tests/testmodels/in/mds/director.mds",
                "./tests/testmodels/in/mds/doc.mds",
                "./tests/testmodels/in/mds/drz.mds",
                "./tests/testmodels/in/mds/eliteguard.mds",
                "./tests/testmodels/in/mds/eva.mds",
                "./tests/testmodels/in/mds/femzombie.mds",
                "./tests/testmodels/in/mds/hans.mds",
                "./tests/testmodels/in/mds/heinrich.mds",
                "./tests/testmodels/in/mds/helga.mds",
                "./tests/testmodels/in/mds/higgs.mds",
                "./tests/testmodels/in/mds/himmler.mds",
                "./tests/testmodels/in/mds/infantryss.mds",
                "./tests/testmodels/in/mds/inge.mds",
                "./tests/testmodels/in/mds/jack.mds",
                "./tests/testmodels/in/mds/loper.mds",
                "./tests/testmodels/in/mds/mechanic.mds",
                "./tests/testmodels/in/mds/murphy.mds",
                "./tests/testmodels/in/mds/officerss.mds",
                "./tests/testmodels/in/mds/partisan.mds",
                "./tests/testmodels/in/mds/priestss.mds",
                "./tests/testmodels/in/mds/protosoldier.mds",
                "./tests/testmodels/in/mds/supersoldier.mds",
                "./tests/testmodels/in/mds/trench.mds",
                "./tests/testmodels/in/mds/venom.mds",
                "./tests/testmodels/in/mds/warrior.mds",
                "./tests/testmodels/in/mds/zemph.mds",
                "./tests/testmodels/in/mds/zombie.mds",
            ]

        for file_path_in in file_paths:

            file_path_in = os.path.abspath(file_path_in)

            mds_model = mds._mds.MDS.read(file_path_in)

            for mds_surface in mds_model.surfaces:

                for mds_vertex in mds_surface.vertices:

                    self.assertEqual(mds_vertex.fixed_parent, 0)
                    self.assertEqual(mds_vertex.fixed_dist, 0.0)
