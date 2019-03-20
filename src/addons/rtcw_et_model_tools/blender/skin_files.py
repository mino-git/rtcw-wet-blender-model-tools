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

"""Apply shading or import tag models by reading .skin file information.
"""

import os
import re

import bpy


# Core
# ==============================

def import_tag_model(tag_name, model_path, skin_file, data_path, status):
    """Import a tag model"""

    import rtcw_et_model_tools.md3.facade as md3_facade
    import rtcw_et_model_tools.mdc.facade as mdc_facade
    import rtcw_et_model_tools.blender.scene as blender_scene

    # paths relative to game directory
    model_path_1 = os.path.join(data_path,
                              model_path)
    model_path_md3_1 = "{}.{}".format(model_path_1, "md3")
    model_path_mdc_1 = "{}.{}".format(model_path_1, "mdc")

    # paths relative to skin file directory
    skin_file_path = os.path.dirname(os.path.abspath(skin_file.file_path))
    model_path_2 = os.path.join(skin_file_path, model_path)
    model_path_md3_2= "{}.{}".format(model_path_2, "md3")
    model_path_mdc_2 = "{}.{}".format(model_path_2, "mdc")

    # try to find it relative to game data path
    if os.path.isfile(model_path_md3_1):

        bind_frame = 0
        mdi_model = md3_facade.read(model_path_md3_1, bind_frame,
                                    encoding="binary")
        blender_scene.write(mdi_model, bind_frame)

    elif os.path.isfile(model_path_mdc_1):

        bind_frame = 0
        mdi_model = mdc_facade.read(model_path_mdc_1, bind_frame,
                                    encoding="binary")
        blender_scene.write(mdi_model, bind_frame)

    # try to find it relative to the skin file path
    elif os.path.isfile(model_path_md3_2):

        bind_frame = 0
        mdi_model = md3_facade.read(model_path_md3_2, bind_frame,
                                    encoding="binary")
        blender_scene.write(mdi_model, bind_frame)

    elif os.path.isfile(model_path_mdc_2):

        bind_frame = 0
        mdi_model = mdc_facade.read(model_path_mdc_2, bind_frame,
                                    encoding="binary")
        blender_scene.write(mdi_model, bind_frame)

    else:

        warning_msg = "Tag import model '{}' not found".format(model_path)
        status.warning_msgs.append(warning_msg)

def import_tag_models(active_collection, skin_file, data_path,
                      status):
    """Import a tag models"""

    for tag_to_model_mapping in skin_file.tag_to_model_mappings:

        tag_name = tag_to_model_mapping.tag_name
        model_path = tag_to_model_mapping.model_path
        import_tag_model(tag_name, model_path, skin_file, data_path, status)


# UI
# ==============================

class SkinFilePanel(bpy.types.Panel):
    """Panel for handling .skin files.
    """

    bl_label = "Skin File"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene,
                "remt_skin_file_path")

        row = layout.row()
        row.prop(context.scene,
                "remt_data_path")

        row = layout.row()
        row.prop(context.scene,
                "remt_apply_shaders")
        row.prop(context.scene,
                "remt_import_tag_models")

        row = layout.row()
        row.operator("remt.apply_skin_file",
                     text="Apply Skin",
                     icon="MATCLOTH")


# Operators
# ==============================

class SkinFileOperator(bpy.types.Operator):
    """Operator for handling shading or importing tag models based on .skin"
    files.
    """

    bl_idname = "remt.apply_skin_file"
    bl_label = "Use Skin"
    bl_description = "Apply shading or import models from .skin files"

    @staticmethod
    def _validate_input(skin_file_path, data_path, apply_shaders,
                        import_tag_models, status):
        """Validate input.
        """

        if not skin_file_path:
            cancel_msg = "input failed: no skin file path"
            status.set_canceled(cancel_msg)

        if not isinstance(skin_file_path, str):
            cancel_msg = "input failed: skin file path must be string"
            status.set_canceled(cancel_msg)

        skin_file_path = bpy.path.abspath(skin_file_path)
        if not os.path.isfile(skin_file_path):
            cancel_msg = "input failed: skin file not found on disk"
            status.set_canceled(cancel_msg)

        if not data_path:
            cancel_msg = "input failed: no data path"
            status.set_canceled(cancel_msg)

        if not isinstance(data_path, str):
            cancel_msg = "input failed: data path must be string"
            status.set_canceled(cancel_msg)

        data_path = bpy.path.abspath(data_path)
        if not os.path.isdir(data_path):
            cancel_msg = "input failed: data path not found on disk"
            status.set_canceled(cancel_msg)

        if not skin_file_path.endswith(".skin"):
            cancel_msg = "input failed: skin file must end with '.skin'"
            status.set_canceled(cancel_msg)

        if not isinstance(apply_shaders, bool):
            cancel_msg = "input failed: apply shaders option must be bool"
            status.set_canceled(cancel_msg)

        if not isinstance(import_tag_models, bool):
            cancel_msg = "input failed: import tag models option must be bool"
            status.set_canceled(cancel_msg)

        if not (apply_shaders or import_tag_models):
            cancel_msg = "input failed: must choose at least one option"
            status.set_canceled(cancel_msg)

    def execute(self, context):
        """Apply shading or import tag models based on .skin file.
        """

        import rtcw_et_model_tools.misc.skin as skin
        import rtcw_et_model_tools.blender.status as status
        import rtcw_et_model_tools.blender.shading as shading
        status = status.Status()

        try:

            skin_file_path = context.scene.remt_skin_file_path
            data_path = context.scene.remt_data_path
            apply_shaders = context.scene.remt_apply_shaders
            import_tag_models_o = context.scene.remt_import_tag_models
            SkinFileOperator._validate_input(skin_file_path, data_path,
                                             apply_shaders,
                                             import_tag_models_o, status)

            skin_data = skin.SkinData.read(skin_file_path, status)

            active_collection = \
                bpy.context.view_layer.active_layer_collection.collection
            if apply_shaders:
                shading.apply_shaders_from_skin(active_collection, skin_data,
                                                data_path, status)

            if import_tag_models_o:
                import_tag_models(active_collection, skin_data, data_path,
                                  status)

        except status.Canceled:
            pass

        status.report(self)
        return {'FINISHED'}


# Registration
# ==============================

classes = (
    SkinFilePanel,
    SkinFileOperator,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_skin_file_path = \
        bpy.props.StringProperty(
            name="Skin Filepath",
            description="Path to .skin file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_apply_shaders = \
        bpy.props.BoolProperty(
            name="Apply Shaders",
            description="Apply shading info",
            default = True)

    bpy.types.Scene.remt_import_tag_models = \
        bpy.props.BoolProperty(
            name="Import Tag Models",
            description="Import tag models",
            default = True)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_skin_file_path
    del bpy.types.Scene.remt_apply_shaders
    del bpy.types.Scene.remt_import_tag_models
