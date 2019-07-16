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

class TestPanel(bpy.types.Panel):
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
        row.prop(context.scene, "remt_test_type")

        row = layout.row()
        row.prop(context.scene,
                 "remt_test_directory")

        row = layout.row()
        row.prop(context.scene, "remt_to_md3")
        row.prop(context.scene, "remt_to_mdc")
        row.prop(context.scene, "remt_to_mds")
        row.prop(context.scene, "remt_to_mdmmdx")

        if context.scene.remt_test_type == "Read/Write":

            row = layout.row()
            row.operator("remt.test_read_write_operator",
                        text="Exec",
                        icon="BLENDER")

        if context.scene.remt_test_type == "Direct Conversion":

            row = layout.row()
            row.operator("remt.test_direct_conversion_operator",
                        text="Exec",
                        icon="BLENDER")

        if context.scene.remt_test_type == "Random":

            row = layout.row()
            row.operator("remt.test_exec",
                        text="Exec",
                        icon="BLENDER")


# Operators
# ==============================

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


class TestDirectConversion(bpy.types.Operator):
    """Tests direction conversion.
    """

    bl_idname = "remt.test_direct_conversion_operator"
    bl_label = "RtCW/ET Test Direct Conversion Operator"
    bl_description = "Tests direct conversion."

    def execute(self, context):

        import rtcw_et_model_tools.tests.test_manager

        test_directory = context.scene.remt_test_directory
        to_md3 = context.scene.remt_to_md3
        to_mdc = context.scene.remt_to_mdc
        to_mds = context.scene.remt_to_mds
        to_mdmmdx = context.scene.remt_to_mdmmdx
        settings = rtcw_et_model_tools.tests.test_manager. \
            TestParameters(test_directory, to_md3, to_mdc, to_mds, to_mdmmdx)
        rtcw_et_model_tools.tests.test_manager. \
            TestManager.run_test("test_direct_conversion", settings)

        return {'FINISHED'}


class TestExec(bpy.types.Operator):
    """For internal testing, gets removed later.
    """

    bl_idname = "remt.test_exec"
    bl_label = "RtCW/ET Test Exec Operator"
    bl_description = "Execute something"

    def execute(self, context):

        import os
        import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade
        import rtcw_et_model_tools.mdi.mdi as mdi
        import rtcw_et_model_tools.tests.random_test as random_test

        # file_path_mdm = \
        #     os.path.join("C:\\Users\\nm\\Desktop\\test_dir", "body.mdm")
        # file_path_mdx = \
        #     os.path.join("C:\\Users\\nm\\Desktop\\test_dir", "body.mdx")

        # file_path_mdm_o = \
        #     os.path.join("C:\\Users\\nm\\Desktop\\test_dir", "body_o.mdm")
        # file_path_mdx_o = \
        #     os.path.join("C:\\Users\\nm\\Desktop\\test_dir", "body_o.mdx")

        # mdi_model = mdmmdx_facade.read(file_path_mdx, file_path_mdm, 0)

        #random_test.random_test(mdi_model)
        random_test.random_test()

        # mdmmdx_facade.write(mdi_model, file_path_mdx_o, file_path_mdm_o)

        return {'FINISHED'}


# Registration
# ==============================

classes = (
    TestPanel,
    TestReadWrite,
    TestDirectConversion,
    TestExec,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_test_type = \
        bpy.props.EnumProperty(
            name = "Test Type",
            description = "Choose test type",
            items = [("Read/Write", "Read/Write", ""),
                     ("Direct Conversion", "Direct Conversion", ""),
                     ("Random", "Random", "")],
            default = "Read/Write")

    bpy.types.Scene.remt_test_directory = \
        bpy.props.StringProperty(
            name="Test Directory",
            description="File path to directory of test models. If not"
                " specified the current working directory will be the test"
                " directory",
            subtype='DIR_PATH')

    bpy.types.Scene.remt_to_md3 = \
        bpy.props.BoolProperty(
            name="MD3",
            description="Convert to md3",
            default=False,
        )

    bpy.types.Scene.remt_to_mdc = \
        bpy.props.BoolProperty(
            name="MDC",
            description="Convert to mdc",
            default=False,
        )

    bpy.types.Scene.remt_to_mds = \
        bpy.props.BoolProperty(
            name="MDS",
            description="Convert to mds",
            default=False,
        )

    bpy.types.Scene.remt_to_mdmmdx = \
        bpy.props.BoolProperty(
            name="MDM/MDX",
            description="Convert to mdm/mdx",
            default=False,
        )

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_test_type
    del bpy.types.Scene.remt_test_directory
    del bpy.types.Scene.remt_to_md3
    del bpy.types.Scene.remt_to_mdc
    del bpy.types.Scene.remt_to_mds
    del bpy.types.Scene.remt_to_mdmmdx

