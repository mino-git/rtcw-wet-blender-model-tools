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

"""TODO.
"""

import bpy


# UI
# ==============================

class ImportPanel(bpy.types.Panel):
    """Panel for import operations.
    """

    bl_label = "Import"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "remt_import_format")

        if context.scene.remt_import_format == "MD3":

            row = layout.row()
            row.prop(context.scene,
                    "remt_md3_import_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_md3_bind_frame")

            row = layout.row()
            row.operator("remt.md3_importer",
                            text="Import",
                            icon="IMPORT")

        elif context.scene.remt_import_format == "MDC":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdc_import_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdc_bind_frame")

            row = layout.row()
            row.operator("remt.mdc_importer",
                            text="Import",
                            icon="IMPORT")

        elif context.scene.remt_import_format == "MDS":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mds_import_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mds_bind_frame")

            row = layout.row()
            row.operator("remt.mds_importer",
                            text="Import",
                            icon="IMPORT")

        elif context.scene.remt_import_format == "MDM/MDX":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdm_import_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdx_import_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdmmdx_bind_frame")

            row = layout.row()
            row.operator("remt.mdmmdx_importer",
                            text="Import",
                            icon="IMPORT")

        else:

            pass


# Operators
# ==============================

class MD3Importer(bpy.types.Operator):
    """Import MD3 file format into blender.
    """

    bl_idname = "remt.md3_importer"
    bl_label = "Import MD3 file format into blender"
    bl_description = "Import MD3 file format into blender"

    def execute(self, context):

        import rtcw_et_model_tools.md3.facade as md3_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        md3_file_path = context.scene.remt_md3_import_path
        bind_frame = context.scene.remt_md3_bind_frame

        if not md3_file_path.endswith(".md3"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MD3 Filepath" must end with ".md3".')
            return {'CANCELLED'}

        md3_file_path = bpy.path.abspath(md3_file_path)

        mdi_model = md3_facade.read(md3_file_path, bind_frame,
                                    encoding = "binary")
        blender_scene.write(mdi_model)

        return {'FINISHED'}


class MDCImporter(bpy.types.Operator):
    """Import MDC file into blender.
    """

    bl_idname = "remt.mdc_importer"
    bl_label = "Import MDC file format into blender"
    bl_description = "Import MDC file format into blender"

    def execute(self, context):

        import rtcw_et_model_tools.mdc.facade as mdc_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mdc_file_path = context.scene.remt_mdc_import_path
        bind_frame = context.scene.remt_mdc_bind_frame

        if not mdc_file_path.endswith(".mdc") :
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDC Filepath" must end with ".mdc".')
            return {'CANCELLED'}

        mdc_file_path = bpy.path.abspath(mdc_file_path)

        mdi_model = mdc_facade.read(mdc_file_path, bind_frame,
                                    encoding="binary")
        blender_scene.write(mdi_model)

        return {'FINISHED'}


class MDSImporter(bpy.types.Operator):
    """Import MDS file format into blender.
    """

    bl_idname = "remt.mds_importer"
    bl_label = "Import MDS file format into blender"
    bl_description = "Import MDS file format into blender"

    def execute(self, context):

        import rtcw_et_model_tools.mds.facade as mds_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mds_file_path = context.scene.remt_mds_import_path
        bind_frame = context.scene.remt_mds_bind_frame

        if not mds_file_path.endswith(".mds"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDS Filepath" must end with ".mds".')
            return {'CANCELLED'}

        mds_file_path = bpy.path.abspath(mds_file_path)

        mdi_model = mds_facade.read(mds_file_path, bind_frame,
                                    encoding="binary")
        blender_scene.write(mdi_model)

        return {'FINISHED'}


class MDMMDXImporter(bpy.types.Operator):
    """Import MDM/MDX file into blender.
    """

    bl_idname = "remt.mdmmdx_importer"
    bl_label = "Import MDM/MDX file format into blender"
    bl_description = "Import MDM/MDX file format into blender"

    def execute(self, context):

        import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mdm_file_path = context.scene.remt_mdm_import_path
        mdx_file_path = context.scene.remt_mdx_import_path
        bind_frame = context.scene.remt_mdmmdx_bind_frame

        if not mdm_file_path.endswith(".mdm"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDM Filepath" must end with ".mdm".')
            return {'CANCELLED'}

        if not mdx_file_path.endswith(".mdx"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDX Filepath" must end with ".mdx".')
            return {'CANCELLED'}

        mdm_file_path = bpy.path.abspath(mdm_file_path)
        mdx_file_path = bpy.path.abspath(mdx_file_path)

        if not mdm_file_path:
            mdm_file_path = None

        mdi_model = mdmmdx_facade.read(mdx_file_path, mdm_file_path,
                                       bind_frame, encoding="binary")
        blender_scene.write(mdi_model)

        return {'FINISHED'}


# Registration
# ==============================

classes = (
    ImportPanel,
    MD3Importer,
    MDCImporter,
    MDSImporter,
    MDMMDXImporter,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_import_format = \
        bpy.props.EnumProperty(
            name = "Format",
            description = "Choose which format to import",
            items = [("MD3", "MD3", ""),
                     ("MDC", "MDC", ""),
                     ("MDS", "MDS", ""),
                     ("MDM/MDX", "MDM/MDX", "")],
            default = "MD3")

    bpy.types.Scene.remt_md3_import_path = \
        bpy.props.StringProperty(
            name="MD3 Filepath",
            description="Path to MD3 file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mdc_import_path = \
        bpy.props.StringProperty(
            name="MDC Filepath",
            description="Path to MDC file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mds_import_path = \
        bpy.props.StringProperty(
            name="MDS Filepath",
            description="Path to MDS file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mdm_import_path = \
        bpy.props.StringProperty(
            name="MDM Filepath",
            description="Path to MDM file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mdx_import_path = \
        bpy.props.StringProperty(
            name="MDX Filepath",
            description="Path to MDX file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_md3_bind_frame = \
        bpy.props.IntProperty(
            name = "Bind Frame",
            description = "Bind pose used for morphing",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mdc_bind_frame = \
        bpy.props.IntProperty(
            name = "Bind Frame",
            description = "Bind pose used for morphing",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mds_bind_frame = \
        bpy.props.IntProperty(
            name = "Bind Frame",
            description = "Bind pose used for skinning",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mdmmdx_bind_frame = \
        bpy.props.IntProperty(
            name = "Bind Frame",
            description = "Bind pose used for skinning",
            default = 0,
            min = 0,
            max = 1000000
            )

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_import_format
    del bpy.types.Scene.remt_md3_import_path
    del bpy.types.Scene.remt_mdc_import_path
    del bpy.types.Scene.remt_mds_import_path
    del bpy.types.Scene.remt_mdm_import_path
    del bpy.types.Scene.remt_mdx_import_path
    del bpy.types.Scene.remt_md3_bind_frame
    del bpy.types.Scene.remt_mdc_bind_frame
    del bpy.types.Scene.remt_mds_bind_frame
    del bpy.types.Scene.remt_mdmmdx_bind_frame
