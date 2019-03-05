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

"""TODO
"""

bl_info = {
    "name": "RtCW/ET Model Tools",
    "author": "Norman Mitschke",
    "version": (0, 9, 0),
    "blender": (2, 80, 0),
    "location": "View3D",
    "description": "RtCW/ET Model Tools for Blender",
    "warning": "",
    "wiki_url": "",
    "category": "Object",
}

import sys
import logging

import bpy


def clear_scene():

    for object in bpy.data.objects:
        bpy.data.objects.remove(object)

    for armature in bpy.data.armatures:
        bpy.data.armatures.remove(armature)

    for collection in bpy.data.collections:
        bpy.data.collections.remove(collection)


# Panels
# ==============================

class ImportPanel(bpy.types.Panel):
    """Panel for test operations.
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


class TestsPanel(bpy.types.Panel):
    """Panel for test operations.
    """

    bl_label = "Tests"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene,
                 "remt_test_directory")

        row = layout.row()
        row.operator("remt.test_read_write_operator",
                     text="Read/Write",
                     icon="FILE_NEW")

        row = layout.row()
        row.operator("remt.test_exec",
                     text="Exec",
                     icon="BLENDER")


# Operators
# ==============================

class MD3Importer(bpy.types.Operator):
    """Import MD3 file format into blender.
    """

    bl_idname = "remt.md3_importer"
    bl_label = "Import MD3 file format into blender"
    bl_description = "Import MD3 file format into blender"

    def execute(self, context):

        clear_scene()

        import rtcw_et_model_tools.md3.facade as md3_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        md3_file_path = context.scene.remt_md3_import_path
        bind_frame = context.scene.remt_md3_bind_frame

        if not md3_file_path.endswith(".md3"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MD3 Filepath" must end with ".md3".')
            return {'CANCELLED'}

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

        clear_scene()

        import rtcw_et_model_tools.mdc.facade as mdc_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mdc_file_path = context.scene.remt_mdc_import_path
        bind_frame = context.scene.remt_mdc_bind_frame

        if not mdc_file_path.endswith(".mdc") :
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDC Filepath" must end with ".mdc".')
            return {'CANCELLED'}

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

        clear_scene()

        import rtcw_et_model_tools.mds.facade as mds_facade
        import rtcw_et_model_tools.blender.scene as blender_scene

        mds_file_path = context.scene.remt_mds_import_path
        bind_frame = context.scene.remt_mds_bind_frame

        if not mds_file_path.endswith(".mds"):
            self.report({'ERROR_INVALID_INPUT'},
                        '"MDS Filepath" must end with ".mds".')
            return {'CANCELLED'}

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

        clear_scene()

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

        if not mdm_file_path:
            mdm_file_path = None

        mdi_model = mdmmdx_facade.read(mdx_file_path, mdm_file_path,
                                       bind_frame, encoding="binary")
        blender_scene.write(mdi_model, bind_frame)

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
    ImportPanel,
    TestsPanel,
    MD3Importer,
    MDCImporter,
    MDSImporter,
    MDMMDXImporter,
    TestReadWrite,
    TestExec,
)

def register():

    # classes
    for cls in classes:

        bpy.utils.register_class(cls)

    # global ui properties
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

    bpy.types.Scene.remt_test_directory = \
        bpy.props.StringProperty(
            name="Test Directory",
            description="File path to directory of test models. If not"
                " specified the current working directory will be the test"
                " directory",
            subtype='DIR_PATH')

    # logging
    logger = logging.getLogger('remt_logger')

    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)15s %(levelname)-6s %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)


def unregister():

    # classes
    for cls in classes:

        bpy.utils.unregister_class(cls)

    # global ui properties
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

    del bpy.types.Scene.remt_test_directory

    # logging
    logger = logging.getLogger('remt_logger')
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

if __name__ == "__main__":

    register()
