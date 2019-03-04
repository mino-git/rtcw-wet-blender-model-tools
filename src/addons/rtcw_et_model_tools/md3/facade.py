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

"""Facade for MD3 file format.
"""

import rtcw_et_model_tools.md3._md3 as md3
import rtcw_et_model_tools.md3._md3_mdi as md3_mdi


def read(file_path, encoding="binary"):

    """Reads MD3 data from file, then converts it to MDI.

    Args:

        file_path (str): path to MD3 file.
        encoding (str): encoding to use for MD3.

    Returns:

        mdi (MDI): converted MD3 data as MDI.
    """

    if encoding == "binary":
        md3_model = md3.MD3.read(file_path)
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        print("encoding option '{}' not supported".format(encoding))

    mdi_model = md3_mdi.ModelToMDI.convert(md3_model)

    return mdi_model


def write(mdi, file_path, encoding="binary"):

    """Converts MDI data to MD3, then writes it back to file.

    Args:
        mdi (MDI): model definition interchange format.
        file_path (str): path to which MD3 data is written to.
        encoding (str): encoding to use for MD3.
    """

    md3_model = md3_mdi.convert_from_mdi(mdi_model)

    if encoding == "binary":
        md3_model.write(file_path)
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        print("encoding option '{}' not supported".format(encoding))
