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

"""Blender tools for dealing with the model formats.
"""

import bpy
import mathutils


class AttachToTag:
    """Attach to tag operation. This operation mimics the games behavior of
    attaching external meshes to a given mesh in Blender.
    """

    @staticmethod
    def _add_child_of_constraint(attach_object, tag_object):
        """This uses a child of constraint to mimic attaching.

        Args:

            attach_object: attach object.
            tag_object: tag object.
        """

        attach_object.constraints.new(type="CHILD_OF")
        attach_object.constraints["Child Of"].target = tag_object

        attach_object.constraints["Child Of"].use_location_x = True
        attach_object.constraints["Child Of"].use_location_y = True
        attach_object.constraints["Child Of"].use_location_z = True

        attach_object.constraints["Child Of"].use_rotation_x = True
        attach_object.constraints["Child Of"].use_rotation_y = True
        attach_object.constraints["Child Of"].use_rotation_z = True

        attach_object.constraints["Child Of"].use_scale_x = True
        attach_object.constraints["Child Of"].use_scale_y = True
        attach_object.constraints["Child Of"].use_scale_z = True

    @staticmethod
    def _is_tag_object(tag_object, status):
        """Checks if the object is a tag object.

        Args:

            tag_object: tag object.
            status: status object.

        Returns:

            bool.
        """

        if tag_object is None:

            status.was_canceled = True
            status.cancel_msg = "active object not found"
            return False

        if not tag_object.type == 'EMPTY':

            status.was_canceled = True
            status.cancel_msg = "tag object not found. The tag object" \
                " must be the active object of type 'EMPTY'"
            return False

        if not tag_object.empty_display_type == 'ARROWS':

            status.was_canceled = True
            status.cancel_msg = "tag object not found. The tag object" \
                " must be the active object of type 'EMPTY' and display type" \
                "'ARROWS'"
            return False

        if not tag_object.name.startswith("tag_") or False:

            status.was_canceled = True
            status.cancel_msg = "tag object not found. The tag object" \
                " is of correct type, but its name must be prefixed with" \
                " '_tag' or it must have a custom flag property (not" \
                " implemented)"
            return False

    @staticmethod
    def _is_attach_object(attach_object, tag_object, status):
        """Checks if an object can be attached to a tag object.

        Args:

            attach_object: attach object.
            tag_object: tag object.
            status: status object.

        Returns:

            bool.
        """

        if attach_object is tag_object:
            return False

        correct_type = False

        if attach_object.type == 'MESH':
            correct_type = True

        if attach_object.type == 'EMPTY' and \
            attach_object.empty_display_type == 'ARROWS':
            correct_type = True

        if not correct_type:
            return False

        for constraint in attach_object.constraints:

            if constraint.type == 'CHILD_OF' and \
                constraint.target is tag_object:

                status.warning_msgs.append("attach object with name '{}'" \
                    " already attached and was filtered" \
                    .format(attach_object.name))
                return False

        return True

    @staticmethod
    def exec(method, status):
        """Attaches a selection of objects to the origin and orientation of a
        tag object. A tag object is represented as an 'EMPTY' object with
        display type 'ARROWS' inside Blender. It must be the active object
        (usually the last object selected). This operation first does some
        checks if attachment is possible, then attaches all valid objects by
        setting a 'CHILD_OF' constraint.

        Args:

            method (str): defines how a user selects a number of attachable
                objects.

            Returns:

                status (Status): status object for error reporting.
        """

        tag_object = bpy.context.view_layer.objects.active

        if AttachToTag._is_tag_object(tag_object, status):

            pass

        else:

            if status.was_canceled:
                return status

        attach_objects = []

        if method == "Objects":

            # use selected objects as method, this will collect all objects
            # the user manually selected
            for obj in bpy.context.selected_objects:

                if AttachToTag._is_attach_object(obj, tag_object, \
                                                 status):

                    attach_objects.append(obj)

                else:

                    if status.was_canceled:
                        return status

        elif method == "Collection":

            # use active collection as method, this will collect all objects
            # inside a collection and its children collection
            active_collection = \
                bpy.context.view_layer.active_layer_collection.collection

            for obj in active_collection.all_objects:

                if AttachToTag._is_attach_object(obj, tag_object, \
                                                status):

                    attach_objects.append(obj)

                else:

                    if status.was_canceled:
                        return status

        else:

            status.was_canceled = True
            status.cancel_msg = "unkown method"
            return status

        if len(attach_objects) == 0:

            status.was_canceled = True
            status.cancel_msg = "no objects to attach or objects were filtered"
            return status

        for attach_object in attach_objects:

            AttachToTag._add_child_of_constraint(attach_object, tag_object)

        return status
