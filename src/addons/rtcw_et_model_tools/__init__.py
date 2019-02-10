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
    "location": "View3d > Tools > RtCW/ET",
    "version": (0, 9, 0),
    "blender": (2, 7, 9),
    "description": "RtCW/ET Model Tools for Blender",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Development",
}

import bpy
import os

import rtcw_et_model_tools.controller


class TestOperator(bpy.types.Operator):

    bl_idname = "rtcw_et_model_tools.test_operator"
    bl_label = 'RtCW/ET Test Operator'

    def execute(self, context):

        working_directory = bpy.path.abspath(context.scene.working_directory)

        rtcw_et_model_tools.controller.run_unit_tests(working_directory)

        return {'FINISHED'}

    @classmethod
    def register(cls):

        pass

    @classmethod
    def unregister(cls):

        pass


class TestPanel(bpy.types.Panel):

    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "RtCW/ET"
    bl_label = "RtCW/ET Model Tools"
    bl_context = "objectmode"

    def draw(self, context):

        box = self.layout.box()
        box.prop(context.scene, "working_directory")

        box = self.layout.box()
        box.operator("rtcw_et_model_tools.test_operator", text="Run Tests")

    @classmethod
    def register(cls):

        bpy.types.Scene.working_directory \
            = bpy.props.StringProperty(name = "Working Directory",
                                       default = "",
                                       description = "Filepath to mesh data (.mdm)",
                                       subtype = "FILE_PATH")

        bpy.types.Scene.test_operator \
            = bpy.props.StringProperty(name = "",
                                       description = "description",
                                       default = "Test")


    @classmethod
    def unregister(cls):

        del bpy.types.Scene.working_directory
        del bpy.types.Scene.test_operator


def register():

    bpy.utils.register_class(TestOperator)
    bpy.utils.register_class(TestPanel)


def unregister():

    bpy.utils.unregister_module(__name__)


if __name__ == "__main__":

    try:
        unregister()
    except Exception as e:
        print(e)
        pass

    register()
