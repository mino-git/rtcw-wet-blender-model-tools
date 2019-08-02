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

"""Reading, writing and converting mesh object to MDI. Mesh objects in this
code base are limited to vertices, triangles, materials and a uv map.
"""

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.blender.core.uv_map as uv_map_m
import rtcw_et_model_tools.blender.core.material as material_m
import rtcw_et_model_tools.blender.core.shape_key as shape_key_m
import rtcw_et_model_tools.blender.util as blender_util_m
import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m

# =====================================
# READ
# =====================================

def _read_static_vertices(mesh_object):
    """Reads a mesh object vertices assuming no animation and converts to a
    list of MDIMorphVertex. List is empty if no success.

    Args:

        mesh_object

    Returns:

        mdi_morph_vertices (list<MDIMorphVertex>): list of MDIMorphVertex
            objects.
    """

    mdi_morph_vertices = []

    mesh_vertices = [vertex.co for vertex in mesh_object.data.vertices]
    mesh_normals = [vertex.normal for vertex in mesh_object.data.vertices]

    frame_start = bpy.context.scene.frame_start
    frame_end = bpy.context.scene.frame_end

    for num_vertex in range(len(mesh_vertices)):

        location = mesh_vertices[num_vertex]
        normal = mesh_normals[num_vertex]

        locations = []
        normals = []

        for _ in range(frame_start, frame_end + 1):

            locations.append(location)
            normals.append(normal)

        mdi_morph_vertex = mdi_m.MDIMorphVertex(locations, normals)
        mdi_morph_vertices.append(mdi_morph_vertex)

    return mdi_morph_vertices

def _read_rigged_vertices(mesh_object, armature_object, root_frame):
    """Reads a mesh object vertices assuming it was rigged and converts to a
    list of MDIRiggedVertex.

    Args:

        mesh_object
        armature_object
        root_frame

    Returns:

        mdi_rigged_vertices (list<MDIRiggedVertex>): list of MDIRiggedVertex
            objects. List is empty or None if no success.
    """

    if not armature_object:
        return None

    armature_object_found = mesh_object.find_armature()
    if not armature_object_found:
        return None

    if not armature_object_found.name == armature_object.name:
        return None

    mdi_rigged_vertices = []

    bpy.context.view_layer.objects.active = \
        bpy.data.objects[armature_object.name]
    bpy.ops.object.mode_set(mode='EDIT')

    bind_pose_bones = \
        [edit_bone.matrix for edit_bone in armature_object.data.edit_bones]

    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.view_layer.objects.active = mesh_object

    bind_pose_vertices = [vertex.co for vertex in mesh_object.data.vertices]

    num_vertices = len(mesh_object.data.vertices)
    for vertex_index in range(0, num_vertices):

        mdi_rigged_vertex = mdi_m.MDIRiggedVertex()

        total_rotation = None  # for the normal

        # search vertex groups for the vertex
        # TODO vertex_groups could be used outside the context of bones?
        for vertex_group in mesh_object.vertex_groups:

            bone_name = vertex_group.name

            weight_value = None
            try:
                weight_value = \
                    mesh_object.vertex_groups[bone_name]. \
                    weight(vertex_index)
            except:
                pass

            if weight_value != None:

                bone_index = armature_object.data.bones.find(bone_name)

                # location
                loc, ori, _ = bind_pose_bones[bone_index].decompose()
                bone_bind_pose_location = loc
                bone_bind_pose_orientation = ori.to_matrix().to_3x3()

                location = bone_bind_pose_orientation.transposed() @ \
                            (bind_pose_vertices[vertex_index] - \
                            bone_bind_pose_location)

                mdi_weight = mdi_m.MDIVertexWeight(bone_index, weight_value,
                                                    location)
                mdi_rigged_vertex.weights.append(mdi_weight)

                # normal
                if total_rotation == None:

                    total_rotation = \
                        bone_bind_pose_orientation * \
                        weight_value

                else:

                    total_rotation = \
                        total_rotation + \
                        (bone_bind_pose_orientation * \
                        weight_value)

        normal = mesh_object.data.vertices[vertex_index].normal
        normal = total_rotation.transposed() @ normal

        mdi_rigged_vertex.normal = normal.normalized()

        mdi_rigged_vertices.append(mdi_rigged_vertex)

    # some final checks
    a_vertex_was_not_skinned = False
    vertex_skins_exist = False

    for mdi_rigged_vertex in mdi_rigged_vertices:

        if not mdi_rigged_vertex.weights:
            a_vertex_was_not_skinned = True
        else:
            vertex_skins_exist = True

    if vertex_skins_exist:
        if a_vertex_was_not_skinned:
            reporter_m.warning("A vertex was not skinned")
    else:
        reporter_m.warning("Found skeletal animation data but vertices not"
                           " skinned")
        return None

    return mdi_rigged_vertices

