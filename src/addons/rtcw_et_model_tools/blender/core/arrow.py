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

"""Attach to tag operation, and reading/writing/converting an arrow object.
Arrows represent tags.
"""

import os

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.blender.util as blender_util_m
import rtcw_et_model_tools.common.skin_file as skin_file_m
import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


# =====================================
# ATTACH TO TAG OPERATION
# =====================================

def _add_child_of_constraint(child_object, parent_object):
    """Adds a child-of constraint.
    """

    for constraint in child_object.constraints:
        if constraint.type == 'CHILD_OF' and \
            constraint.target is parent_object:

            reporter_m.warning("attach object with name '{}' already attached"
                               " and was filtered".format(child_object.name))
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

def _is_attach_object(attach_object):
    """Checks if attachable object. Only mesh objects and tag objects can be
    attached.
    """

    if not attach_object:
        return False

    is_mesh_object = attach_object.type == 'MESH'
    is_tag = is_tag_object(attach_object)
    if not (is_mesh_object or is_tag):
        return False

    return True

def is_tag_object(tag_object):
    """Checks if tag object. A tag is represented as an object of type 'EMPTY',
    display type 'ARROWS' and prefixed by 'tag_'.
    """

    if not tag_object:
        return False

    if not tag_object.type == 'EMPTY':
        return False

    if not tag_object.empty_display_type == 'ARROWS':
        return False

    if not tag_object.name.startswith("tag_"):
        return False

    return True

def _import_tag_model(game_path, skin_file_path, tag_name, model_path):
    """Import a tag model. These are either md3 or mdc models."""

    import rtcw_et_model_tools.md3.facade as md3_facade
    import rtcw_et_model_tools.mdc.facade as mdc_facade
    import rtcw_et_model_tools.blender.core.collection as collection_m

    # paths relative to game directory
    model_path_1 = os.path.join(game_path, model_path)
    model_path_md3_1 = "{}.{}".format(model_path_1, "md3")
    model_path_mdc_1 = "{}.{}".format(model_path_1, "mdc")

    # paths relative to skin file directory
    skin_file_dir = os.path.dirname(os.path.realpath(skin_file_path))
    model_path_2 = os.path.join(skin_file_dir, model_path)
    model_path_md3_2= "{}.{}".format(model_path_2, "md3")
    model_path_mdc_2 = "{}.{}".format(model_path_2, "mdc")

    # try to find it relative to game data path
    if os.path.isfile(model_path_md3_1):

        bind_frame = 0
        mdi_model = md3_facade.read(model_path_md3_1, bind_frame)
        collection = collection_m.write(mdi_model)

    elif os.path.isfile(model_path_mdc_1):

        bind_frame = 0
        mdi_model = mdc_facade.read(model_path_mdc_1, bind_frame)
        collection = collection_m.write(mdi_model)

    # try to find it relative to the skin file path
    elif os.path.isfile(model_path_md3_2):

        bind_frame = 0
        mdi_model = md3_facade.read(model_path_md3_2, bind_frame,
                                    encoding="binary")
        collection = collection_m.write(mdi_model)

    elif os.path.isfile(model_path_mdc_2):

        bind_frame = 0
        mdi_model = mdc_facade.read(model_path_mdc_2, bind_frame,
                                    encoding="binary")
        collection = collection_m.write(mdi_model)

    else:

        raise Exception("Tag model '{}' not found".format(model_path))

    return collection

def _find_tag_object(tag_name, collection = None):

    if not collection:

        collection = bpy.context.view_layer.active_layer_collection.collection

    arrow_object = None
    for obj in collection.objects:

        if obj.type == 'EMPTY' and \
           obj.empty_display_type == 'ARROWS' and \
           obj.name == tag_name:
            arrow_object = obj
            break

    return arrow_object

def _attach_by_skin_file(game_path, skin_file_path):
    """Attach objects defined in skin file.
    """

    skin_data = skin_file_m.read(skin_file_path)

    # TODO check warnings

    collection = bpy.context.view_layer.active_layer_collection.collection

    for mapping in skin_data.tag_to_model_mappings:

        tag_name = mapping.tag_name
        tag_object = _find_tag_object(tag_name, collection)

        model_path = mapping.model_path
        new_collection = \
            _import_tag_model(game_path, skin_file_path, tag_name, model_path)

        _attach_by_collection(new_collection, tag_object)

