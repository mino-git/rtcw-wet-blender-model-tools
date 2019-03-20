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

"""Read .skin file information.
"""

import re


class SkinData:
    """In-memory representation of skin files. Reads skin file information.

    Background:

        Skin files are domain-specific script files used by the game engine to
        apply a shader or external models during model loading. They are
        usually comma-seperated key/value pairs (1 per line), but syntax is not
        consistent.
    """

    max_qpath_len = 64

    re_strip_comment = re.compile(r'.*//')
    re_player_scale = re.compile(r'\s*playerscale (\d+\.?\d+)')
    re_md3_mapping = re.compile(r'\s*(md3_\w*)\s*,\s*"*([\w/\.]+)"*')
    re_tag_nop = re.compile(r'\s*(tag_\w*)\s*,.*')
    re_shader_mapping = re.compile(r'\s*(\w+)\s*,\s*"*([\w/\.]+)"*')
    re_blank = re.compile(r'^\s*$')

    class SurfaceToShaderMapping:

        def __init__(self, surface_name=None, shader_reference=None):

            self.surface_name = surface_name
            self.shader_reference = shader_reference

    class TagToModelMapping:

        keyword_mappings = [
            ("md3_beltr", "tag_bright"),
            ("md3_beltl", "tag_bleft"),
            ("md3_belt", "tag_ubelt"),
            ("md3_back", "tag_back"),
            ("md3_weapon", "tag_weapon"),
            ("md3_weapon2", "tag_weapon2"),
            ("md3_hat", "tag_mouth"),
            ("md3_rank", "tag_mouth"),
            ("md3_hat2", "tag_mouth"),
            ("md3_hat3", "tag_mouth"),
        ]

        def __init__(self, tag_name=None, model_path=None):

            self.tag_name = tag_name
            self.model_path = model_path

    def __init__(self, file_path):

        self.file_path = file_path
        self.player_scale = None
        self.surface_to_shader_mappings = []
        self.tag_to_model_mappings = []

        self.tag_nops = []
        self.unknown_lines = []

    @staticmethod
    def read(file_path, status):

        skin_data = None

        with open(file_path, encoding="ascii") as skin_file:

            skin_data = SkinData(file_path)

            lines = skin_file.readlines()

            for num_line, line in enumerate(lines, start=1):

                # strip comments
                result = SkinData.re_strip_comment.search(line)
                if result:
                    line = line[result.start(): result.end()]

                # we use the first match of a line and then skip the rest
                match = False

                # playerscale
                result = SkinData.re_player_scale.search(line)
                if result:

                    match = True
                    player_scale = result.group(1)

                    if not skin_data.player_scale:

                        try:
                            skin_data.player_scale = float(player_scale)
                        except ValueError:
                            warning_msg = "Could not convert player scale" \
                                " value"
                            status.warning_msgs.append(warning_msg)

                    else:

                        warning_msg = "Multiple playerscale values found in" \
                            " file"
                        status.warning_msgs.append(warning_msg)

                # md3_
                if not match:

                    result = SkinData.re_md3_mapping.search(line)
                    if result:

                        match = True
                        md3_name = result.group(1)
                        model_path = result.group(2)

                        if len(model_path) >= SkinData.max_qpath_len:

                            model_path = None
                            warning_msg = "Model path too long"
                            status.warning_msgs.append(warning_msg)

                        # parse md3_name
                        tag_name = None
                        for keyword_mapping in \
                            SkinData.TagToModelMapping.keyword_mappings:

                            md3_name_key = keyword_mapping[0]
                            if md3_name_key == md3_name:
                                tag_name = keyword_mapping[1]
                                break

                        if not tag_name:

                            warning_msg = "Could not find tag name for '{}'" \
                                " keyword".format(md3_name)
                            status.warning_msgs.append(warning_msg)

                        # parse model_path
                        if model_path:  # strip file extension
                            if model_path.endswith(".md3") or \
                               model_path.endswith(".mdc"):
                                model_path = model_path[0:-4]

                        if tag_name and model_path:

                            tag_to_model_mapping = \
                                SkinData.TagToModelMapping(tag_name, model_path)
                            skin_data.tag_to_model_mappings \
                                .append(tag_to_model_mapping)

                # shaders
                if not match:

                    result = SkinData.re_shader_mapping.search(line)
                    if result:

                        match = True
                        surface_name = result.group(1)
                        shader_name = result.group(2)

                        if len(surface_name) >= SkinData.max_qpath_len or \
                           len(shader_name) >= SkinData.max_qpath_len:

                            surface_name = None
                            shader_name = None
                            warning_msg = "Surface name or shader name too" \
                                " long"
                            status.warning_msgs.append(warning_msg)

                        # parse shader
                        if shader_name:

                            if shader_name.endswith(".tga") or \
                               shader_name.endswith(".jpg"):
                                shader_name = shader_name[0:-4]

                        if surface_name and shader_name:

                            surface_to_shader_mapping = \
                                SkinData.SurfaceToShaderMapping(surface_name,
                                                                shader_name)
                            skin_data.surface_to_shader_mappings \
                                .append(surface_to_shader_mapping)

                # tag_
                if not match:

                    result = SkinData.re_tag_nop.search(line)
                    if result:

                        match = True
                        tag_name = result.group(1)
                        skin_data.tag_nops.append(tag_name)

                # skip blank lines
                if not match:

                    result = SkinData.re_blank.search(line)
                    if result:

                        match = True

                if not match:

                    skin_data.unknown_lines.append(num_line)
                    warning_msg = "Unknown line ({})".format(num_line)
                    status.warning_msgs.append(warning_msg)

        return skin_data
