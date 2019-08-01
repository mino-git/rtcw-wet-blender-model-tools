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


import bpy


def register():

    import rtcw_et_model_tools.common.reporter as reporter_m

    import rtcw_et_model_tools.blender.ui.imports as imports_m
    import rtcw_et_model_tools.blender.ui.exports as exports_m
    import rtcw_et_model_tools.blender.ui.direct_conversion as direct_conversion_m
    import rtcw_et_model_tools.blender.ui.attachment as attachment_m
    import rtcw_et_model_tools.blender.ui.shading as shading_m
    import rtcw_et_model_tools.blender.ui.unzip_pk3s as unzip_pk3s_m

    reporter_m.init()

    bpy.types.Scene.remt_game_path = \
        bpy.props.StringProperty(
            name="Game Path",
            description="Path to game data. Game data will be read assuming"
                " this is the directory of the mod file (for example"
                " 'etmain' or 'Main'. Note: PK3 files are not extracted, so"
                " you need to manually extract them to this directory."
                " You can use the 'Unzip PK3s' panel for that.",
            subtype='DIR_PATH')

    imports_m.register()
    exports_m.register()
    direct_conversion_m.register()
    attachment_m.register()
    shading_m.register()
    unzip_pk3s_m.register()

def unregister():

    import rtcw_et_model_tools.common.reporter as reporter_m

    import rtcw_et_model_tools.blender.ui.imports as imports_m
    import rtcw_et_model_tools.blender.ui.exports as exports_m
    import rtcw_et_model_tools.blender.ui.direct_conversion as \
           direct_conversion_m
    import rtcw_et_model_tools.blender.ui.attachment as attachment_m
    import rtcw_et_model_tools.blender.ui.shading as shading_m
    import rtcw_et_model_tools.blender.ui.unzip_pk3s as unzip_pk3s_m

    reporter_m.deinit()

    del bpy.types.Scene.remt_game_path

    imports_m.unregister()
    exports_m.unregister()
    direct_conversion_m.unregister()
    attachment_m.unregister()
    shading_m.unregister()
    unzip_pk3s_m.unregister()