def _read_morph_vertices(mesh_object):
    """Reads a mesh objects vertices assuming it was shape keyed and converts
    to a list of MDIMorphVertex.

    Args:

        mesh_object

    Returns:

        mdi_morph_vertices (list<MDIMorphVertex>): list of MDIMorphVertex
            objects. List is empty if no success.
    """

    mdi_morph_vertices = []

    vertex_locations, vertex_normals = shape_key_m.read_shape_keys(mesh_object)
    if vertex_locations and vertex_normals:

        num_vertices = len(mesh_object.data.vertices)
        for num_vertex in range(num_vertices):

            locations = vertex_locations[num_vertex]
            normals = vertex_normals[num_vertex]
            mdi_morph_vertex = mdi_m.MDIMorphVertex(locations, normals)
            mdi_morph_vertices.append(mdi_morph_vertex)

    return mdi_morph_vertices

def read(mesh_object, armature_object = None, root_frame = 0):
    """Reads a mesh object and converts it to MDISurface.

    Args:

        mesh_object
        armature_object
        root_frame

    Returns:

        mdi_surface (MDISurface): MDISurface object.
    """

    mdi_surface = mdi_m.MDISurface()

    mdi_surface.name = mesh_object.name

    # vertices

    # do some checks first
    is_morph_mesh = False
    is_skeletal_mesh = False

    shape_key = mesh_object.data.shape_keys
    if shape_key and \
       shape_key.animation_data and \
       shape_key.animation_data.action:  # TODO nla
       is_morph_mesh = True

    armature_object_found = mesh_object.find_armature()
    if armature_object_found:
        is_skeletal_mesh = True

    if is_morph_mesh and is_skeletal_mesh:

        exception_string = "Found shape key animation as well as skeletal" \
                           " animation data for object '{}'. Both animation" \
                           " types are not supported. Make sure to use only" \
                           " one type of animation for the object." \
                           .format(mesh_object.name)
        raise Exception(exception_string)

    # read the vertices
    if is_morph_mesh:

        mdi_vertices = _read_morph_vertices(mesh_object)

    elif is_skeletal_mesh:

        mdi_vertices = _read_rigged_vertices(mesh_object,
                                             armature_object,
                                             root_frame)

    else:

        mdi_vertices = _read_static_vertices(mesh_object)

    if mdi_vertices:

        mdi_surface.vertices = mdi_vertices

    else:

        if is_morph_mesh:

            reporter_m.warning("Failed reading morph mesh data for object '{}'"
                               .format(mesh_object.name))

        elif is_skeletal_mesh:

            reporter_m.warning("Failed reading skeletal mesh data for object "
                               " '{}'".format(mesh_object.name))

        else:

            reporter_m.warning("Found mesh object '{}' with no vertex data"
                               .format(mesh_object.name))

        return None

    # triangles
    for triangle in mesh_object.data.polygons:

        indices = []
        for index in triangle.vertices:
            indices.append(index)

        mdi_triangle = mdi_m.MDITriangle(indices)
        mdi_surface.triangles.append(mdi_triangle)

    # shaders
    mdi_surface.shader = material_m.read(mesh_object)

    # uv map
    mdi_surface.uv_map = uv_map_m.read(mesh_object)

    return mdi_surface

# =====================================
# WRITE
# =====================================

def _write_rigged_vertices(mdi_rigged_vertices, mdi_skeleton, mesh_object,
                           armature_object):
    """Converts and writes a list of MDIRiggedVertex.

    Args:

        mdi_rigged_vertices
        mdi_skeleton
        mesh_object
        armature_object
    """

    timer = timer_m.Timer()
    reporter_m.debug("Rigging vertices ...")

    mdi_bones = mdi_skeleton.bones
    vertex_groups_dict = {mdi_bone.name: [] for mdi_bone in mdi_bones}

    for vertex_index, mdi_rigged_vertex in enumerate(mdi_rigged_vertices):

        for mdi_vertex_weight in mdi_rigged_vertex.weights:

            bone_name = mdi_bones[mdi_vertex_weight.parent_bone].name
            weights = (vertex_index, mdi_vertex_weight.weight_value)
            vertex_groups_dict[bone_name].append(weights)

    for bone_name, weights in vertex_groups_dict.items():

        vertex_group = mesh_object.vertex_groups.new(name = bone_name)

        for vertex_index, weight in weights:

            vertex_group.add([vertex_index], weight, 'REPLACE')

    modifier = mesh_object.modifiers.new('Armature', 'ARMATURE')
    modifier.object = armature_object
    modifier.use_bone_envelopes = False
    modifier.use_vertex_groups = True

    time = timer.time()
    reporter_m.debug("Rigging vertices DONE (time={})".format(time))

