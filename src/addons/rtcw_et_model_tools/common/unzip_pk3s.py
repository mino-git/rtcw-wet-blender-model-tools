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

"""Unzip PK3s (game data).
"""

import os
import zipfile


def unzip_dir_recursive(source_path, target_path):
    """Search directory recursively and extract all pk3 files to a destination
    directory.
    """

    if not os.path.isdir(source_path):
        raise Exception("Source directory not found")

    if not os.path.isdir(target_path):
        raise Exception("Target directory not found")

    for root, _, files in os.walk(source_path, topdown=False):

            for file_path in files:

                if file_path.endswith(".pk3"):

                    path_to_pk3_file = os.path.join(root, file_path)
                    zip_ref = zipfile.ZipFile(path_to_pk3_file, 'r')
                    zip_ref.extractall(target_path)
                    zip_ref.close()
