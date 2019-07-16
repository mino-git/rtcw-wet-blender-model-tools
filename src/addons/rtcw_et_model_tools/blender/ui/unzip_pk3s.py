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

"""Unzip PK3 files.
"""

import bpy


class UnzipPK3sPanel(bpy.types.Panel):
    """Panel for unzip pk3s operation.
    """

    bl_label = "Unzip PK3s"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene,
                "remt_unzip_pk3_source_path")

        row = layout.row()
        row.prop(context.scene,
                "remt_unzip_pk3_target_path")

        row = layout.row()
        row.operator("remt.remt_unzip_pk3",
                     text="Unzip",
                     icon="DISK_DRIVE")


class UnzipPK3s(bpy.types.Operator):
    """Unzip PK3s.
    """

    bl_idname = "remt.remt_unzip_pk3"
    bl_label = "Unzip"
    bl_description = "Unzip all pk3s found in the source directory and all" \
                     " its subdirectories and copy to target path"

    @staticmethod
    def _parse_input(context):

        source_path = context.scene.remt_unzip_pk3_source_path
        source_path = bpy.path.abspath(source_path)

        target_path = context.scene.remt_unzip_pk3_target_path
        target_path = bpy.path.abspath(target_path)

        return (source_path, target_path)

    def execute(self, context):
        """Search directory recursively and unzip all pk3 files to a
        destination directory. PK3 files are .zip files containing most of the
        game data.
        """

        import rtcw_et_model_tools.common.unzip_pk3s as unzip_pks_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            source_path, target_path = self._parse_input(context)
            unzip_pks_m.unzip_dir_recursive(source_path, target_path)

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


# Registration
# ==============================

classes = (
    UnzipPK3sPanel,
    UnzipPK3s,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_unzip_pk3_source_path = \
        bpy.props.StringProperty(
            name="Source Filepath",
            description="Path to top level source directory (game data)",
            subtype='DIR_PATH')

    bpy.types.Scene.remt_unzip_pk3_target_path = \
        bpy.props.StringProperty(
            name="Target Filepath",
            description="Path to destination directory for extraction",
            subtype='DIR_PATH')

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_unzip_pk3_source_path
    del bpy.types.Scene.remt_unzip_pk3_target_path