def _write_morph_vertices(mdi_morph_vertices, mesh_object, root_frame):
    """Converts and writes a list of MDIMorphVertex.

    Args:

        mdi_morph_vertices
        mesh_object
        root_frame
    """

    timer = timer_m.Timer()
    reporter_m.debug("Morphing vertices ...")

    sample_vertex = mdi_morph_vertices[0]
    if len(sample_vertex.locations) == 1:

        pass  # it is just 1 frame, no need to animate

    else:

        vertex_locations = []
        vertex_normals = []
        for mdi_morph_vertex in mdi_morph_vertices:

            vertex_locations.append(mdi_morph_vertex.locations)
            vertex_normals.append(mdi_morph_vertex.normals)

        shape_key_m.write_shape_keys(mesh_object,
                                     vertex_locations,
                                     vertex_normals)

    time = timer.time()
    reporter_m.debug("Morphing vertices DONE (time={})".format(time))

def _create_geometry(mdi_model, num_surface, collection):
    """Creates a new mesh object along with vertices and triangles.

    Args:

        mdi_model
        num_surface
        collection

    Returns:

        mesh_object
    """

    mdi_surface = mdi_model.surfaces[num_surface]

    name = mdi_surface.name
    mesh = bpy.data.meshes.new("{}{}".format(name, "_data"))
    mesh_object = bpy.data.objects.new(name, mesh)

    mdi_vertices = mdi_surface.vertices
    mdi_triangles = mdi_surface.triangles

    root_frame = mdi_model.root_frame
    vertex_locations = []
    for mdi_vertex in mdi_vertices:

        if isinstance(mdi_vertex, mdi_m.MDIRiggedVertex):

            location = \
                mdi_vertex.calc_location_ms(mdi_model.skeleton, root_frame)
            vertex_locations.append(location)

        elif isinstance(mdi_vertex, mdi_m.MDIMorphVertex):

            location = mdi_vertex.locations[root_frame]
            vertex_locations.append(location)

        else:

            reporter_m.exception("Unknown type in vertex list")
            raise TypeError

    triangles = [mdi_triangle.indices for mdi_triangle in mdi_triangles]

    if vertex_locations and triangles:

        mesh.from_pydata(vertex_locations, [], triangles)
        mesh.update()
        mesh.validate(verbose=True)

    else:

        reporter_m.warning("A surface was defined without geometry")
        return None

    collection.objects.link(mesh_object)

    return mesh_object

def write(mdi_model, num_surface, collection, armature_object = None):
    """Converts and writes an MDISurface object.

    Args:

        mdi_model
        num_surface
        collection
        armature_object

    Returns:

        mesh_object
    """

    mdi_surface = mdi_model.surfaces[num_surface]

    timer = timer_m.Timer()
    reporter_m.debug("Writing mesh: {} ...".format(mdi_surface.name))

    # geometry
    mesh_object = _create_geometry(mdi_model, num_surface, collection)
    if not mesh_object:
        return None

    # animation
    sample_vertex = None
    if mdi_surface.vertices:
        sample_vertex = mdi_surface.vertices[0]

    if sample_vertex:

        if isinstance(sample_vertex, mdi_m.MDIRiggedVertex):

            _write_rigged_vertices(mdi_surface.vertices, mdi_model.skeleton,
                                   mesh_object, armature_object)
            mesh_object.parent = armature_object

        elif isinstance(sample_vertex, mdi_m.MDIMorphVertex):

            _write_morph_vertices(mdi_surface.vertices, mesh_object,
                                  mdi_model.root_frame)

        else:

            reporter_m.exception("Unknown type in vertex list")
            raise TypeError

    else:

        reporter_m.warning("A surface was defined without geometry")
        return None

    # shaders
    material_m.write(mdi_surface.shader, mesh_object)

    # uv map
    uv_map_m.write(mdi_surface.uv_map, mesh_object)

    time = timer.time()
    reporter_m.debug("Writing mesh DONE (time={})".format(time))

    return mesh_object
