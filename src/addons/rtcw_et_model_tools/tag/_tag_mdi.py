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

"""Converts between in-memory representations of TAG and MDI.
"""

import mathutils

import rtcw_et_model_tools.tag._tag as tag_m
import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.mdi.util as mdi_util_m

import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


class MDIToModel:
    """MDI to TAG conversion.
    """

    @staticmethod
    def _calc_tag_header(tag_model, mdi_model):

        # tag_model.header
        ident = tag_m.TAGHeader.ident
        version = tag_m.TAGHeader.version

        num_tags = len(tag_model.tags)

        ofs_end = 0 + num_tags * tag_m.TAGData.format_size

        tag_model.header = tag_m.TAGHeader(ident, version, num_tags, ofs_end)

    @staticmethod
    def _to_tag_data(mdi_model, num_tag):

        mdi_free_tag = mdi_model.tags[num_tag]

        # name
        name = mdi_util_m.to_c_string_padded(mdi_free_tag.name,
                                             tag_m.TAGData.name_len)

        # location
        location = mdi_free_tag.locations[0]

        # orientation
        forward = mdi_free_tag.orientations[0].col[1]
        left = mdi_free_tag.orientations[0].col[2]
        up = mdi_free_tag.orientations[0].col[0]

        orientation = mathutils.Matrix.Identity(3)
        orientation[0][0:3] = forward[0], left[0], up[0]
        orientation[1][0:3] = forward[1], left[1], up[1]
        orientation[2][0:3] = forward[2], left[2], up[2]

        orientation = mdi_util_m.matrix_to_tuple(orientation)

        tag_data = tag_m.TAGData(name, location, orientation)

        return tag_data

    @staticmethod
    def convert(mdi_model):
        """Converts MDI to TAG.

        Args:

            mdi_model (MDI): MDI model.

        Returns:

            tag_model (TAG): TAG model.
        """

        timer = timer_m.Timer()
        reporter_m.info("Converting MDI to TAG ...")

        tag_model = tag_m.TAG()

        # type conversions
        mdi_model.tags_to_type(mdi_m.MDIFreeTag)

        # tag_data
        for num_tag in range(len(mdi_model.tags)):

            tag_data = MDIToModel._to_tag_data(mdi_model, num_tag)
            tag_model.tags.append(tag_data)

        # header
        MDIToModel._calc_tag_header(tag_model, mdi_model)

        time = timer.time()
        reporter_m.info("Converting MDI to TAG DONE (time={})".format(time))

        return tag_model


class ModelToMDI:
    """TAG to MDI conversion.
    """

    @staticmethod
    def _to_mdi_tag(tag_model, num_tag):

        tag_data = tag_model.tags[num_tag]

        # name
        name = mdi_util_m.from_c_string_padded(tag_data.name)

        # location
        locations = []
        location = mathutils.Vector(tag_data.location)
        locations.append(location)

        # orientation
        orientations = []
        orientation = mdi_util_m.tuple_to_matrix(tag_data.orientation)

        forward = orientation.col[2]
        left = orientation.col[0]
        up = orientation.col[1]

        orientation = mathutils.Matrix.Identity(3)
        orientation[0][0:3] = forward[0], left[0], up[0]
        orientation[1][0:3] = forward[1], left[1], up[1]
        orientation[2][0:3] = forward[2], left[2], up[2]

        orientations.append(orientation)

        mdi_tag = mdi_m.MDIFreeTag(name, locations, orientations)

        return mdi_tag

    @staticmethod
    def convert(tag_model):
        """Converts TAG to MDI.

        Args:

            tag_model (TAG): TAG model.

        Returns:

            mdi_model (MDI): MDI model.
        """

        timer = timer_m.Timer()
        reporter_m.info("Converting TAG to MDI ...")

        mdi_model = mdi_m.MDI()

        mdi_model.name = "Tag file"
        # mdi_model.root_frame = 0

        # mdi tags
        for num_tag in range(len(tag_model.tags)):

            mdi_tag = ModelToMDI._to_mdi_tag(tag_model, num_tag)
            mdi_model.tags.append(mdi_tag)

        time = timer.time()
        reporter_m.info("Converting TAG to MDI DONE (time={})".format(time))

        return mdi_model
