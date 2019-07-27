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

"""Exports.
"""

import os

import bpy


class REMT_PT_Export(bpy.types.Panel):
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
            row.operator("remt.md3_exporter",
                            text="Export",
                            icon="EXPORT")

        elif context.scene.remt_export_format == "MDC":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdc_export_path")

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
                    "remt_mds_collapse_frame_export")

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
                    "remt_mdmmdx_collapse_frame_export")

            row = layout.row()
            row.operator("remt.mdmmdx_exporter",
                            text="Export",
                            icon="EXPORT")

        else:

            pass


class REMT_OT_MD3Export(bpy.types.Operator):
    """Operator for exporting to MD3 file format.
    """

    bl_idname = "remt.md3_exporter"
    bl_label = "Export to MD3 file format"
    bl_description = "Export to MD3 file format"

    @staticmethod
    def _parse_input(context):

        md3_file_path = context.scene.remt_md3_export_path
        md3_file_path = bpy.path.abspath(md3_file_path)

        if not md3_file_path.endswith(".md3"):
            raise Exception("MD3 filepath must end with '.md3'")

        return md3_file_path

    def execute(self, context):
        """Export to MD3 file format.
        """

        import rtcw_et_model_tools.md3.facade as md3_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            md3_file_path = self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MD3 export started ...")

            mdi_model = collection_m.read()
            md3_facade_m.write(mdi_model, md3_file_path)

            time = timer.time()
            reporter_m.info("MD3 export DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


class REMT_OT_MDCExport(bpy.types.Operator):
    """Operator for exporting to MDC file format.
    """

    bl_idname = "remt.mdc_exporter"
    bl_label = "Export to MDC file format"
    bl_description = "Export to MDC file format"

    @staticmethod
    def _parse_input(context):

        mdc_file_path = context.scene.remt_mdc_export_path
        mdc_file_path = bpy.path.abspath(mdc_file_path)

        if not mdc_file_path.endswith(".mdc"):
            raise Exception("MDC filepath must end with '.mdc'")

        return mdc_file_path

    def execute(self, context):
        """Export to MDC file format.
        """

        import rtcw_et_model_tools.mdc.facade as mdc_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            mdc_file_path = self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MDC export started ...")

            mdi_model = collection_m.read()
            mdc_facade_m.write(mdi_model, mdc_file_path)

            time = timer.time()
            reporter_m.info("MDC export DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


class REMT_OT_MDSExport(bpy.types.Operator):
    """Operator for exporting to MDS file format.
    """

    bl_idname = "remt.mds_exporter"
    bl_label = "Export to MDS file format"
    bl_description = "Export to MDS file format"

    @staticmethod
    def _parse_input(context):

        mds_file_path = context.scene.remt_mds_export_path
        mds_file_path = bpy.path.abspath(mds_file_path)

        if not mds_file_path.endswith(".mds"):
            raise Exception("MDS filepath must end with '.mds'")

        collapse_frame = context.scene.remt_mds_collapse_frame_export

        return (mds_file_path, collapse_frame)

    def execute(self, context):
        """Export MDS file format.
        """

        import rtcw_et_model_tools.mds.facade as mds_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            mds_file_path, collapse_frame = self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MDS export started ...")

            mdi_model = collection_m.read(collapse_frame)
            mds_facade_m.write(mdi_model, mds_file_path)

            time = timer.time()
            reporter_m.info("MDS export DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


class REMT_OT_MDMMDXExport(bpy.types.Operator):
    """Operator for exporting to MDM/MDX file format.
    """

    bl_idname = "remt.mdmmdx_exporter"
    bl_label = "Export to MDM/MDX file format"
    bl_description = "Export to MDM/MDX file format"

    @staticmethod
    def _parse_input(context):

        mdm_file_path = context.scene.remt_mdm_export_path
        if mdm_file_path:

            if not mdm_file_path.endswith(".mdm"):
                raise Exception("MDM filepath must end with '.mdm'")

        else:

            mdm_file_path = None

        mdx_file_path = context.scene.remt_mdx_export_path
        if mdx_file_path:

            mdx_file_path = bpy.path.abspath(mdx_file_path)

            if not mdx_file_path.endswith(".mdx"):
                raise Exception("MDX filepath must end with '.mdx'")

        else:

            mdx_file_path = None

        if not (mdm_file_path or mdx_file_path):
            raise Exception("Must provide at least 1 export path.")

        collapse_frame = context.scene.remt_mdmmdx_collapse_frame_export

        return (mdm_file_path, mdx_file_path, collapse_frame)

    def execute(self, context):
        """Export MDM/MDX file format.
        """

        import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            mdm_file_path, mdx_file_path, collapse_frame = \
                self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MDM/MDX export started ...")

            mdi_model = collection_m.read(collapse_frame)
            mdmmdx_facade_m.write(mdi_model, mdm_file_path, mdx_file_path)

            time = timer.time()
            reporter_m.info("MDM/MDX  export DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


# Registration
# ==============================

classes = (
    REMT_PT_Export,
    REMT_OT_MD3Export,
    REMT_OT_MDCExport,
    REMT_OT_MDSExport,
    REMT_OT_MDMMDXExport,
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

    bpy.types.Scene.remt_mds_collapse_frame_export = \
        bpy.props.IntProperty(
            name = "Collapse Frame",
            description = "Collapse frame for LOD data",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mdmmdx_collapse_frame_export = \
        bpy.props.IntProperty(
            name = "Collapse Frame",
            description = "Collapse frame for LOD data",
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
    del bpy.types.Scene.remt_mds_collapse_frame_export
    del bpy.types.Scene.remt_mdmmdx_collapse_frame_export
