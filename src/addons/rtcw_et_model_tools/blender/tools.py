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
import mathutils


def attach_to_tag(method = "Objects"):

    tag_object = bpy.context.view_layer.objects.active

    if tag_object is None:

        status = 'CANCELLED'
        msg = "No active objects found."
        return (status, msg)

    if not tag_object.empty_display_type == 'ARROWS':

        status = 'CANCELLED'
        msg = "Parent object must be tag (type='EMPTY', display_type='ARROWS'"
        return (status, msg)

    if not tag_object.name.startswith("tag_") or False:

        status = 'CANCELLED'
        msg = "Parent object must be tag (name starts with 'tag_' or has" \
            " flag.)"
        return (status, msg)

    attach_objects = []

    if method == "Collection":

        for object in bpy.context.selected_objects:

            if object is tag_object:
                continue

            # TODO check if already attached

            attach_objects.append(object)

    elif method == "Objects":

        active_layer_collection = \
            bpy.context.view_layer.active_layer_collection
        for object in active_layer_collection.collection.objects:

            if object is tag_object:
                continue

            # TODO check if already attached

            attach_objects.append(object)

    else:

        status = 'CANCELLED'
        msg = "Unknown method."
        return (status, msg)

    for attach_object in attach_objects:

        # TODO check other constraints

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

    status = 'SUCCESS'
    msg = ""
    return (status, msg)
