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

"""Blender utils.
"""

import math

import bpy
import mathutils

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.blender.core.fcurve as fcurve_m


def apply_object_transforms(mesh_object, mdi_model):

    # TODO parent objects, child of constraints?

    locations, rotations = fcurve_m.read_object(mesh_object)

    if not locations:

        locations = []
        rotations = []

        matrix_world = mesh_object.matrix_world

        loc, rot, _ = matrix_world.decompose()
        rot = rot.to_matrix()

        zero_vector = mathutils.Vector((0, 0, 0))
        matrix_identity = mathutils.Matrix.Identity(3)

        if not (loc == zero_vector and rot == matrix_identity):

            frame_start = bpy.context.scene.frame_start
            frame_end = bpy.context.scene.frame_end

            for _ in range(frame_start, frame_end + 1):

                locations.append(loc)
                rotations.append(rot)

    if locations and rotations:

        for mdi_surface in mdi_model.surfaces:

            for mdi_vertex in mdi_surface.vertices:

                if isinstance(mdi_vertex , mdi_m.MDIMorphVertex):

                    new_locations = []
                    new_normals = []

                    for num_frame in range(len(mdi_vertex.locations)):

                        loc = locations[num_frame]
                        rot = rotations[num_frame]

                        new_loc = loc + rot @ mdi_vertex.locations[num_frame]
                        new_locations.append(new_loc)
                        new_normal = rot @ mdi_vertex.normals[num_frame]
                        new_normals.append(new_normal)

                    mdi_vertex.locations = new_locations
                    mdi_vertex.normals = new_normals

                elif isinstance(mdi_vertex, mdi_m.MDIRiggedVertex):

                    mdi_vertex.normal = rot @ mdi_vertex.normal

                    # weight locations are given on bone space, so no
                    # transform needed

                else:

                    # TODO warning
                    pass

        if mdi_model.skeleton:

            for mdi_bone in mdi_model.skeleton.bones:

                new_bone_locations = []
                new_bone_oris = []

                for num_frame in range(len(mdi_bone.locations)):

                    loc = locations[num_frame]
                    rot = rotations[num_frame]

                    new_loc = loc + rot @ mdi_bone.locations[num_frame]
                    new_ori = rot @ mdi_bone.orientations[num_frame]

                    new_bone_locations.append(new_loc)
                    new_bone_oris.append(new_ori)

                mdi_bone.locations = new_bone_locations
                mdi_bone.orientations = new_bone_oris


# calculates a vector (x, y, z) orthogonal to v
def getOrthogonal(v):

    x = 0
    y = 0
    z = 0

    if v[0] == 0: # x-axis is 0 => yz-plane

        x = 1
        y = 0
        z = 0

    else:

        if v[1] == 0: # y-axis is 0 => xz-plane

            x = 0
            y = 1
            z = 0

        else:

            if v[2] == 0: # z-axis is 0 => xy-plane

                x = 0
                y = 0
                z = 1

            else:

                # x*v0 + y*v1 + z*v2 = 0
                x = 1 / v[0]
                y = 1 / v[1]
                z = -((1/v[2]) * 2)

    return (x, y, z)

