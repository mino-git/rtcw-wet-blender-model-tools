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

"""Direct conversion.
"""

import bpy


class REMT_PT_DirectConversion(bpy.types.Panel):
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

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mds_collapse_frame")                      

        elif context.scene.remt_dc_target_format == "MDM/MDX":

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdm_target_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdx_target_path")

            row = layout.row()
            row.prop(context.scene,
                    "remt_dc_mdmmdx_collapse_frame")                    

        else:

            pass

        row = layout.row()
        row.operator("remt.remt_direct_conversion",
                     text="Convert",
                     icon="PLUGIN")


class REMT_OT_DirectConversion(bpy.types.Operator):
    """Operator for direct conversion operation.
    """

    bl_idname = "remt.remt_direct_conversion"
    bl_label = "Direct Conversion"
    bl_description = "Convert one type of model format to another without" \
        " writing to blender scene"

    @staticmethod
    def _parse_input(context):

        source_format = context.scene.remt_dc_source_format

        md3_source_path = context.scene.remt_dc_md3_source_path
        md3_source_path = bpy.path.abspath(md3_source_path)

        mdc_source_path = context.scene.remt_dc_mdc_source_path
        mdc_source_path = bpy.path.abspath(mdc_source_path)

        mds_source_path = context.scene.remt_dc_mds_source_path
        mds_source_path = bpy.path.abspath(mds_source_path)

        mdm_source_path = context.scene.remt_dc_mdm_source_path
        mdm_source_path = bpy.path.abspath(mdm_source_path)

        mdx_source_path = context.scene.remt_dc_mdx_source_path
        mdx_source_path = bpy.path.abspath(mdx_source_path)

        target_format = context.scene.remt_dc_target_format

        md3_target_path = context.scene.remt_dc_md3_target_path
        md3_target_path = bpy.path.abspath(md3_target_path)

        mdc_target_path = context.scene.remt_dc_mdc_target_path
        mdc_target_path = bpy.path.abspath(mdc_target_path)

        mds_target_path = context.scene.remt_dc_mds_target_path
        mds_target_path = bpy.path.abspath(mds_target_path)

        mdm_target_path = context.scene.remt_dc_mdm_target_path
        mdm_target_path = bpy.path.abspath(mdm_target_path)

        mdx_target_path = context.scene.remt_dc_mdx_target_path
        mdx_target_path = bpy.path.abspath(mdx_target_path)

        mdmmdx_collapse_frame = context.scene.remt_dc_mdmmdx_collapse_frame
        mds_collapse_frame = context.scene.remt_dc_mds_collapse_frame

        return (source_format,
                md3_source_path,
                mdc_source_path,
                mds_source_path,
                mdm_source_path,
                mdx_source_path,
                target_format,
                md3_target_path,
                mdc_target_path,
                mds_target_path,
                mdm_target_path,
                mdx_target_path,
                mdmmdx_collapse_frame,
                mds_collapse_frame)

    def execute(self, context):
        """Directly convert between model formats without involving Blender.
        """

        import rtcw_et_model_tools.common.direct_conversion as dc_m
        import rtcw_et_model_tools.common.timer as timer_m
        import rtcw_et_model_tools.common.reporter as reporter_m

        reporter_m.reset_state()

        try:

            timer = timer_m.Timer()
            reporter_m.info("Direct conversion started ...")

            source_format, \
            md3_source_path, \
            mdc_source_path, \
            mds_source_path, \
            mdm_source_path, \
            mdx_source_path, \
            target_format, \
            md3_target_path, \
            mdc_target_path, \
            mds_target_path, \
            mdm_target_path, \
            mdx_target_path, \
            mdmmdx_collapse_frame, \
            mds_collapse_frame \
                = self._parse_input(context)

            if source_format == 'MD3' and target_format == 'MD3':

                reporter_m.info("Direct conversion of MD3 to MD3")

                dc_m.md3_to_md3(md3_source_path, md3_target_path)

            elif source_format == 'MD3' and target_format == 'MDC':

                reporter_m.info("Direct conversion of MD3 to MDC")

                dc_m.md3_to_mdc(md3_source_path, mdc_target_path)

            elif source_format == 'MD3' and target_format == 'MDS':

                reporter_m.info("Direct conversion of MD3 to MDS")

                dc_m.md3_to_mds(md3_source_path, mds_target_path)

            elif source_format == 'MD3' and target_format == 'MDM/MDX':

                reporter_m.info("Direct conversion of MD3 to MDM/MDX")

                dc_m.md3_to_mdmmdx(md3_source_path,
                                   mdm_target_path,
                                   mdx_target_path)

            elif source_format == 'MDC' and target_format == 'MD3':

                reporter_m.info("Direct conversion of MDC to MD3")

                dc_m.mdc_to_md3(mdc_source_path, md3_target_path)

            elif source_format == 'MDC' and target_format == 'MDC':

                reporter_m.info("Direct conversion of MDC to MDC")

                dc_m.mdc_to_mdc(mdc_source_path, mdc_target_path)

            elif source_format == 'MDC' and target_format == 'MDS':

                reporter_m.info("Direct conversion of MDC to MDS")

                dc_m.mdc_to_mds(mdc_source_path, mds_target_path)

            elif source_format == 'MDC' and target_format == 'MDM/MDX':

                reporter_m.info("Direct conversion of MDC to MDM/MDX")

                dc_m.mdc_to_mdmmdx(mdc_source_path,
                                   mdm_target_path,
                                   mdx_target_path)

            elif source_format == 'MDS' and target_format == 'MD3':

                reporter_m.info("Direct conversion of MDS to MD3")

                dc_m.mds_to_md3(mds_source_path, md3_target_path)

            elif source_format == 'MDS' and target_format == 'MDC':

                reporter_m.info("Direct conversion of MDS to MDC")

                dc_m.mds_to_mdc(mds_source_path, mdc_target_path)

            elif source_format == 'MDS' and target_format == 'MDS':

                reporter_m.info("Direct conversion of MDS to MDS")

                dc_m.mds_to_mds(mds_source_path, mds_target_path,
                                mds_collapse_frame)

            elif source_format == 'MDS' and target_format == 'MDM/MDX':

                reporter_m.info("Direct conversion of MDS to MDM/MDX")

                dc_m.mds_to_mdmmdx(mds_source_path,
                                   mdm_target_path,
                                   mdx_target_path,
                                   mdmmdx_collapse_frame)

            elif source_format == 'MDM/MDX' and target_format == 'MD3':

                reporter_m.info("Direct conversion of MDM/MDX to MD3")

                dc_m.mdmmdx_to_md3(mdm_source_path,
                                   mdx_source_path,
                                   md3_target_path)

            elif source_format == 'MDM/MDX' and target_format == 'MDC':

                reporter_m.info("Direct conversion of MDM/MDX to MDC")

                dc_m.mdmmdx_to_mdc(mdm_source_path,
                                   mdx_source_path,
                                   mdc_target_path)

            elif source_format == 'MDM/MDX' and target_format == 'MDS':

                reporter_m.info("Direct conversion of MDM/MDX to MDS")

                dc_m.mdmmdx_to_mds(mdm_source_path,
                                   mdx_source_path,
                                   mds_target_path,
                                   mds_collapse_frame)

            elif source_format == 'MDM/MDX' and target_format == 'MDM/MDX':

                reporter_m.info("Direct conversion of MDM/MDX to MDM/MDX")

                dc_m.mdmmdx_to_mdmmdx(mdm_source_path,
                                      mdx_source_path,
                                      mdm_target_path,
                                      mdx_target_path,
                                      mdmmdx_collapse_frame)
            else:

                raise Exception("Format not supported")

            time = timer.time()
            reporter_m.info("Direct conversion DONE (time={})".format(time))

        except Exception as error:

            reporter_m.exception(error)
            self.report({'ERROR'}, error.__str__())
            return {'CANCELLED'}

        return {'FINISHED'}

# Registration
# ==============================

classes = (
    REMT_PT_DirectConversion,
    REMT_OT_DirectConversion,
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

    bpy.types.Scene.remt_dc_mdmmdx_collapse_frame = \
        bpy.props.IntProperty(
            name = "Collapse Frame",
            description = "Collapse frame for LOD data",
            default = 0,
            min = 0,
            max = 1000000
            )

    bpy.types.Scene.remt_dc_mds_collapse_frame = \
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
    del bpy.types.Scene.remt_dc_mdmmdx_collapse_frame
    del bpy.types.Scene.remt_dc_mds_collapse_frame
