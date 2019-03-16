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

"""Extract PK3s (game data).
"""

import os
import zipfile

import bpy


# UI
# ==============================

class ExtractPK3sPanel(bpy.types.Panel):
    """Panel for extract pk3 operation.
    """

    bl_label = "Extract PK3s"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene,
                "remt_extract_pk3_source_path")

        row = layout.row()
        row.prop(context.scene,
                "remt_extract_pk3_target_path")

        row = layout.row()
        row.operator("remt.remt_extract_pk3",
                     text="Extract",
                     icon="DISK_DRIVE")


# Operators
# ==============================

class ExtractPK3s(bpy.types.Operator):
    """Extract PK3s.
    """

    bl_idname = "remt.remt_extract_pk3"
    bl_label = "Extract"
    bl_description = "Prepare game data by extracting all pk3s found in a" \
        " directory and subdirectory."

    @staticmethod
    def _validate_input(source_path, target_path, status):
        """Validate input.
        """

        if not source_path:
            cancel_msg = "input failed: no source path"
            status.set_canceled(cancel_msg)

        if not isinstance(source_path, str):
            cancel_msg = "input failed: source path must be string"
            status.set_canceled(cancel_msg)

        source_path = bpy.path.abspath(source_path)
        if not os.path.isdir(source_path):
            cancel_msg = "input failed: source directory not found"
            status.set_canceled(cancel_msg)

        if not target_path:
            cancel_msg = "input failed: no target path"
            status.set_canceled(cancel_msg)

        if not isinstance(target_path, str):
            cancel_msg = "input failed: target path must be string"
            status.set_canceled(cancel_msg)

        target_path = bpy.path.abspath(target_path)
        if not os.path.isdir(target_path):
            cancel_msg = "input failed: target directory not found"
            status.set_canceled(cancel_msg)

    def execute(self, context):
        """Search directory recursively and extract all pk3 files to a
        destination directory.
        """

        import rtcw_et_model_tools.blender.status as status
        status = status.Status()

        try:

            source_path = context.scene.remt_extract_pk3_source_path
            target_path = context.scene.remt_extract_pk3_target_path
            ExtractPK3s._validate_input(source_path, target_path, status)

            for root, dirs, files in os.walk(source_path, topdown=False):

                    for file_path in files:

                        if file_path.endswith(".pk3"):

                            path_to_pk3_file = os.path.join(root, file_path)
                            zip_ref = zipfile.ZipFile(path_to_pk3_file, 'r')
                            zip_ref.extractall(target_path)
                            zip_ref.close()

        except status.Canceled:
            pass

        status.report(self)
        return {'FINISHED'}

# Registration
# ==============================

classes = (
    ExtractPK3sPanel,
    ExtractPK3s,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_extract_pk3_source_path = \
        bpy.props.StringProperty(
            name="Source Filepath",
            description="Path to top level source directory",
            subtype='DIR_PATH')

    bpy.types.Scene.remt_extract_pk3_target_path = \
        bpy.props.StringProperty(
            name="Target Filepath",
            description="Path to destination directory",
            subtype='DIR_PATH')

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_extract_pk3_source_path
    del bpy.types.Scene.remt_extract_pk3_target_path
