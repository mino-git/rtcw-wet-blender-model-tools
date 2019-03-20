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

"""Shading.
"""

import os

import bpy


# Core
# ==============================

def apply_simple_shader(mesh_object, shader_reference, data_path, status):

    material = bpy.data.materials.new(shader_reference)
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

    # TODO remove indexing
    material.node_tree.links.new(node_mix_shader.inputs[2], \
                                    node_bsdf_principled.outputs.get("BSDF"))

    material.node_tree.links.new(node_material_output.inputs.get("Surface"), \
                                    node_mix_shader.outputs.get("Shader"))

    node_bsdf_principled.inputs.get("Specular").default_value = 0
    node_bsdf_principled.inputs.get("Roughness").default_value = 0
    node_bsdf_principled.inputs.get("Sheen Tint").default_value = 0

    texture_path = os.path.join(data_path, shader_reference)
    texture_path_tga = "{}.{}".format(texture_path, "tga")
    texture_path_jpg = "{}.{}".format(texture_path, "jpg")

    if os.path.isfile(texture_path_tga):
        node_tex_image.image = bpy.data.images.load(texture_path_tga)
        if mesh_object.data.materials:

            mesh_object.data.materials.append(material)

            # switch slots
            slot_material = mesh_object.data.materials[0]
            mesh_object.data.materials[0] = material
            mesh_object.data.materials[-1] = slot_material

        else:

            mesh_object.data.materials.append(material)

    elif os.path.isfile(texture_path_jpg):
        node_tex_image.image = bpy.data.images.load(texture_path_jpg)
        if mesh_object.data.materials:

            mesh_object.data.materials.append(material)

            # switch slots
            slot_material = mesh_object.data.materials[0]
            mesh_object.data.materials[0] = material
            mesh_object.data.materials[-1] = slot_material

        else:

            mesh_object.data.materials.append(material)
    else:
        bpy.data.materials.remove(material)
        warning_msg = "Could not find texture for shader reference: {}" \
            .format(shader_reference)
        status.warning_msgs.append(warning_msg)

    return True

def apply_shaders_from_material_names(collection, data_path, status):

    mesh_objects = []
    for obj in collection.all_objects:
        if obj.type == 'MESH':
            mesh_objects.append(obj)

    if not mesh_objects:

        cancel_msg = "No mesh objects found in active collection"
        status.set_canceled(cancel_msg)

    for mesh_object in mesh_objects:

        material = mesh_object.active_material
        if material:

            shader_reference = material.name
            i = shader_reference.find(".")
            if i != -1:
                shader_reference = shader_reference[0:i]

            apply_simple_shader(mesh_object, shader_reference, data_path,
                                status)

def apply_shaders_from_skin(collection, skin_data, data_path, status):

    import rtcw_et_model_tools.blender.shading as shading

    bpy.context.view_layer.active_layer_collection = \
        bpy.context.view_layer.layer_collection.children[collection.name]

    mesh_objects = []
    for obj in collection.all_objects:
        if obj.type == 'MESH':
            mesh_objects.append(obj)

    for mesh_object in mesh_objects:

        shader_reference = None
        for surface_to_shader_mapping in skin_data.surface_to_shader_mappings:

            surface_name = surface_to_shader_mapping.surface_name
            if surface_name == mesh_object.name:

                shader_reference = surface_to_shader_mapping.shader_reference
                break

        if shader_reference:

            shading.apply_simple_shader(mesh_object, shader_reference,
                                        data_path, status)

        else:

            warning_msg = "Shader reference for mesh object '{}' not found" \
                .format(mesh_object.name)
            status.warning_msgs.append(warning_msg)


# UI
# ==============================

class ShadingPanel(bpy.types.Panel):
    """TODO.
    """

    bl_label = "Shading"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "RtCW/ET"

    def draw(self, context):

        layout = self.layout

        row = layout.row()
        row.prop(context.scene,
                "remt_data_path")

        row = layout.row()
        row.operator("remt.apply_shading",
                     text="Apply Shading",
                     icon="MATERIAL_DATA")


# Operators
# ==============================

class ShadingOperator(bpy.types.Operator):
    """TODO.
    """

    bl_idname = "remt.apply_shading"
    bl_label = "Apply Materials"
    bl_description = "Apply shading from material names"

    @staticmethod
    def _validate_input(data_path, status):
        """Validate input.
        """

        if not data_path:
            cancel_msg = "input failed: no data path"
            status.set_canceled(cancel_msg)

        if not isinstance(data_path, str):
            cancel_msg = "input failed: data path must be string"
            status.set_canceled(cancel_msg)

        data_path = bpy.path.abspath(data_path)
        if not os.path.isdir(data_path):
            cancel_msg = "input failed: data path not found on disk"
            status.set_canceled(cancel_msg)

    def execute(self, context):
        """TODO.
        """

        import rtcw_et_model_tools.blender.status as status
        status = status.Status()

        try:

            data_path = context.scene.remt_data_path
            ShadingOperator._validate_input(data_path, status)

            active_collection = \
                bpy.context.view_layer.active_layer_collection.collection
            apply_shaders_from_material_names(active_collection, data_path,
                                              status)

        except status.Canceled:
            pass

        status.report(self)
        return {'FINISHED'}


# Registration
# ==============================

classes = (
    ShadingPanel,
    ShadingOperator,
)

def register():

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():

    for cls in classes:
        bpy.utils.unregister_class(cls)
