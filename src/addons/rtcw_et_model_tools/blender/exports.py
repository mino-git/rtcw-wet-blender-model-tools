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

class ExportPanel(bpy.types.Panel):
    """Panel for export operations.
    """

    bl_label = "Export"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene, "remt_export_format")

        if context.scene.remt_export_format == "MD3":

            row = layout.row()
            row.prop(context.scene,
                    "remt_md3_export_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_md3_bind_frame_export")

            row = layout.row()
            row.operator("remt.md3_exporter",
                            text="Export",
                            icon="EXPORT")

        elif context.scene.remt_export_format == "MDC":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdc_export_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdc_bind_frame_export")

            row = layout.row()
            row.operator("remt.mdc_exporter",
                            text="Export",
                            icon="EXPORT")

        elif context.scene.remt_export_format == "MDS":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mds_export_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mds_bind_frame_export")

            row = layout.row()
            row.operator("remt.mds_exporter",
                            text="Export",
                            icon="EXPORT")

        elif context.scene.remt_export_format == "MDM/MDX":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdm_export_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdx_export_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdmmdx_bind_frame_export")

            row = layout.row()
            row.operator("remt.mdmmdx_exporter",
                            text="Export",
                            icon="EXPORT")

        else:

            pass


# Operators
# ==============================

class MD3Exporter(bpy.types.Operator):
    """Export blender scene to MD3 file.
    """

    bl_idname = "remt.md3_exporter"
    bl_label = "Export to MD3 file format"
    bl_description = "Export to MD3 file format"

    def execute(self, context):

        import rtcw_et_model_tools.md3.facade as md3_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        md3_file_path = context.scene.remt_md3_export_path
        bind_frame = context.scene.remt_md3_bind_frame_export

        if not md3_file_path.endswith(".md3"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MD3 Filepath" must end with ".md3".')
            return {'CANCELLED'}

        md3_file_path = bpy.path.abspath(md3_file_path)

        mdi_model = blender_scene.read(bind_frame)
        md3_facade.write(mdi_model, md3_file_path)

        return {'FINISHED'}


class MDCExporter(bpy.types.Operator):
    """Export blender scene to MDC file.
    """

    bl_idname = "remt.mdc_exporter"
    bl_label = "Export to MDC file format"
    bl_description = "Export to MDC file format"

    def execute(self, context):

        import rtcw_et_model_tools.mdc.facade as mdc_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mdc_file_path = context.scene.remt_mdc_export_path
        bind_frame = context.scene.remt_mdc_bind_frame_export

        if not mdc_file_path.endswith(".mdc") :
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDC Filepath" must end with ".mdc".')
            return {'CANCELLED'}

        mdc_file_path = bpy.path.abspath(mdc_file_path)

        mdi_model = blender_scene.read(bind_frame)
        mdc_facade.write(mdi_model, mdc_file_path)

        return {'FINISHED'}


class MDSExporter(bpy.types.Operator):
    """Export blender scene to MDS file.
    """

    bl_idname = "remt.mds_exporter"
    bl_label = "Export to MDS file format"
    bl_description = "Export to MDS file format"

    def execute(self, context):

        import rtcw_et_model_tools.mds.facade as mds_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mds_file_path = context.scene.remt_mds_export_path
        bind_frame = context.scene.remt_mds_bind_frame_export

        if not mds_file_path.endswith(".mds"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDS Filepath" must end with ".mds".')
            return {'CANCELLED'}

        mds_file_path = bpy.path.abspath(mds_file_path)

        mdi_model = blender_scene.read(bind_frame)
        mds_facade.write(mdi_model, mds_file_path)

        return {'FINISHED'}


class MDMMDXExporter(bpy.types.Operator):
    """Export blender scene to MDM/MDX files.
    """

    bl_idname = "remt.mdmmdx_exporter"
    bl_label = "Export to MDM/MDX file format"
    bl_description = "Export to MDM/MDX file format"

    def execute(self, context):

        import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mdm_file_path = context.scene.remt_mdm_export_path
        mdx_file_path = context.scene.remt_mdx_export_path
        bind_frame = context.scene.remt_mdmmdx_bind_frame_export

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

        mdi_model = blender_scene.read(bind_frame)
        mdmmdx_facade.write(mdi_model, mdx_file_path, mdm_file_path)

        return {'FINISHED'}


# Registration
# ==============================

classes = (
    ExportPanel,
    MD3Exporter,
    MDCExporter,
    MDSExporter,
    MDMMDXExporter,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_export_format = \
        bpy.props.EnumProperty(
            name = "Format",
            description = "Choose which format to export",
            items = [("MD3", "MD3", ""),
                     ("MDC", "MDC", ""),
                     ("MDS", "MDS", ""),
                     ("MDM/MDX", "MDM/MDX", "")],
            default = "MD3")

    bpy.types.Scene.remt_md3_export_path = \
        bpy.props.StringProperty(
            name="MD3 Filepath",
            description="Path to MD3 file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mdc_export_path = \
        bpy.props.StringProperty(
            name="MDC Filepath",
            description="Path to MDC file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mds_export_path = \
        bpy.props.StringProperty(
            name="MDS Filepath",
            description="Path to MDS file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mdm_export_path = \
        bpy.props.StringProperty(
            name="MDM Filepath",
            description="Path to MDM file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_mdx_export_path = \
        bpy.props.StringProperty(
            name="MDX Filepath",
            description="Path to MDX file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_md3_bind_frame_export = \
        bpy.props.IntProperty(
            name = "Bind Frame",
            description = "Bind pose used for morphing",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mdc_bind_frame_export = \
        bpy.props.IntProperty(
            name = "Bind Frame",
            description = "Bind pose used for morphing",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mds_bind_frame_export = \
        bpy.props.IntProperty(
            name = "Bind Frame",
            description = "Bind pose used for skinning",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mdmmdx_bind_frame_export = \
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

    del bpy.types.Scene.remt_export_format
    del bpy.types.Scene.remt_md3_export_path
    del bpy.types.Scene.remt_mdc_export_path
    del bpy.types.Scene.remt_mds_export_path
    del bpy.types.Scene.remt_mdm_export_path
    del bpy.types.Scene.remt_mdx_export_path
    del bpy.types.Scene.remt_md3_bind_frame_export
    del bpy.types.Scene.remt_mdc_bind_frame_export
    del bpy.types.Scene.remt_mds_bind_frame_export
    del bpy.types.Scene.remt_mdmmdx_bind_frame_export