def _attach_by_collection(collection = None, tag_object = None):
    """Attach all objects from active collection to tag by setting a
    child-of constraint.
    """

    if not collection:

        collection = bpy.context.view_layer.active_layer_collection.collection

    if not tag_object:

        tag_object = bpy.context.view_layer.objects.active

    if not is_tag_object(tag_object):

        exception_str = "Tag object not found. " \
                        " Must be of type='EMPTY', " \
                        " display_type='ARROWS', " \
                        " and name prefix 'tag_'."
        raise Exception(exception_str)

    attach_objects = []
    for collection_object in collection.all_objects:

        if _is_attach_object(collection_object):
            attach_objects.append(collection_object)
        else:
            reporter_m.warning("Selected object is not attachable.")

    if not attach_objects:
        raise Exception("No objects selected for attachment.")

    for attach_object in attach_objects:
        _add_child_of_constraint(attach_object, tag_object)

def _attach_by_objects():
    """Attach all selected objects to tag by setting a child-of constraint.
    """

    tag_object = bpy.context.view_layer.objects.active
    if not is_tag_object(tag_object):

        exception_str = "Tag object not found. " \
                        " Must be of type='EMPTY', " \
                        " display_type='ARROWS', " \
                        " and name prefix '_tag'."
        raise Exception(exception_str)

    attach_objects = []
    for selected_object in bpy.context.selected_objects:

        if _is_attach_object(selected_object):
            attach_objects.append(selected_object)
        else:
            reporter_m.warning("Selected object is not attachable.")

    if not attach_objects:
        raise Exception("No objects selected for attachment.")

    for attach_object in attach_objects:
        _add_child_of_constraint(attach_object, tag_object)

def attach_to_tag(method, game_path = None, skin_file_path = None):
    """Attach to tag operation.

    Args:

        method
    """

    if method == 'Objects':
        _attach_by_objects()
    elif method == 'Collection':
        _attach_by_collection()
    elif method == 'Skinfile':
        _attach_by_skin_file(game_path, skin_file_path)
    else:
        raise Exception("Attachment method not found.")

# =====================================
# READ
# =====================================

def read(arrow_object, armature_object = None):
    """Read arrow object and convert to mdi.

    Args:

        arrow_object
        armature_object

    Returns:

        mdi_tag
    """

    if not arrow_object.type == 'EMPTY' or \
        not arrow_object.empty_display_type == 'ARROWS':
        return None

    mdi_tag = None

    is_free_tag = False
    is_bone_tag = False
    is_bone_tag_off = False

    matrix_identity = mathutils.Matrix.Identity(4)

    for constraint in arrow_object.constraints:

        if constraint.type == 'CHILD_OF' and \
            constraint.target == armature_object:

            is_inherit_transforms = constraint.use_location_x and \
                                    constraint.use_location_y and \
                                    constraint.use_location_z and \
                                    constraint.use_rotation_x and \
                                    constraint.use_rotation_y and \
                                    constraint.use_rotation_z and \
                                    constraint.use_scale_x and \
                                    constraint.use_scale_y and \
                                    constraint.use_scale_z
            if not is_inherit_transforms:

                reporter_m.warning("Tried reading tag object '{}' but "
                                   "constraint does not inherit location, "
                                   "rotation or scale"
                                   .format(arrow_object.name))
                return None

            if arrow_object.matrix_basis == matrix_identity:
                is_bone_tag = True
            else:
                is_bone_tag_off = True

    if not (is_bone_tag or is_bone_tag_off):

        is_free_tag = True

    if is_free_tag:

        mdi_tag = mdi_m.MDIFreeTag()

        mdi_tag.name = arrow_object.name

        frame_start = bpy.context.scene.frame_start
        frame_end = bpy.context.scene.frame_end
        locations, rotations, _ = \
            blender_util_m.read_object_space_lrs(arrow_object,
                                                 frame_start,
                                                 frame_end,
                                                 read_scales=False)
        mdi_tag.locations = locations
        mdi_tag.orientations = rotations

    elif is_bone_tag:

        mdi_tag = mdi_m.MDIBoneTag()

        mdi_tag.name = arrow_object.name
        bone_name = arrow_object.constraints['Child Of'].subtarget
        mdi_tag.parent_bone = armature_object.data.bones.find(bone_name)
        if mdi_tag.parent_bone < 0:
            reporter_m.warning("Tried reading tag object '{}' but "
                                "did not find parent bone. Skipping."
                                .format(arrow_object.name))
            return None

        try:

            mdi_tag.torso_weight = arrow_object['Torso Weight']

        except:

            reporter_m.warning("'Torso Weight' value not specified on tag "
                                "object '{}'. Defaulting to '0.0'."
                                .format(arrow_object.name))
            mdi_tag.torso_weight = 0.0

    elif is_bone_tag_off:

        mdi_tag = mdi_m.MDIBoneTagOff()

        mdi_tag.name = arrow_object.name
        bone_name = arrow_object.constraints['Child Of'].subtarget
        mdi_tag.parent_bone = armature_object.data.bones.find(bone_name)
        if mdi_tag.parent_bone < 0:
            reporter_m.warning("Tried reading tag object '{}' but "
                                "did not find parent bone. Skipping."
                                .format(arrow_object.name))
            return None

        mdi_tag.location = arrow_object.location
        mdi_tag.orientation = arrow_object.rotation_quaternion.to_matrix()

    else:

        pass  # will be None

    return mdi_tag

