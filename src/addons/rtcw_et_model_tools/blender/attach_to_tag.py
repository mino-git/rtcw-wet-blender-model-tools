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

"""Mimics the games known method of attaching external models to a tag inside a
model.
"""

import os

import bpy


# UI
# ==============================

class AttachToTagPanel(bpy.types.Panel):
    """Panel for attach to tag operation.
    """

    bl_label = "Attach To Tag"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()

        row.prop(context.scene, "remt_attach_to_tag_method")

        row = layout.row()
        row.operator("remt.attach_to_tag",
                     text="Attach",
                     icon="EMPTY_DATA")


# Operators
# ==============================

class AttachToTag(bpy.types.Operator):
    """Attach objects to a tag.
    """

    bl_idname = "remt.attach_to_tag"
    bl_label = "Attach"
    bl_description = "Attach a selection of objects to a tag."

    @staticmethod
    def _add_child_of_constraint(child_object, parent_object, status):
        """Adds a child-of constraint.
        """

        for constraint in child_object.constraints:
            if constraint.type == 'CHILD_OF' and \
                constraint.target is parent_object:
                warning_msg = "attach object with name '{}' already attached" \
                    " and was filtered".format(child_object.name)
                status.add_warning_msg(warning_msg)
                return False

        child_object.constraints.new(type="CHILD_OF")
        child_object.constraints["Child Of"].target = parent_object

        child_object.constraints["Child Of"].use_location_x = True
        child_object.constraints["Child Of"].use_location_y = True
        child_object.constraints["Child Of"].use_location_z = True

        child_object.constraints["Child Of"].use_rotation_x = True
        child_object.constraints["Child Of"].use_rotation_y = True
        child_object.constraints["Child Of"].use_rotation_z = True

        child_object.constraints["Child Of"].use_scale_x = True
        child_object.constraints["Child Of"].use_scale_y = True
        child_object.constraints["Child Of"].use_scale_z = True

        return True

    @staticmethod
    def _is_tag_object(tag_object, status):
        """Checks if tag object.

        A tag is represented as an object of type 'EMPTY', display type
        'ARROWS' inside Blender.
        """

        if tag_object is None:
            cancel_msg = "tag object is none"
            status.set_canceled(cancel_msg)

        correct_type = False
        if tag_object.type == 'EMPTY' and \
            tag_object.empty_display_type == 'ARROWS':
            correct_type = True
        if not correct_type:
            cancel_msg = "tag object not found. Must be of type='EMPTY'," \
                " display_type='ARROWS'"
            status.set_canceled(cancel_msg)

        if not tag_object.name.startswith("tag_") or False:
            cancel_msg = "tag object not found. Must have prefix 'tag_' or" \
                " flag property"
            status.set_canceled(cancel_msg)

        return True

    @staticmethod
    def _is_attach_object(attach_object, status):
        """Checks if attachable object.

        Only mesh objects and tag objects can be attached.
        """

        if attach_object is None:
            warning_msg = "attach object is none"
            status.add_warning_msg(warning_msg)
            return False

        correct_type = False
        if attach_object.type == 'MESH' or \
            (attach_object.type == 'EMPTY' and \
                attach_object.empty_display_type == 'ARROWS'):
            correct_type = True
        if not correct_type:
            return False

        return True

    @staticmethod
    def _validate_input(method, status):
        """Validate input.
        """

        if not method:
            cancel_msg = "input failed: no method"
            status.set_canceled(cancel_msg)

        if not isinstance(method, str):
            cancel_msg = "input failed: method must be string"
            status.set_canceled(cancel_msg)

        method_exists = False
        if method == "Objects" or method == "Collection":
            method_exists = True
        if not method_exists:
            cancel_msg = "input failed: method not found"
            status.set_canceled(cancel_msg)

    @staticmethod
    def _attach_by_objects(status):
        """Attach all selected objects to tag by setting a child-of constraint.
        """

        tag_object = bpy.context.view_layer.objects.active
        if not AttachToTag._is_tag_object(tag_object, status):
            cancel_msg = "tag object not found"
            status.set_canceled(cancel_msg)

        attach_objects = []
        for selected_object in bpy.context.selected_objects:
            if AttachToTag._is_attach_object(selected_object, status) and \
               selected_object is not tag_object:
                attach_objects.append(selected_object)

        if not attach_objects:
            cancel_msg = "attach objects not found or filtered"
            status.set_canceled(cancel_msg)

        for attach_object in attach_objects:
            AttachToTag._add_child_of_constraint(attach_object, tag_object,
                                                 status)

    @staticmethod
    def _attach_by_collection(status):
        """Attach all objects from active collection to tag by setting a
        child-of constraint.
        """

        tag_object = bpy.context.view_layer.objects.active
        if not AttachToTag._is_tag_object(tag_object, status):
            cancel_msg = "tag object not found"
            status.set_canceled(cancel_msg)

        attach_objects = []
        active_collection = \
            bpy.context.view_layer.active_layer_collection.collection
        for obj in active_collection.all_objects:
            if AttachToTag._is_attach_object(obj, status) and \
               obj is not tag_object:
                attach_objects.append(obj)

        if not attach_objects:
            cancel_msg = "attach objects not found or filtered"
            status.set_canceled(cancel_msg)

        for attach_object in attach_objects:
            AttachToTag._add_child_of_constraint(attach_object, tag_object,
                                                 status)

    def execute(self, context):
        """Attach to tag operation.
        """

        import rtcw_et_model_tools.blender.status as status
        status = status.Status()

        try:

            method = context.scene.remt_attach_to_tag_method
            AttachToTag._validate_input(method, status)

            if method == 'Objects':
                AttachToTag._attach_by_objects(status)

            elif method == 'Collection':
                AttachToTag._attach_by_collection(status)

            else:  # should never happen

                cancel_msg = "unknown method"
                status.set_canceled(cancel_msg)

        except status.Canceled:
            pass

        status.report(self)
        return {'FINISHED'}

# Registration
# ==============================

classes = (
    AttachToTagPanel,
    AttachToTag,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.remt_attach_to_tag_method = \
        bpy.props.EnumProperty(
            name = "Method",
            description = "Defines how objects are selected for attachment",
            items = [("Objects", "Objects", ""),
                     ("Collection", "Collection", "")],
            default = "Objects")

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.remt_attach_to_tag_method
