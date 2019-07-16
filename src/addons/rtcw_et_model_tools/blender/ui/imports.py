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

"""Imports.
"""

import os

import bpy


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
            row.operator("remt.md3_importer",
                            text="Import",
                            icon="IMPORT")

        elif context.scene.remt_import_format == "MDC":

            row = layout.row()
            row.prop(context.scene,
                    "remt_mdc_import_path")

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


class MD3Importer(bpy.types.Operator):
    """Operator for importing MD3 file format.
    """

    bl_idname = "remt.md3_importer"
    bl_label = "Import MD3 file format into blender"
    bl_description = "Import MD3 file format into blender"

    @staticmethod
    def _parse_input(context):

        md3_file_path = context.scene.remt_md3_import_path
        md3_file_path = bpy.path.abspath(md3_file_path)

        if not os.path.isfile(md3_file_path):
            raise Exception("MD3 filepath not found")

        bind_frame = 0

        return (md3_file_path, bind_frame)

    def execute(self, context):
        """Import MD3 file format.
        """

        import rtcw_et_model_tools.md3.facade as md3_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            md3_file_path, bind_frame = self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MD3 import started ...")

            mdi_model = md3_facade_m.read(md3_file_path, bind_frame)
            collection_m.write(mdi_model)

            time = timer.time()
            reporter_m.info("MD3 import DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


class MDCImporter(bpy.types.Operator):
    """Operator for importing MDC file format.
    """

    bl_idname = "remt.mdc_importer"
    bl_label = "Import MDC file format into blender"
    bl_description = "Import MDC file format into blender"

    @staticmethod
    def _parse_input(context):

        mdc_file_path = context.scene.remt_mdc_import_path
        mdc_file_path = bpy.path.abspath(mdc_file_path)

        if not os.path.isfile(mdc_file_path):
            raise Exception("MDC filepath not found")

        bind_frame = 0

        return (mdc_file_path, bind_frame)

    def execute(self, context):
        """Import MDC file format.
        """

        import rtcw_et_model_tools.mdc.facade as mdc_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            mdc_file_path, bind_frame = self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MDC import started ...")

            mdi_model = mdc_facade_m.read(mdc_file_path, bind_frame)
            collection_m.write(mdi_model)

            time = timer.time()
            reporter_m.info("MDC import DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


class MDSImporter(bpy.types.Operator):
    """Operator for importing MDS file format.
    """

    bl_idname = "remt.mds_importer"
    bl_label = "Import MDS file format into blender"
    bl_description = "Import MDS file format into blender"

    @staticmethod
    def _parse_input(context):

        mds_file_path = context.scene.remt_mds_import_path
        mds_file_path = bpy.path.abspath(mds_file_path)

        if not os.path.isfile(mds_file_path):
            raise Exception("MDS filepath not found")

        bind_frame = context.scene.remt_mds_bind_frame

        return (mds_file_path, bind_frame)

    def execute(self, context):
        """Import MDS file format.
        """

        import rtcw_et_model_tools.mds.facade as mds_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            mds_file_path, bind_frame = self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MDS import started ...")

            mdi_model = mds_facade_m.read(mds_file_path, bind_frame)
            collection_m.write(mdi_model)

            time = timer.time()
            reporter_m.info("MDS import DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}


class MDMMDXImporter(bpy.types.Operator):
    """Operator for importing MDM/MDX file format.
    """

    bl_idname = "remt.mdmmdx_importer"
    bl_label = "Import MDM/MDX file format into blender"
    bl_description = "Import MDM/MDX file format into blender"

    @staticmethod
    def _parse_input(context):

        mdm_file_path = context.scene.remt_mdm_import_path
        mdx_file_path = context.scene.remt_mdx_import_path

        bind_frame = context.scene.remt_mdmmdx_bind_frame

        if mdm_file_path:

            mdm_file_path = bpy.path.abspath(mdm_file_path)

            if not os.path.isfile(mdm_file_path):
                raise Exception("MDM filepath not found")

        else:

            mdm_file_path = None

        mdx_file_path = bpy.path.abspath(mdx_file_path)

        if not os.path.isfile(mdx_file_path):
            raise Exception("MDX filepath not found")

        return (mdm_file_path, mdx_file_path, bind_frame)

    def execute(self, context):
        """Import MDM/MDX file format.
        """

        import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade_m
        import rtcw_et_model_tools.mdi.mdi as mdi_m
        import rtcw_et_model_tools.blender.core.collection as collection_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            mdm_file_path, mdx_file_path, bind_frame = \
                self._parse_input(context)

            timer = timer_m.Timer()
            reporter_m.info("MDM/MDX import started ...")

            mdi_model = \
                mdmmdx_facade_m.read(mdm_file_path, mdx_file_path, bind_frame)
            collection_m.write(mdi_model)

            time = timer.time()
            reporter_m.info("Import DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

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

    bpy.types.Scene.remt_mds_bind_frame = \
        bpy.props.IntProperty(
            name = "Bindpose Frame",
            description = "Bind pose used for skinning (optional)",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_mdmmdx_bind_frame = \
        bpy.props.IntProperty(
            name = "Bindpose Frame",
            description = "Bind pose used for skinning (optional)",
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
    del bpy.types.Scene.remt_mds_bind_frame
    del bpy.types.Scene.remt_mdmmdx_bind_frame
