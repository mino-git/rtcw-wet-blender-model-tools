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

"""Shading.
"""

import bpy


class REMT_PT_Shading(bpy.types.Panel):
    """Panel for shading operations.
    """

    bl_label = "Shading"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()

        row.prop(context.scene, "remt_shading_method")

        row = layout.row()
        row.prop(context.scene,
                "remt_game_path")

        if context.scene.remt_shading_method == "Skinfile":

            row = layout.row()
            row.prop(context.scene,
                    "remt_skin_file_path")

        row = layout.row()
        row.operator("remt.apply_shading",
                     text="Apply Shading",
                     icon="MATERIAL_DATA")


class REMT_OT_Shading(bpy.types.Operator):
    """Operator for shading operations.
    """

    bl_idname = "remt.apply_shading"
    bl_label = "Apply Materials"
    bl_description = "Apply shading from material names"

    @staticmethod
    def _parse_input(context):

        method = context.scene.remt_shading_method
        if not (method == 'Material Names' or
                method == 'Skinfile'):
            raise Exception("Method not supported.")

        game_path = context.scene.remt_game_path
        if not game_path:
            raise Exception("Game path is empty")
        game_path = bpy.path.abspath(game_path)

        skin_file_path = context.scene.remt_skin_file_path
        if method == 'Skinfile' and not skin_file_path:
            raise Exception("Skinfilepath is empty")
        skin_file_path = bpy.path.abspath(skin_file_path)

        return (method, game_path, skin_file_path)

    def execute(self, context):
        """Shading operation.
        """

        import rtcw_et_model_tools.blender.core.material as material_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            method, game_path, skin_file_path = self._parse_input(context)
            material_m.apply_shaders(method, game_path, skin_file_path)

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}

# Registration
# ==============================

classes = (
    REMT_PT_Shading,
    REMT_OT_Shading,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_shading_method = \
        bpy.props.EnumProperty(
            name = "Method",
            description = "Apply a basic set of shader nodes to the meshes"
                          " of the active collection.\n"
                           "- Materialnames: material names are used\n"
                           " shader references in the game data.\n"
                           "- Skin file: skin files are used.",
            items = [("Material Names", "Material Names", ""),
                     ("Skinfile", "Skinfile", "")],
            default = "Material Names")

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_shading_method
