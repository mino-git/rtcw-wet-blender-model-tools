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

"""Reading, writing and converting a material. A material name is used to store
a reference to an in-game shader.
"""

import os

import bpy

import rtcw_et_model_tools.mdi.mdi as mdi_m
import rtcw_et_model_tools.common.skin_file as skin_file_m
import rtcw_et_model_tools.common.util as common_util_m
import rtcw_et_model_tools.common.reporter as reporter_m


# =====================================
# SHADING OPERATION
# =====================================

def _set_material_active_all(mesh_object, material):

    material_index = _get_index_for_material(mesh_object, material)
    if material_index == -1:

        mesh_object.data.materials.append(material)
        material_index = \
            _get_index_for_material(mesh_object, material)

    mesh_object.active_material_index = material_index

    for polygon in mesh_object.data.polygons:
        polygon.material_index = material_index

def _get_index_for_material(mesh_object, material):

    material_index = -1
    for index, material_tmp in enumerate(mesh_object.data.materials):

        if material == material_tmp:
            material_index = index

    return material_index

def _get_material_by_name(material_name):

    material = None
    for material_tmp in bpy.data.materials:

        if material_tmp.name == material_name:
            material = material_tmp
            break

    return material

def _apply_nodes_to_material(material, possible_texture_paths):

    material.use_nodes = True

    nodes = material.node_tree.nodes
    nodes.clear()

    # create
    node_tex_image = nodes.new('ShaderNodeTexImage')
    node_diffuse_bsdf = nodes.new('ShaderNodeBsdfDiffuse')
    node_material_output = nodes.new('ShaderNodeOutputMaterial')

    # links
    material.node_tree.links.new(
        node_diffuse_bsdf.inputs.get("Color"),
        node_tex_image.outputs.get("Color")
        )

    material.node_tree.links.new(
        node_material_output.inputs.get("Surface"),
        node_diffuse_bsdf.outputs.get("BSDF")
        )

    # locations
    node_tex_image.location = (-300, 300)
    node_diffuse_bsdf.location = (0, 300)
    node_material_output.location = (300, 300)

    # load texture
    texture_found = False
    for possible_texture_path in possible_texture_paths:

        if os.path.isfile(possible_texture_path):

            node_tex_image.image = bpy.data.images.load(possible_texture_path)
            texture_found = True
            break

    # if not texture_found:
    #     nodes.clear()

    return texture_found

def _apply_shaders_by_skin_file(collection, game_path, skin_file_path):

    if not os.path.isfile(skin_file_path):
        raise Exception("Skinfile not found")

    mesh_objects = []
    for obj in collection.all_objects:
        if obj.type == 'MESH':
            mesh_objects.append(obj)

    if not mesh_objects:
        raise Exception("No mesh objects found")

    skin_data = skin_file_m.read(skin_file_path)

    for mesh_object in mesh_objects:

        shader_reference = None
        for mapping in skin_data.surface_to_shader_mappings:

            surface_name = mapping.surface_name
            if surface_name == mesh_object.name:

                shader_reference = mapping.shader_reference
                break

        if shader_reference:

            material = _get_material_by_name(shader_reference)
            if material:

                _set_material_active_all(mesh_object, material)

            else:

                material = bpy.data.materials.new(shader_reference)

                possible_texture_paths = \
                    common_util_m.prepare_texture_paths(game_path,
                                                        shader_reference,
                                                        True)
                success = \
                    _apply_nodes_to_material(material, possible_texture_paths)

                if not success:

                    reporter_m.warning("Could not apply shader nodes for"
                                        " material: '{}'"
                                        .format(material.name))
                    bpy.data.materials.remove(material)

                else:

                    _set_material_active_all(mesh_object, material)

        else:

            reporter_m.warning("Could not find mesh object '{}' defined in"
                               " .skin file "
                               .format(mesh_object.name))

def _apply_shaders_by_material_names(collection, game_path):

    mesh_objects = []
    for obj in collection.all_objects:
        if obj.type == 'MESH':
            mesh_objects.append(obj)

    if not mesh_objects:
        raise Exception("No mesh objects found")

    for mesh_object in mesh_objects:

        material = None
        material_index = mesh_object.active_material_index
        if material_index >= 0:

            try:
                material = mesh_object.data.materials[material_index]
            except:
                pass

        if material:

            possible_texture_paths = \
                common_util_m.prepare_texture_paths(game_path,
                                                    material.name,
                                                    True)
            success = \
                _apply_nodes_to_material(material, possible_texture_paths)

            if not success:

                reporter_m.warning("Could not apply shader nodes for"
                                    " material: '{}'"
                                    .format(material.name))

            else:

                _set_material_active_all(mesh_object, material)

def apply_shaders(method, game_path, skin_file_path):
    """Apply shaders operation.

    Args:

        method
        game_path
        skin_file_path
    """

    collection = bpy.context.view_layer.active_layer_collection.collection

    if not os.path.isdir(game_path):
        raise Exception("Game path directory not found")

    if method == 'Material Names':

        _apply_shaders_by_material_names(collection, game_path)

    elif method == 'Skinfile':

        _apply_shaders_by_skin_file(collection, game_path, skin_file_path)

    else:
        raise Exception("Shading method not found.")

# =====================================
# READ
# =====================================

def read(mesh_object):
    """Reads material from mesh object and converts to mdi shader.

    Args:

        mesh_object

    Returns:

        mdi_shader_paths
    """

    mdi_shader_paths = mdi_m.MDIShaderPaths()

    for material in mesh_object.data.materials:

        if material:

            mdi_shader_path = mdi_m.MDIShaderPath(material.name)
            mdi_shader_paths.paths.append(mdi_shader_path)

    if not mdi_shader_paths.paths:

        mdi_shader_path = mdi_m.MDIShaderPath("\0")
        mdi_shader_paths.paths.append(mdi_shader_path)

    return mdi_shader_paths

# =====================================
# WRITE
# =====================================

def write_empty_material_by_name(mesh_object, material_name):
    """Creates a new empty material just by name. Will not create if exists.

    Args:

        mesh_object
        material_name
    """

    material = None
    if material_name:

        material = _get_material_by_name(material_name)

        if not material:

            material = bpy.data.materials.new(material_name)
            mesh_object.data.materials.append(material)

    return material

def write(mdi_shader, mesh_object):
    """Write mdi shader to mesh object.

    Args:

        mdi_shader
        mesh_object
    """

    material = None
    if isinstance(mdi_shader, mdi_m.MDIShaderPaths):

        for mdi_shader_path in mdi_shader.paths:

            material = \
                write_empty_material_by_name(mesh_object, mdi_shader_path.path)

        if material:
            _set_material_active_all(mesh_object, material)

    elif isinstance(mdi_shader, mdi_m.MDIShaderPath):

        material = \
            write_empty_material_by_name(mesh_object, mdi_shader.path)
        if material:
            _set_material_active_all(mesh_object, material)

    else:

        raise Exception("Unknown type for mdi shader")
