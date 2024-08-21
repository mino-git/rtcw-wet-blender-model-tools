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

"""Attachment.
"""

import bpy


class REMT_PT_Attachment(bpy.types.Panel):
    """Panel for attach to tag operation.
    """

    bl_label = "Attachment"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()

        row.prop(context.scene, "remt_attach_method")

        if context.scene.remt_attach_method == "Skinfile":

            row = layout.row()
            row.prop(context.scene,
                    "remt_game_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_skin_file_path")

        row = layout.row()
        row.operator("remt.attachment",
                     text="Attach",
                     icon="EMPTY_DATA")


class REMT_OT_Attachment(bpy.types.Operator):
    """Operator for attach to tag operation.
    """

    bl_idname = "remt.attachment"
    bl_label = "Attach"
    bl_description = "Attach a selection of objects to a tag."

    @staticmethod
    def _parse_input(context):

        method = context.scene.remt_attach_method
        if not (method == 'Objects' or
                method == 'Skinfile'):
            raise Exception("Method not supported.")

        game_path = context.scene.remt_game_path
        game_path = bpy.path.abspath(game_path)

        skin_file_path = context.scene.remt_skin_file_path
        skin_file_path = bpy.path.abspath(skin_file_path)

        return (method, game_path, skin_file_path)

    def execute(self, context):
        """Attachment of models to a tag object
        """

        import rtcw_et_model_tools.blender.core.arrow as arrow_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            method, game_path, skin_file_path = self._parse_input(context)
            arrow_m.attach_to_tag(method, game_path, skin_file_path)

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}

# Registration
# ==============================

classes = (
    REMT_PT_Attachment,
    REMT_OT_Attachment,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_attach_method = \
        bpy.props.EnumProperty(
            name = "Method",
            description = "Defines how objects are selected for attachment"
                          " to a tag object.\n"
                           "- Objects: selection of objects is attached to"
                           " tag. The tag object is the last selected object\n"
                           "- Skinfile: import and attach models based on skin"
                           " files to active collection",
            items = [("Objects", "Objects", ""),
                     ("Skinfile", "Skinfile", "")],
            default = "Objects")

    bpy.types.Scene.remt_skin_file_path = \
        bpy.props.StringProperty(
            name="Skin Filepath",
            description="Path to .skin file. These contain data like models"
                        " to attach to a tag or shaders to apply to a surface",
            subtype='FILE_PATH')

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_attach_method
    del bpy.types.Scene.remt_skin_file_path