def draw_normals_in_frame(mdi_vertices, num_frame, collection,
                          mdi_skeleton = None):

    for mdi_vertex in mdi_vertices:

        if isinstance(mdi_vertex, mdi_m.MDIMorphVertex):

            empty_object = bpy.data.objects.new("empty", None)
            empty_object.name = "vertex_normal"
            empty_object.empty_display_type = 'SINGLE_ARROW'
            empty_object.rotation_mode = 'QUATERNION'

            b3 = mdi_vertex.normals[num_frame]

            # find orthogonal basis vectors
            b2 = mathutils.Vector(getOrthogonal(b3))
            b1 = b2.cross(b3)

            # normalize
            b1.normalize()
            b2.normalize()
            b3.normalize()

            # build transformation matrix
            basis = mathutils.Matrix()
            basis[0].xyz = b1
            basis[1].xyz = b2
            basis[2].xyz = b3
            basis.transpose()
            basis.translation = mdi_vertex.locations[num_frame]

            empty_object.matrix_world = basis

            collection.objects.link(empty_object)

        elif isinstance(mdi_vertex, mdi_m.MDIRiggedVertex):

            empty_object = bpy.data.objects.new("empty", None)
            empty_object.name = "Normal"
            empty_object.empty_display_type = 'SINGLE_ARROW'
            empty_object.rotation_mode = 'QUATERNION'

            b3 = mdi_vertex.calc_normal_ms(mdi_skeleton, num_frame)

            # find orthogonal basis vectors
            b2 = mathutils.Vector(getOrthogonal(b3))
            b1 = b2.cross(b3)

            # normalize
            b1.normalize()
            b2.normalize()
            b3.normalize()

            # build transformation matrix
            basis = mathutils.Matrix()
            basis[0].xyz = b1
            basis[1].xyz = b2
            basis[2].xyz = b3
            basis.transpose()
            basis.translation = mdi_vertex.calc_location_ms(mdi_skeleton,
                                                            num_frame)

            empty_object.matrix_world = basis

            collection.objects.link(empty_object)

        else:

            pass  # TODO

def get_verts_from_bounds(min_bound, max_bound):

    vertices = []

    v0 = (min_bound[0], min_bound[1], min_bound[2])
    v1 = (min_bound[0], max_bound[1], min_bound[2])
    v2 = (min_bound[0], min_bound[1], max_bound[2])
    v3 = (min_bound[0], max_bound[1], max_bound[2])

    v4 = (max_bound[0], max_bound[1], max_bound[2])
    v5 = (max_bound[0], min_bound[1], max_bound[2])
    v6 = (max_bound[0], max_bound[1], min_bound[2])
    v7 = (max_bound[0], min_bound[1], min_bound[2])

    vertices.append(v0)
    vertices.append(v1)
    vertices.append(v2)
    vertices.append(v3)
    vertices.append(v4)
    vertices.append(v5)
    vertices.append(v6)
    vertices.append(v7)

    return vertices

def draw_bounding_volume(mdi_bounding_volume):

    min_bound = mdi_bounding_volume.aabbs[0].min_bound
    max_bound = mdi_bounding_volume.aabbs[0].max_bound

    vertices = get_verts_from_bounds(min_bound, max_bound)

    # faces
    faces = []

    f1 = (0, 1, 3, 2)
    f2 = (4, 5, 7, 6)

    f3 = (2, 3, 4, 5)
    f4 = (0, 1, 6, 7)

    f5 = (0, 2, 5, 7)
    f6 = (1, 3, 4, 6)

    faces.append(f1)
    faces.append(f2)
    faces.append(f3)
    faces.append(f4)
    faces.append(f5)
    faces.append(f6)

    name = "BoundingBox"
    mesh = bpy.data.meshes.new(name)
    mesh_object = bpy.data.objects.new(name, mesh)
    mesh_object.display_type = 'WIRE'

    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    mesh.validate(verbose=True)

    active_collection = \
        bpy.context.view_layer.active_layer_collection.collection
    active_collection.objects.link(mesh_object)

    num_frames = len(mdi_bounding_volume.aabbs)

    for num_frame in range(num_frames):

        shape_key = mesh_object.shape_key_add(name="Frame", from_mix=False)

        min_bound = mdi_bounding_volume.aabbs[num_frame].min_bound
        max_bound = mdi_bounding_volume.aabbs[num_frame].max_bound
        vertices = get_verts_from_bounds(min_bound, max_bound)

        for num_vertex, vertex in enumerate(vertices):

            x = vertex[0]
            y = vertex[1]
            z = vertex[2]
            shape_key.data[num_vertex].co = (x, y, z)

    mesh_object.data.shape_keys.use_relative = False

    for num_frame in range(num_frames):

        mesh_object.data.shape_keys.eval_time = 10.0 * num_frame
        mesh_object.data.shape_keys. \
            keyframe_insert('eval_time', frame = num_frame)

    mesh_object.data.update()
