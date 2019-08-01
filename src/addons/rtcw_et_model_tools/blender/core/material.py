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

def apply_basic_shader_nodes(mesh_object,
                             possible_texture_paths,
                             material = None):

    # TODO clear all nodes option or if nodes in material present escape

    material_created = False
    if not material:
        material = bpy.data.materials.new(possible_texture_paths[0])
        material_created = True

    use_nodes_prev = material.use_nodes
    material.use_nodes = True

    node_tex_image = material.node_tree.nodes.new('ShaderNodeTexImage')
    node_bsdf_transparent = \
        material.node_tree.nodes.new('ShaderNodeBsdfTransparent')
    node_mix_shader = material.node_tree.nodes.new('ShaderNodeMixShader')
    node_bsdf_principled = material.node_tree.nodes.get('Principled BSDF')
    node_material_output = material.node_tree.nodes.get('Material Output')

    if not node_bsdf_principled:
        node_bsdf_principled = material.node_tree.nodes.new('Principled BSDF')

    if not node_material_output:
        node_material_output = material.node_tree.nodes.new('Material Output')

    node_tex_image.location = (-700, 300)
    node_bsdf_transparent.location = (-300, 400)
    node_mix_shader.location = (50, 300)
    node_bsdf_principled.location = (-300, 200)

    material.node_tree.links.new(node_bsdf_transparent.inputs.get("Color"), \
                                    node_tex_image.outputs.get("Color"))

    material.node_tree.links.new(node_mix_shader.inputs.get("Fac"), \
                                    node_tex_image.outputs.get("Alpha"))

    material.node_tree.links.new(node_bsdf_principled.inputs \
        .get("Base Color"), node_tex_image.outputs.get("Color"))

    material.node_tree.links.new(node_mix_shader.inputs.get("Shader"), \
                                    node_bsdf_transparent.outputs.get("BSDF"))

    material.node_tree.links.new(node_mix_shader.inputs[2], \
                                    node_bsdf_principled.outputs.get("BSDF"))

    material.node_tree.links.new(node_material_output.inputs.get("Surface"), \
                                    node_mix_shader.outputs.get("Shader"))

    node_bsdf_principled.inputs.get("Specular").default_value = 0
    node_bsdf_principled.inputs.get("Roughness").default_value = 0
    node_bsdf_principled.inputs.get("Sheen Tint").default_value = 0

    applied = False
    for possible_texture_path in possible_texture_paths:

        if os.path.isfile(possible_texture_path):

            node_tex_image.image = bpy.data.images.load(possible_texture_path)
            if mesh_object.data.materials:

                mesh_object.data.materials.append(material)

                # switch slots
                slot_material = mesh_object.data.materials[0]
                mesh_object.data.materials[0] = material
                mesh_object.data.materials[-1] = slot_material

            else:

                mesh_object.data.materials.append(material)

            applied = True
            break

    if not applied:

        material.use_nodes = use_nodes_prev

        reporter_m.warning("Could not apply shader nodes for material"
                            " name: '{}'".format(material.name))

        if material_created:

            bpy.data.materials.remove(material)

        return False

    return True

def _apply_shaders_by_skin_file(collection, game_path, skin_file_path):

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

            exts = ('tga', 'jpg')
            texture_paths = \
                common_util_m.create_exts(shader_reference, exts, True)

            texture_paths = \
                common_util_m.join_rel_paths_with_path(game_path,
                                                       texture_paths)

            apply_basic_shader_nodes(mesh_object,
                                     texture_paths,
                                     None)

        else:

            raise Exception("Mesh not found defined in .skin file '{}'"
                            .format(mesh_object.name))

def _apply_shaders_by_material_names(collection, game_path):

    mesh_objects = []
    for obj in collection.all_objects:
        if obj.type == 'MESH':
            mesh_objects.append(obj)

    if not mesh_objects:
        raise Exception("No mesh objects found")

    for mesh_object in mesh_objects:

        material = mesh_object.active_material
        if material:

            exts = ('tga', 'jpg')
            texture_paths = \
                common_util_m.create_exts(material.name, exts, True)

            texture_paths = \
                common_util_m.join_rel_paths_with_path(game_path,
                                                       texture_paths)

            apply_basic_shader_nodes(mesh_object,
                                     texture_paths,
                                     material)

        else:

            raise Exception("Material not found on mesh object '{}'"
                            .format(mesh_object.name))

def apply_shaders(method, game_path, skin_file_path):
    """Apply shaders.

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

        if not os.path.isfile(skin_file_path):
            raise Exception("Skinfile not found")

        _apply_shaders_by_skin_file(collection, game_path, skin_file_path)

    else:
        raise Exception("Shading method not found.")

# =====================================
# READ
# =====================================

def read(mesh_object):
    """TODO

    Args:

        TODO
    """

    mdi_shader_paths = mdi_m.MDIShaderPaths()

    for material in mesh_object.data.materials:

        if material:

            mdi_shader_path = mdi_m.MDIShaderPath(material.name)
            mdi_shader_paths.paths.append(mdi_shader_path)

    if not mdi_shader_paths.paths:

        mdi_shader_path = mdi_m.MDIShaderPath("unknown material")
        mdi_shader_paths.paths.append(mdi_shader_path)

    return mdi_shader_paths

# =====================================
# WRITE
# =====================================

def write_empty_material_by_name(mesh_object, material_name):
    """Creates a new empty material just by name. Will not create if exists."""

    material = None
    if material_name:

        for existing_material in bpy.data.materials:

            if existing_material.name == material_name:

                material = existing_material
                break

        if not material:

            material = bpy.data.materials.new(material_name)
            mesh_object.data.materials.append(material)

    return material

def write(mdi_shader, mesh_object):
    """TODO

    Args:

        TODO
    """

    material = None
    if isinstance(mdi_shader, mdi_m.MDIShaderPaths):

        for mdi_shader_path in mdi_shader.paths:

            material = \
                write_empty_material_by_name(mesh_object, mdi_shader_path.path)
            if material:
                # last one will be active
                mesh_object.active_material = material

    elif isinstance(mdi_shader, mdi_m.MDIShaderPath):

        material = \
            write_empty_material_by_name(mesh_object, mdi_shader.path)
        if material:
            mesh_object.active_material = material

    else:

        raise Exception("Unknown type for mdi shader")
