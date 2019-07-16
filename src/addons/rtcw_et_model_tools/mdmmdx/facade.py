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

"""Facade for MDM and MDX file format.
"""

import rtcw_et_model_tools.mdmmdx._mdm as mdm_m
import rtcw_et_model_tools.mdmmdx._mdx as mdx_m
import rtcw_et_model_tools.mdmmdx._mdmmdx_mdi as mdmmdx_mdi_m


def read(file_path_mdm, file_path_mdx, bind_frame, encoding="binary"):
    """Reads MDM/MDX data from file, then converts it to MDI.

    Args:

        file_path_mdm (str): path to MDM file.
        file_path_mdx (str): path to MDX file.
        bind_frame (int): bind frame used for skinning.
        encoding (str): encoding to use for MDM/MDX.

    Notes:

        Can read MDX without MDM. MDM without MDX is not possible.

    Returns:

        mdi_model (MDI): converted MDM/MDX data as MDI.
    """

    if encoding == "binary":
        mdx_model = mdx_m.MDX.read(file_path_mdx)
        if file_path_mdm:
            mdm_model = mdm_m.MDM.read(file_path_mdm)
        else:
            mdm_model = None
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        print("encoding option '{}' not supported".format(encoding))

    mdi_model = \
        mdmmdx_mdi_m.ModelToMDI.convert(mdx_model, mdm_model, bind_frame)

    return mdi_model


def write(mdi_model, file_path_mdm, file_path_mdx, encoding="binary"):
    """Converts MDI data to MDM/MDX, then writes it back to file.

    Args:
        mdi (MDI): model definition interchange format.
        file_path_mdm (str): path to which MDM data is written to.
        file_path_mdx (str): path to which MDX data is written to.
        encoding (str): encoding to use for MDS.
    """

    mdx_model, mdm_model = mdmmdx_mdi_m.MDIToModel.convert(mdi_model)

    if encoding == "binary":
        mdx_model.write(file_path_mdx)
        mdm_model.write(file_path_mdm)
        pass
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        print("encoding option '{}' not supported".format(encoding))
