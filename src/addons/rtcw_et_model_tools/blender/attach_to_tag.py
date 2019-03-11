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

"""Attach to tag command (known from the games) inside Blender.
"""

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi_util


def _add_child_of_constraint(attach_object, tag_object):
    """Attaches an object to a tag object by adding a child of constraint.

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


def _is_tag_object(tag_object, status):
    """Checks if the object is a tag object.

    Args:

        tag_object: tag object.
        status: status object.

    Returns:

        bool.
    """

    if tag_object is None:
        cancel_msg = "tag object not found. Must be active object (last" \
            " selected"
        status.set_canceled(cancel_msg)
        return False

    correct_type = False
    if tag_object.type == 'EMPTY' and \
        tag_object.empty_display_type == 'ARROWS':
        correct_type = True
    if not correct_type:
        cancel_msg = "tag object not found. Must be of type='EMPTY'," \
            " display_type='ARROWS'"
        status.set_canceled(cancel_msg)
        return False

    if not tag_object.name.startswith("tag_") or False:
        cancel_msg = "tag object not found. Must have prefix '_tag' or flag" \
            " property"
        status.set_canceled(cancel_msg)
        return False


def _is_attach_object(attach_object, tag_object, status):
    """Checks if the object can be attached to the tag object.

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
    if attach_object.type == 'MESH' or (attach_object.type == 'EMPTY' and \
        attach_object.empty_display_type == 'ARROWS'):
        correct_type = True
    if not correct_type:
        return False

    for constraint in attach_object.constraints:

        if constraint.type == 'CHILD_OF' and \
            constraint.target is tag_object:

            warning_msg = "attach object with name '{}' already attached and" \
                " was filtered".format(attach_object.name)
            status.add_warning_msg(warning_msg)
            return False

    return True

def _collect_attach_objects_from_selected_objects(attach_objects, tag_object,
                                                  status):
    """Collects all attachable objects the user manually selected.

    Args:

        attach_objects: list of attachable objects to append to.
        tag_object: tag object.
        status: status object.
    """

    for obj in bpy.context.selected_objects:

        if _is_attach_object(obj, tag_object, status):
            attach_objects.append(obj)
        else:
            if status.was_canceled:
                return

def _collect_attach_objects_from_active_collection(attach_objects, tag_object,
                                                   status):
    """Collects all attachable objects from an active collection (and its
    children collections).

    Args:

        attach_objects: list of attachable objects to append to.
        tag_object: tag object.
        status: status object.
    """

    active_collection = \
        bpy.context.view_layer.active_layer_collection.collection

    for obj in active_collection.all_objects:

        if _is_attach_object(obj, tag_object, status):
            attach_objects.append(obj)
        else:
            if status.was_canceled:
                return

def execute(method, status):
    """Attach to tag operation. This operation mimics the games behavior of
    attaching external meshes to a given mesh in Blender. Attachment means
    the location and origin of an object gets attached to the tags location
    and origin.

    A tag object is represented as an 'EMPTY' object with display type
    'ARROWS' inside Blender. It must be the active object (usually the last
    object selected). This operation first does some checks if attachment is
    possible, then attaches all valid objects by setting a 'CHILD_OF'
    constraint.

    Args:

        method (str): defines how a user selects a number of attachable
            objects.
        status (Status): status object for warning and error reporting.
    """

    tag_object = bpy.context.view_layer.objects.active

    if not _is_tag_object(tag_object, status):
        if status.was_canceled:
            return

    attach_objects = []

    if method == "Objects":
        _collect_attach_objects_from_selected_objects(attach_objects,
                                                      tag_object,
                                                      status)
        if status.was_canceled:
            return

    elif method == "Collection":
        _collect_attach_objects_from_active_collection(attach_objects,
                                                       tag_object,
                                                       status)
        if status.was_canceled:
            return

    else:

        status.set_canceled("unknown method")
        return

    if len(attach_objects) == 0:

        status.set_canceled("no objects to attach or objects were filtered")
        return

    for attach_object in attach_objects:

        _add_child_of_constraint(attach_object, tag_object)
