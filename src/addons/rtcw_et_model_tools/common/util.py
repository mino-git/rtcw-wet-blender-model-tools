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

"""Common utils.
"""

import os

def abs_path_to_game_path_rel(game_path, abs_path):
    """Creates a relative path starting from the game_path.

    Args:

        game_path
        abs_path

    Returns:

        new_paths
    """

    if not game_path or not abs_path:
        return None

    rel_path = None

    i = abs_path.find(game_path)
    if i != -1 and i == 0:

        rel_path = abs_path[len(game_path):]

    return rel_path

def join_rel_paths_with_path(path, rel_paths):
    """Take a list of relative paths and joins them to path.

    Args:

        path
        rel_paths

    Returns:

        new_paths
    """

    new_paths = []

    for rel_path in rel_paths:

        new_path = os.path.join(path, rel_path)
        new_paths.append(new_path)

    return new_paths

def create_exts(name, exts, include_stripped = False):
    """Takes a name and returns a formatted list of strings with the intended
    suffixes. Format = <name>.<ext>.
    """

    names = []

    i = name.find(".")
    if i != -1:
        name = name[0:i]

    if include_stripped:
        names.append(name)

    for ext in exts:
        names.append("{}.{}".format(name, ext))

    return names


