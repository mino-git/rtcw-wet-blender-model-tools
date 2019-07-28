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

"""Reading, writing and converting a collection from a blender scene.
Collections represent a model.
"""

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.blender.core.armature as armature_m
import rtcw_et_model_tools.blender.core.arrow as arrow_m
import rtcw_et_model_tools.blender.core.mesh as mesh_m
import rtcw_et_model_tools.blender.util as blender_util_m
import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


def _collect_objects_for_export(collection):

    mesh_objects = []
    armature_objects = []
    arrow_objects = []
    for obj in collection.all_objects:

        if obj.type == 'MESH':
            mesh_objects.append(obj)

        elif obj.type == 'ARMATURE':
            armature_objects.append(obj)

        elif obj.type == 'EMPTY' and \
             obj.empty_display_type == 'ARROWS' and \
             obj.name.startswith('tag_'):
            arrow_objects.append(obj)

    num_mesh_objects =  len(mesh_objects)
    num_armature_objects = len(armature_objects)
    num_arrow_objects = len(arrow_objects)
    num_objects = num_mesh_objects + num_armature_objects + num_arrow_objects
    reporter_m.info("Found {} objects for export."
                    " {} mesh objects,"
                    " {} armature objects,"
                    " {} arrow objects"
                    .format(num_objects,
                            num_mesh_objects,
                            num_armature_objects,
                            num_arrow_objects))

    armature_object = None
    if armature_objects:

        if len(armature_objects) > 1:

            reporter_m.warning("Found multiple skeletons, but only 1 "
                               "supported. Picking '{}'") \
                               .format(armature_object.name)

        armature_object = armature_objects[0]

    return (mesh_objects, armature_object, arrow_objects)

def read(collapse_frame = 0):
    """Reads a collection from active blender collection and converts to MDI.

    Args:

        collapse_frame (int): frame to use if the collapase map algorithm is
            applied.

    Returns:

        mdi_model (MDI): MDI object.
    """



    # frame_start = bpy.context.scene.frame_start
    # frame_end = bpy.context.scene.frame_end
    # if collapse_frame < frame_start or collapse_frame > frame_end:
    #     reporter_m.warning("Collapse frame not in range. Adjusting to frame "
    #                         "'{}'.".format(frame_start))
    #     collapse_frame = frame_start

    active_collection = \
        bpy.context.view_layer.active_layer_collection.collection

    timer = timer_m.Timer()
    reporter_m.info("Reading collection: {} ..."
        .format(active_collection.name))

    mdi_model = mdi_m.MDI()

    mdi_model.name = active_collection.name
    # mdi_model.root_frame = 0

    mesh_objects, armature_object, arrow_objects = \
        _collect_objects_for_export(active_collection)

    # mdi surfaces
    for mesh_object in mesh_objects:

        mdi_surface = mesh_m.read(mesh_object, armature_object)
        if mdi_surface:
            mdi_model.surfaces.append(mdi_surface)

    # mdi skeleton
    mdi_model.skeleton = armature_m.read(armature_object)

    # mdi tags
    for arrow_object in arrow_objects:

        mdi_tag = arrow_m.read(arrow_object, armature_object)
        if mdi_tag:
            mdi_model.tags.append(mdi_tag)

    # mdi bounds
    mdi_model.bounds = mdi_m.MDIBoundingVolume.calc(mdi_model)

    # mdi lod
    mdi_model.lod = mdi_m.MDIDiscreteLOD()  # TODO

    # apply object transforms
    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    blender_util_m.apply_object_transforms(mdi_model,
                                           mesh_objects,
                                           armature_object,
                                           arrow_objects,
                                           frame_start,
                                           frame_end)

    # consider parenting
    blender_util_m.apply_parent_transforms(mdi_model,
                                           mesh_objects,
                                           armature_object,
                                           arrow_objects)

    time = timer.time()
    reporter_m.info("Reading collection DONE (time={})".format(time))

    return mdi_model

def write(mdi_model):
    """Converts MDI model and writes it to a new collection in blender.

    Args:

        mdi_model (MDI): MDI model to convert and write.

    Returns:

        collection (Collection(ID)): blender collection.
    """

    # TODO return value

    timer = timer_m.Timer()
    reporter_m.info("Writing collection: {} ...".format(mdi_model.name))

    collection = bpy.data.collections.new(mdi_model.name)
    bpy.context.scene.collection.children.link(collection)

    armature_object = armature_m.write(mdi_model.skeleton,
                                       mdi_model.root_frame,
                                       collection)

    for num_surface in range(len(mdi_model.surfaces)):

        mesh_m.write(mdi_model, num_surface, collection, armature_object)

    for num_tag in range(len(mdi_model.tags)):

        arrow_m.write(mdi_model, num_tag, collection, armature_object)

    time = timer.time()
    reporter_m.info("Writing collection DONE (time={})".format(time))

    return collection
