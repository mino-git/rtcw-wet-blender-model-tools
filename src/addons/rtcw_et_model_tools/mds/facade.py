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

"""Facade for MDS file format.
"""

import rtcw_et_model_tools.mds._mds as mds
import rtcw_et_model_tools.mds._mds_mdi as mds_mdi


def read(file_path, bind_frame, encoding="binary"):

    """Reads MDS data from file, then converts it to MDI.

    Args:

        file_path (str): path to MDS file.
        bind_frame (int): bind frame used for skinning.
        encoding (str): encoding to use for MDS.

    Returns:

        mdi (MDI): converted MDS data as MDI.
    """

    if encoding == "binary":
        mds_model = mds.MDS.read(file_path)
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        print("encoding option '{}' not supported".format(encoding))

    mdi_model = mds_mdi.ModelToMDI.convert(mds_model, bind_frame)

    return mdi_model


# def write(mdi_model, file_path, encoding="binary"):

#     """Converts MDI data to MDS, then writes it back to file.

#     Args:
#         mdi (MDI): model definition interchange format.
#         file_path (str): path to which MDS data is written to.
#         encoding (str): encoding to use for MDS.
#     """

#     mds_model = mds_mdi.MDIToModel.convert(mdi_model)

#     if encoding == "binary":
#         mds_model.write(file_path)
#     elif encoding == "xml":
#         pass  # TODO
#     elif encoding == "json":
#         pass  # TODO
#     else:
#         print("encoding option '{}' not supported".format(encoding))
