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

import os

import bpy


# UI
# ==============================

class DirectConversionPanel(bpy.types.Panel):
    """Panel for direct conversion operation.
    """

    bl_label = "Direct Conversion"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene,
                "remt_dc_source_format")

        if context.scene.remt_dc_source_format == "MD3":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_md3_source_path")

        elif context.scene.remt_dc_source_format == "MDC":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdc_source_path")

        elif context.scene.remt_dc_source_format == "MDS":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mds_source_path")

        elif context.scene.remt_dc_source_format == "MDM/MDX":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdm_source_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdx_source_path")

        else:

            pass

        row = layout.row()
        row.prop(context.scene,
                "remt_dc_target_format")

        if context.scene.remt_dc_target_format == "MD3":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_md3_target_path")

        elif context.scene.remt_dc_target_format == "MDC":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdc_target_path")

        elif context.scene.remt_dc_target_format == "MDS":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mds_target_path")

        elif context.scene.remt_dc_target_format == "MDM/MDX":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdm_target_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdx_target_path")

        else:

            pass

        row = layout.row()
        row.operator("remt.remt_direct_conversion",
                     text="Convert",
                     icon="PLUGIN")


# Operators
# ==============================

class DirectConversionOperator(bpy.types.Operator):
    """TODO.
    """

    bl_idname = "remt.remt_direct_conversion"
    bl_label = "Direct Conversion"
    bl_description = "Convert one type of model format to another without" \
        " writing to blender scene"

    @staticmethod
    def _validate_input(remt_dc_source_format, remt_dc_md3_source_path,
                        remt_dc_mdc_source_path, remt_dc_mds_source_path,
                        remt_dc_mdm_source_path, remt_dc_mdx_source_path,
                        remt_dc_target_format, remt_dc_md3_target_path,
                        remt_dc_mdc_target_path, remt_dc_mds_target_path,
                        remt_dc_mdm_target_path, remt_dc_mdx_target_path,
                        status):
        """Validate input.
        """

        # source
        if not remt_dc_source_format:
            cancel_msg = "input failed: no source format given"
            status.set_canceled(cancel_msg)

        if not isinstance(remt_dc_source_format, str):
            cancel_msg = "input failed: source format must be string"
            status.set_canceled(cancel_msg)

        if remt_dc_source_format == "MD3":

            if not remt_dc_md3_source_path:
                cancel_msg = "input failed: no MD3 source path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_md3_source_path, str):
                cancel_msg = "input failed: MD3 source path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_md3_source_path.endswith(".md3"):
                cancel_msg = "input failed: MD3 source path must end" \
                    " with '.md3'."
                status.set_canceled(cancel_msg)

            if not os.path.isfile(remt_dc_md3_source_path):
                cancel_msg = "input failed: MD3 source file not found on disk"
                status.set_canceled(cancel_msg)

        elif remt_dc_source_format == "MDC":

            if not remt_dc_mdc_source_path:
                cancel_msg = "input failed: MDC no source path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mdc_source_path, str):
                cancel_msg = "input failed: MDC source path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mdc_source_path.endswith(".mdc"):
                cancel_msg = "input failed: MDC source path must end" \
                    " with '.mdc'."
                status.set_canceled(cancel_msg)

            if not os.path.isfile(remt_dc_mdc_source_path):
                cancel_msg = "input failed: MDC source file not found on disk"
                status.set_canceled(cancel_msg)

        elif remt_dc_source_format == "MDS":

            if not remt_dc_mds_source_path:
                cancel_msg = "input failed: no MDS source path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mds_source_path, str):
                cancel_msg = "input failed: MDS source path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mds_source_path.endswith(".mds"):
                cancel_msg = "input failed: MDS source path must end" \
                    " with '.mds'."
                status.set_canceled(cancel_msg)

            if not os.path.isfile(remt_dc_mds_source_path):
                cancel_msg = "input failed: MDS source file not found on disk"
                status.set_canceled(cancel_msg)

        elif remt_dc_source_format == "MDM/MDX":

            if not remt_dc_mdm_source_path:
                cancel_msg = "input failed: no MDM source path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mdm_source_path, str):
                cancel_msg = "input failed: MDM source path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mdm_source_path.endswith(".mdm"):
                cancel_msg = "input failed: MDM source path must end" \
                    " with '.mdm'."
                status.set_canceled(cancel_msg)

            if not os.path.isfile(remt_dc_mdm_source_path):
                cancel_msg = "input failed: MDM source file not found on disk"
                status.set_canceled(cancel_msg)

            if not remt_dc_mdx_source_path:
                cancel_msg = "input failed: no MDX source path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mdx_source_path, str):
                cancel_msg = "input failed: MDX source path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mdx_source_path.endswith(".mdx"):
                cancel_msg = "input failed: MDX source path must end" \
                    " with '.mdx'."
                status.set_canceled(cancel_msg)

            if not os.path.isfile(remt_dc_mdx_source_path):
                cancel_msg = "input failed: MDX source file not found on disk"
                status.set_canceled(cancel_msg)

        # target
        if not remt_dc_target_format:
            cancel_msg = "input failed: no source format given"
            status.set_canceled(cancel_msg)

        if not isinstance(remt_dc_target_format, str):
            cancel_msg = "input failed: source format must be string"
            status.set_canceled(cancel_msg)

        if remt_dc_target_format == "MD3":

            if not remt_dc_md3_target_path:
                cancel_msg = "input failed: no MD3 target path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_md3_target_path, str):
                cancel_msg = "input failed: MD3 target path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_md3_target_path.endswith(".md3"):
                cancel_msg = "input failed: MD3 target path must end" \
                    " with '.md3'."
                status.set_canceled(cancel_msg)

        elif remt_dc_target_format == "MDC":

            if not remt_dc_mdc_target_path:
                cancel_msg = "input failed: no MDC target path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mdc_target_path, str):
                cancel_msg = "input failed: MDC target path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mdc_target_path.endswith(".mdc"):
                cancel_msg = "input failed: MDC target path must end" \
                    " with '.mdc'."
                status.set_canceled(cancel_msg)

        elif remt_dc_target_format == "MDS":

            if not remt_dc_mds_target_path:
                cancel_msg = "input failed: no MDS target path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mds_target_path, str):
                cancel_msg = "input failed: MDS target path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mds_target_path.endswith(".mds"):
                cancel_msg = "input failed: MDS target filepath must end" \
                    " with '.mds'."
                status.set_canceled(cancel_msg)

        elif remt_dc_target_format == "MDM/MDX":

            if not remt_dc_mdm_target_path:
                cancel_msg = "input failed: no MDM target path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mdm_target_path, str):
                cancel_msg = "input failed: MDM target path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mdm_target_path.endswith(".mdm"):
                cancel_msg = "input failed: MDM target path must end" \
                    " with '.mdm'."
                status.set_canceled(cancel_msg)

            if not remt_dc_mdx_target_path:
                cancel_msg = "input failed: no MDX target path given"
                status.set_canceled(cancel_msg)

            if not isinstance(remt_dc_mdx_target_path, str):
                cancel_msg = "input failed: MDX target path must be string"
                status.set_canceled(cancel_msg)

            if not remt_dc_mdx_target_path.endswith(".mdx"):
                cancel_msg = "input failed: MDX target path must end" \
                    " with '.mdx'."
                status.set_canceled(cancel_msg)

        else:

            cancel_msg = "input failed: target format type unknown"
            status.set_canceled(cancel_msg)

    def execute(self, context):
        """TODO.
        """

        import rtcw_et_model_tools.blender.status as status
        status = status.Status()

        try:

            remt_dc_source_format = context.scene.remt_dc_source_format
            remt_dc_md3_source_path = context.scene.remt_dc_md3_source_path
            remt_dc_md3_source_path = bpy.path.abspath(remt_dc_md3_source_path)

            remt_dc_mdc_source_path = context.scene.remt_dc_mdc_source_path
            remt_dc_mdc_source_path = bpy.path.abspath(remt_dc_mdc_source_path)

            remt_dc_mds_source_path = context.scene.remt_dc_mds_source_path
            remt_dc_mds_source_path = bpy.path.abspath(remt_dc_mds_source_path)

            remt_dc_mdm_source_path = context.scene.remt_dc_mdm_source_path
            remt_dc_mdm_source_path = bpy.path.abspath(remt_dc_mdm_source_path)

            remt_dc_mdx_source_path = context.scene.remt_dc_mdx_source_path
            remt_dc_mdx_source_path = bpy.path.abspath(remt_dc_mdx_source_path)

            remt_dc_target_format = context.scene.remt_dc_target_format
            remt_dc_md3_source_path = bpy.path.abspath(remt_dc_md3_source_path)

            remt_dc_md3_target_path = context.scene.remt_dc_md3_target_path
            remt_dc_md3_target_path = bpy.path.abspath(remt_dc_md3_target_path)

            remt_dc_mdc_target_path = context.scene.remt_dc_mdc_target_path
            remt_dc_mdc_target_path = bpy.path.abspath(remt_dc_mdc_target_path)

            remt_dc_mds_target_path = context.scene.remt_dc_mds_target_path
            remt_dc_mds_target_path = bpy.path.abspath(remt_dc_mds_target_path)

            remt_dc_mdm_target_path = context.scene.remt_dc_mdm_target_path
            remt_dc_mdm_target_path = bpy.path.abspath(remt_dc_mdm_target_path)

            remt_dc_mdx_target_path = context.scene.remt_dc_mdx_target_path
            remt_dc_mdx_target_path = bpy.path.abspath(remt_dc_mdx_target_path)

            DirectConversionOperator._validate_input(remt_dc_source_format,
                                                     remt_dc_md3_source_path,
                                                     remt_dc_mdc_source_path,
                                                     remt_dc_mds_source_path,
                                                     remt_dc_mdm_source_path,
                                                     remt_dc_mdx_source_path,
                                                     remt_dc_target_format,
                                                     remt_dc_md3_target_path,
                                                     remt_dc_mdc_target_path,
                                                     remt_dc_mds_target_path,
                                                     remt_dc_mdm_target_path,
                                                     remt_dc_mdx_target_path,
                                                     status)

            mdi_model = None

            # read source
            if remt_dc_source_format == 'MD3':

                import rtcw_et_model_tools.md3.facade as md3_facade

                bind_frame = 0  # TODO
                mdi_model = md3_facade.read(remt_dc_md3_source_path,
                                            bind_frame)

            elif remt_dc_source_format == 'MDC':

                import rtcw_et_model_tools.mdc.facade as mdc_facade

                bind_frame = 0  # TODO
                mdi_model = mdc_facade.read(remt_dc_mdc_source_path,
                                            bind_frame)

            elif remt_dc_source_format == 'MDS':

                import rtcw_et_model_tools.mds.facade as mds_facade

                bind_frame = 0  # TODO
                mdi_model = mds_facade.read(remt_dc_mds_source_path,
                                            bind_frame)

            elif remt_dc_source_format == 'MDM/MDX':

                import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade

                bind_frame = 0  # TODO
                mdi_model = mdmmdx_facade.read(remt_dc_mdx_source_path,
                                               remt_dc_mdm_source_path,
                                               bind_frame)

            else:  # should never happen

                cancel_msg = "input failed: source format type unknown (2)"
                status.set_canceled(cancel_msg)

            # write target
            if remt_dc_target_format == 'MD3':

                import rtcw_et_model_tools.md3.facade as md3_facade

                md3_facade.write(mdi_model, remt_dc_md3_target_path)

            elif remt_dc_target_format == 'MDC':

                import rtcw_et_model_tools.mdc.facade as mdc_facade

                mdc_facade.write(mdi_model, remt_dc_mdc_target_path)

            elif remt_dc_target_format == 'MDS':

                import rtcw_et_model_tools.mds.facade as mds_facade

                mds_facade.write(mdi_model, remt_dc_mds_target_path)

            elif remt_dc_target_format == 'MDM/MDX':

                import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade

                mdmmdx_facade.write(mdi_model, remt_dc_mdx_target_path,
                                    remt_dc_mdm_target_path)

            else:  # should never happen

                cancel_msg = "input failed: target format type unknown (2)"
                status.set_canceled(cancel_msg)

        except status.Canceled:
            pass

        status.report(self)
        return {'FINISHED'}

