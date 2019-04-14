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

bl_info = {
    "name": "RtCW/ET Model Tools",
    "author": "Norman Mitschke",
    "version": (0, 9, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "RtCW/ET Model Tools for Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Import-Export",
}

import sys
import logging

import bpy


def register():

    import rtcw_et_model_tools.blender.imports as imports
    import rtcw_et_model_tools.blender.direct_conversion as direct_conversion
    import rtcw_et_model_tools.blender.attach_to_tag as attach_to_tag
    import rtcw_et_model_tools.blender.skin_files as skin_files
    import rtcw_et_model_tools.blender.shading as shading
    import rtcw_et_model_tools.blender.extract_pk3s as extract_pk3s
    import rtcw_et_model_tools.blender.tests as tests

    bpy.types.Scene.remt_data_path = \
        bpy.props.StringProperty(
            name="Datapath",
            description="Path to game data (pk3s need to be extracted" \
                " manually)",
            subtype='DIR_PATH')

    imports.register()
    direct_conversion.register()
    attach_to_tag.register()
    skin_files.register()
    shading.register()
    extract_pk3s.register()
    tests.register()

    logger = logging.getLogger('remt_logger')

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)15s %(levelname)-6s %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

def unregister():

    import rtcw_et_model_tools.blender.imports as imports
    import rtcw_et_model_tools.blender.direct_conversion as direct_conversion
    import rtcw_et_model_tools.blender.attach_to_tag as attach_to_tag
    import rtcw_et_model_tools.blender.skin_files as skin_files
    import rtcw_et_model_tools.blender.shading as shading
    import rtcw_et_model_tools.blender.extract_pk3s as extract_pk3s
    import rtcw_et_model_tools.blender.tests as tests

    del bpy.types.Scene.remt_data_path

    imports.unregister()
    direct_conversion.unregister()
    attach_to_tag.unregister()
    skin_files.unregister()
    shading.unregister()
    extract_pk3s.unregister()
    tests.unregister()

    logger = logging.getLogger('remt_logger')
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
