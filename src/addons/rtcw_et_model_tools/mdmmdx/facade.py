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

from mdmmdx import _mdm
from mdmmdx import _mdx
from mdmmdx import _mdmmdx_mdi


def read(file_path_mdm, file_path_mdx, encoding="binary"):
    """Reads MDM/MDX data from file, then converts it to MDI.

    Args:

        file_path_mdm (str): path to MDM file.
        file_path_mdx (str): path to MDX file.
        encoding (str): encoding to use for MDM/MDX.

    Notes:

        Can read MDX without MDM. MDM without MDX is not possible.

    Returns:

        mdi (MDI): converted MDM/MDX data as MDI.
    """

    if encoding == "binary":
        if file_path_mdm is not None:
            mdm = _mdm.MDM.read(file_path_mdm)
        mdx = _mdx.MDX.read(file_path_mdx)
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        print("encoding option '{}' not supported".format(encoding))

    mdi = _mdmmdx_mdi.convert_to_mdi(mdm, mdx)

    return mdi


def write(mdi, file_path_mdm, file_path_mdx, encoding="binary"):
    """Converts MDI data to MDM/MDX, then writes it back to file.

    Args:
        mdi (MDI): model definition interchange format.
        file_path_mdm (str): path to which MDM data is written to.
        file_path_mdx (str): path to which MDX data is written to.
        encoding (str): encoding to use for MDS.
    """

    mds = _mds_mdi.convert_from_mdi(mdi)

    if encoding == "binary":
        mds.write(file_path)
    elif encoding == "xml":
        pass  # TODO
    elif encoding == "json":
        pass  # TODO
    else:
        print("encoding option '{}' not supported".format(encoding))