# Registration
# ==============================

classes = (
    DirectConversionPanel,
    DirectConversionOperator,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_dc_source_format = \
        bpy.props.EnumProperty(
            name = "Source Format",
            description = "Choose source format",
            items = [("MD3", "MD3", ""),
                     ("MDC", "MDC", ""),
                     ("MDS", "MDS", ""),
                     ("MDM/MDX", "MDM/MDX", "")],
            default = "MD3")

    bpy.types.Scene.remt_dc_md3_source_path = \
        bpy.props.StringProperty(
            name="MD3 Filepath",
            description="Path to MD3 file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mdc_source_path = \
        bpy.props.StringProperty(
            name="MDC Filepath",
            description="Path to MDC file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mds_source_path = \
        bpy.props.StringProperty(
            name="MDS Filepath",
            description="Path to MDS file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mdm_source_path = \
        bpy.props.StringProperty(
            name="MDM Filepath",
            description="Path to MDM file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mdx_source_path = \
        bpy.props.StringProperty(
            name="MDX Filepath",
            description="Path to MDX file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_target_format = \
        bpy.props.EnumProperty(
            name = "Target Format",
            description = "Choose target format",
            items = [("MD3", "MD3", ""),
                     ("MDC", "MDC", ""),
                     ("MDS", "MDS", ""),
                     ("MDM/MDX", "MDM/MDX", "")],
            default = "MD3")

    bpy.types.Scene.remt_dc_md3_target_path = \
        bpy.props.StringProperty(
            name="MD3 Filepath",
            description="Path to MD3 file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mdc_target_path = \
        bpy.props.StringProperty(
            name="MDC Filepath",
            description="Path to MDC file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mds_target_path = \
        bpy.props.StringProperty(
            name="MDS Filepath",
            description="Path to MDS file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mdm_target_path = \
        bpy.props.StringProperty(
            name="MDM Filepath",
            description="Path to MDM file",
            subtype='FILE_PATH')

    bpy.types.Scene.remt_dc_mdx_target_path = \
        bpy.props.StringProperty(
            name="MDX Filepath",
            description="Path to MDX file",
            subtype='FILE_PATH')

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_dc_source_format
    del bpy.types.Scene.remt_dc_md3_source_path
    del bpy.types.Scene.remt_dc_mdc_source_path
    del bpy.types.Scene.remt_dc_mds_source_path
    del bpy.types.Scene.remt_dc_mdm_source_path
    del bpy.types.Scene.remt_dc_mdx_source_path
    del bpy.types.Scene.remt_dc_target_format
    del bpy.types.Scene.remt_dc_md3_target_path
    del bpy.types.Scene.remt_dc_mdc_target_path
    del bpy.types.Scene.remt_dc_mds_target_path
    del bpy.types.Scene.remt_dc_mdm_target_path
    del bpy.types.Scene.remt_dc_mdx_target_path
