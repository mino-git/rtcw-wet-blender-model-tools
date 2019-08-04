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

"""Facade for TAG file format.
"""

import pathlib

import rtcw_et_model_tools.tag._tag as tag_m
import rtcw_et_model_tools.tag._tag_mdi as tag_mdi_m


def read(file_path, encoding="binary"):

    """Reads TAG data from file, then converts it to MDI.

    Args:

        file_path (str): path to TAG file.
        encoding (str): encoding to use for TAG.

    Returns:

        mdi_model (MDI): converted TAG data as MDI.
    """

    if encoding == "binary":
        tag_model = tag_m.TAG.read(file_path)
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        exception_string = \
            "Encoding option '{}' not supported".format(encoding)
        raise Exception(exception_string)

    mdi_model = tag_mdi_m.ModelToMDI.convert(tag_model)

    # TODO this shouldn't be here
    if not mdi_model.name:
        mdi_model.name = pathlib.Path(file_path).name

    return mdi_model


def write(mdi_model, file_path, encoding="binary"):

    """Converts MDI data to TAG, then writes it back to file.

    Args:
        mdi_model (MDI): model definition interchange format.
        file_path (str): path to which TAG data is written to.
        encoding (str): encoding to use for TAG.
    """

    tag_model = tag_mdi_m.MDIToModel.convert(mdi_model)

    if encoding == "binary":
        tag_model.write(file_path)
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        exception_string = \
            "Encoding option '{}' not supported".format(encoding)
        raise Exception(exception_string)
