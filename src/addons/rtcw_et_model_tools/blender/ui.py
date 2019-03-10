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

"""Blender user interface.
"""

import bpy


class Import(bpy.types.Panel):
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


class Tools(bpy.types.Panel):
    """Panel for tool operations.
    """

    bl_label = "Tools"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        box = row.box()

        box.label(text="Attach To Tag:", icon="OUTLINER_OB_EMPTY")

        box.prop(context.scene, "remt_attach_to_tag_method")

        row = box.row()
        row.operator("remt.attach_to_tag",
                     text="Attach",
                     icon="EMPTY_DATA")


class Tests(bpy.types.Panel):
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

# Registration
# ==============================

classes = (
    Import,
    Tools,
    Tests,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    # Import props
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

    # Tools props
    bpy.types.Scene.remt_attach_to_tag_method = \
        bpy.props.EnumProperty(
            name = "Method",
            description = "Choose to attach by selected objects or selected" \
                          " collection",
            items = [("Objects", "Objects", ""),
                     ("Collection", "Collection", "")],
            default = "Objects")

    # Tests props
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

    # Import props
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

    # Tools props
    del bpy.types.Scene.remt_attach_to_tag_method

    # Tests props
    del bpy.types.Scene.remt_test_directory
