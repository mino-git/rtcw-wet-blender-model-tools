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

"""Blender operators.
"""

import bpy


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
        blender_scene.write(mdi_model, bind_frame)

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
        blender_scene.write(mdi_model, bind_frame)

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
        blender_scene.write(mdi_model, bind_frame)

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
        blender_scene.write(mdi_model, bind_frame)

        return {'FINISHED'}


class AttachToTag(bpy.types.Operator):
    """Attach objects to a tag.
    """

    bl_idname = "remt.attach_to_tag"
    bl_label = "Attach"
    bl_description = "Attach a selection of objects to a tag. It works like" \
        " parenting with CTRL + P. First select the objects, then the target" \
        " empty, then press this button. Requirements: the target tag" \
        " must be an object of type 'EMPTY', draw type 'ARROWS'. Its name" \
        " must start with 'tag_' or have a property flag (not implemented yet)"

    def execute(self, context):

        import rtcw_et_model_tools.blender.attach_to_tag as attach_to_tag
        import rtcw_et_model_tools.mdi.mdi_util as mdi_util

        method = context.scene.remt_attach_to_tag_method
        status = mdi_util.Status()
        attach_to_tag.execute(method, status)

        cancel_report, warning_report = status.prepare_report()
        if cancel_report:
            self.report({'ERROR'}, cancel_report)
        if warning_report:
            self.report({'WARNING'}, warning_report)

        return {'FINISHED'}


class TestReadWrite(bpy.types.Operator):
    """Tests reading from and writing to file.
    """

    bl_idname = "remt.test_read_write_operator"
    bl_label = "RtCW/ET Test Read/Write Operator"
    bl_description = "Tests file read/write operations. Tests all models" \
                     " found in the test directory. A duplicate of each file" \
                     " will be created on disk to compare results."

    def execute(self, context):

        import rtcw_et_model_tools.tests.test_manager

        test_directory = context.scene.remt_test_directory
        settings = rtcw_et_model_tools.tests.test_manager. \
            TestParameters(test_directory)
        rtcw_et_model_tools.tests.test_manager. \
            TestManager.run_test("test_binary_read_write", settings)

        return {'FINISHED'}


class TestExec(bpy.types.Operator):
    """For internal testing, gets removed later.
    """

    bl_idname = "remt.test_exec"
    bl_label = "RtCW/ET Test Exec Operator"
    bl_description = "Execute something"

    def execute(self, context):

        return {'FINISHED'}


# Registration
# ==============================

classes = (
    MD3Importer,
    MDCImporter,
    MDSImporter,
    AttachToTag,
    MDMMDXImporter,
    TestReadWrite,
    TestExec,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)
