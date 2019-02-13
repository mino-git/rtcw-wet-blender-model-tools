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

import bpy

import rtcw_et_model_tools.tests.unittests.runner


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


class TestReadWriteOperator(bpy.types.Operator):
    """Tests reading from and writing to file.
    """

    bl_idname = "remt.test_read_write_operator"
    bl_label = "RtCW/ET Test Read/Write Operator"
    bl_description = "Tests file read/write operations. Tests all models" \
                     " found in the test directory. A duplicate of each file" \
                     " will be created on disk to compare results."

    def execute(self, context):

        test_directory = context.scene.remt_test_directory
        settings = rtcw_et_model_tools.tests.unittests.runner. \
            TestParameters(test_directory)
        rtcw_et_model_tools.tests.unittests.runner. \
            TestManager.run_test("test_binary_read_write", settings)

        return {'FINISHED'}

    @classmethod
    def register(cls):

        pass

    @classmethod
    def unregister(cls):

        pass


classes = (
    TestsPanel,
    TestReadWriteOperator,
)

def register():

    for cls in classes:

        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_test_directory = \
        bpy.props.StringProperty(
            name="Test Directory",
            description="File path to directory of test models. If not"
                " specified the current working directory will be the test"
                " directory",
            subtype='DIR_PATH')

def unregister():

    for cls in classes:

        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_test_directory


if __name__ == "__main__":

    register()