# =====================================
# WRITE
# =====================================

def write(mdi_model, num_tag, collection, armature_object = None):
    """Convert and write mdi tag to collection.

    Args:

        mdi_model
        num_tag
        collection
        armature_object

    Returns:

        empty_object
    """

    mdi_tag = mdi_model.tags[num_tag]

    timer = timer_m.Timer()
    reporter_m.debug("Writing arrow: {} ...".format(mdi_tag.name))

    empty_object = None

    if isinstance(mdi_tag, mdi_m.MDIFreeTag):

        empty_object = bpy.data.objects.new("empty", None)
        collection.objects.link(empty_object)
        empty_object.name = mdi_tag.name
        empty_object.empty_display_type = 'ARROWS'
        empty_object.rotation_mode = 'QUATERNION'

        root_frame_location = mdi_tag.locations[mdi_model.root_frame]
        root_frame_orientation = mdi_tag.orientations[mdi_model.root_frame]

        matrix = mathutils.Matrix.Identity(4)
        matrix.translation = root_frame_location
        matrix = matrix @ root_frame_orientation.to_4x4()
        empty_object.matrix_world = matrix

        # animate
        if len(mdi_tag.locations) == 1:

            pass  # it is just 1 frame, no need to animate

        else:

            blender_util_m.write_object_space_lrs(empty_object,
                                                  mdi_tag.locations,
                                                  mdi_tag.orientations)

    elif isinstance(mdi_tag, mdi_m.MDIBoneTag):

        mdi_bones = mdi_model.skeleton.bones
        parent_bone_name = mdi_bones[mdi_tag.parent_bone].name

        empty_object = bpy.data.objects.new("empty", None)
        collection.objects.link(empty_object)
        empty_object.name = mdi_tag.name
        empty_object.empty_display_type = 'ARROWS'
        empty_object.rotation_mode = 'QUATERNION'

        empty_object.constraints.new(type="CHILD_OF")
        empty_object.constraints["Child Of"].target = armature_object
        empty_object.constraints["Child Of"].subtarget = parent_bone_name

        empty_object.constraints["Child Of"].use_location_x = True
        empty_object.constraints["Child Of"].use_location_y = True
        empty_object.constraints["Child Of"].use_location_z = True

        empty_object.constraints["Child Of"].use_rotation_x = True
        empty_object.constraints["Child Of"].use_rotation_y = True
        empty_object.constraints["Child Of"].use_rotation_z = True

        empty_object.constraints["Child Of"].use_scale_x = True
        empty_object.constraints["Child Of"].use_scale_y = True
        empty_object.constraints["Child Of"].use_scale_z = True

        empty_object['Torso Weight'] = mdi_tag.torso_weight

    elif isinstance(mdi_tag, mdi_m.MDIBoneTagOff):

        mdi_bones = mdi_model.skeleton.bones
        mdi_parent_bone = mdi_bones[mdi_tag.parent_bone]

        empty_object = bpy.data.objects.new("empty", None)
        collection.objects.link(empty_object)
        empty_object.name = mdi_tag.name
        empty_object.empty_display_type = 'ARROWS'
        empty_object.rotation_mode = 'QUATERNION'

        empty_object.constraints.new(type="CHILD_OF")
        empty_object.constraints["Child Of"].target = armature_object
        empty_object.constraints["Child Of"].subtarget = mdi_parent_bone.name

        empty_object.constraints["Child Of"].use_location_x = True
        empty_object.constraints["Child Of"].use_location_y = True
        empty_object.constraints["Child Of"].use_location_z = True

        empty_object.constraints["Child Of"].use_rotation_x = True
        empty_object.constraints["Child Of"].use_rotation_y = True
        empty_object.constraints["Child Of"].use_rotation_z = True

        empty_object.constraints["Child Of"].use_scale_x = True
        empty_object.constraints["Child Of"].use_scale_y = True
        empty_object.constraints["Child Of"].use_scale_z = True

        matrix = mathutils.Matrix.Identity(4)
        matrix.translation = mdi_tag.location
        orientation = mdi_tag.orientation
        empty_object.matrix_world = matrix @ orientation.to_4x4()

    else:

        reporter_m.warning("Could not write arrow object '{}'"
        .format(mdi_tag.name))
        return None

    time = timer.time()
    reporter_m.debug("Writing arrow DONE (time={})".format(time))

    return empty_object
