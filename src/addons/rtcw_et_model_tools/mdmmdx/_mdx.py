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

"""In-memory representation of the MDX file format. Provides file read and file
write functions to deal with the formats binary encoding.

Notes:

    The file format is stored as a byte stream to file. Data types are encoded
    in little-endian byte order. If not else specified, all coordinates are
    given in cartesian space. Convention is right-handed: x points forward,
    y points left, z points up.

Background:

    MDX contains skeletal animation data. Bones make up the skeleton. Their
    location and orientation values are animated per frame.

    MDM data will reference the bone information defined in MDX to calculate
    its surface and tag data in a specific frame. As MDX files can be
    referenced by multiple MDM files, this supports reuse of animation data.
    This is different from MDS, which stores animation and surface data in the
    same file.
"""

import struct


class MDXBoneInfo:
    """Frame independent bone information.

    Attributes:

        name (bytes): bone name, ASCII encoded, null-terminated, length 64.
        parent_bone (int): parent bone as index into the list of bone_infos.
        torso_weight (float): TODO.
        parent_dist (float): distance to parent bone.
        flags (int): not used.

    File encodings:

        name: 64*ASCII (C-String).
        parent_bone: UINT32.
        torso_weight: F32, IEEE-754.
        parent_dist: F32, IEEE-754.
        flags: UINT32.

    Background:

        See "skeletal animation".
    """

    format = '<64sIffI'
    format_size = struct.calcsize(format)

    flags_default_value = 0
    name_len = 64

    def __init__(self, name, parent_bone, torso_weight, parent_dist, flags):

        self.name = name
        self.parent_bone = parent_bone
        self.torso_weight = torso_weight
        self.parent_dist = parent_dist
        self.flags = flags

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDXBoneInfo object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdx_bone_info (MDXBoneInfo): MDXBoneInfo object.
        """

        file.seek(file_ofs)

        name, parent_bone, torso_weight, parent_dist, flags \
            = struct.unpack(MDXBoneInfo.format,
                            file.read(MDXBoneInfo.format_size))

        mdx_bone_info = MDXBoneInfo(name, parent_bone, torso_weight,
                                    parent_dist, flags)

        return mdx_bone_info

    def write(self, file, file_ofs):
        """Writes MDXBoneInfo object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDXBoneInfo.format, self.name, self.parent_bone,
                               self.torso_weight, self.parent_dist,
                               self.flags))


class MDXBoneFrameCompressed:
    """Bone location and orientation in a specific frame.

    Attributes:

        orientation (tuple): orientation as euler angles in frame as tuple of
            shorts. Index 0 = pitch, index 1 = yaw, index 2 = roll. Index 3 is
            not used and contains a default value.
        location_dir (tuple): location in spherical coordinates as tuple of
            shorts. Index 0 = latitude, index 1 = longitude.

    File encodings:

        orientation: 4*INT16.
        location_dir: 2*INT16.

    Notes:

        Bone orientation values are given as compressed 16-Bit integers. To
        convert this range to a range of floats, the given value is linearly
        mapped. For this, a hard coded scale value is used. The result is
        an angle in the range of [0, 360). To convert the angles to a rotation
        matrix, we first roll, then pitch, then yaw (intrinsic).
        TODO recheck signed integer to angle range

        Bone location values are given as offset direction from a parent bone.
        Combined with the parent_dist value in the bone info field and the
        parent bones frame location, one can calculate the bones frame
        location. Linear mapping is done the same way as with the bone
        orientation values to get the angle values from the range of integer
        to the range of floats. To convert the angles to a direction vector,
        we first pitch (latitude), then yaw (longitude).
    """

    format = '<hhhhhh'
    format_size = struct.calcsize(format)

    orientation_scale = 360 / 65536.0  # TODO recheck with source
    location_dir_scale = 360 / 4095.0  # TODO recheck with source

    angle_none_default_value = 777

    def __init__(self, orientation, location_dir):

        self.orientation = orientation
        self.location_dir = location_dir

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDXBoneFrameCompressed object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdx_bone_frame_compressed (MDXBoneFrameCompressed):
                MDXBoneFrameCompressed object.
        """

        file.seek(file_ofs)

        pitch, yaw, roll, none, off_pitch, off_yaw \
            = struct.unpack(MDXBoneFrameCompressed.format,
                            file.read(MDXBoneFrameCompressed.format_size))

        orientation = (pitch, yaw, roll, none)
        location_dir = (off_pitch, off_yaw)

        mdx_bone_frame_compressed = MDXBoneFrameCompressed(orientation,
                                                           location_dir)

        return mdx_bone_frame_compressed

    def write(self, file, file_ofs):
        """Writes MDXBoneFrameCompressed object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDXBoneFrameCompressed.format,
                               self.orientation[0], self.orientation[1],
                               self.orientation[2], self.orientation[3],
                               self.location_dir[0], self.location_dir[1]))


class MDXFrameInfo:
    """General information about a frame.

    Attributes:

        min_bound (tuple): location coordinates of min corner of minimum
            bounding box as tuple of floats.
        max_bound (tuple): location coordinates of max corner of minimum
            bounding box as tuple of floats.
        local_origin (tuple): midpoint of bounds used for sphere culling
            TODO recheck with source
        radius (float): distance from local_origin to corner of bounding box
            TODO recheck with source
        root_bone_location (tuple): the root bone starts at this location.

    File encodings:

        min_bound: 3*F32, IEEE-754.
        max_bound: 3*F32, IEEE-754.
        local_origin: 3*F32, IEEE-754.
        radius: F32, IEEE-754.
        root_bone_location: 3*F32, IEEE-754.

    Notes:

        Describes mostly bounding box information. (TODO For frustum culling?)
    """

    format = '<3f3f3f1f3f'
    format_size = struct.calcsize(format)

    def __init__(self, min_bound, max_bound, local_origin, radius,
                 root_bone_location):

        self.min_bound = min_bound
        self.max_bound = max_bound
        self.local_origin = local_origin
        self.radius = radius
        self.root_bone_location = root_bone_location

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDXFrameInfo object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdx_frame_info (MDXFrameInfo): MDXFrameInfo object.
        """

        file.seek(file_ofs)

        min_bound_x, min_bound_y, min_bound_z, \
            max_bound_x, max_bound_y, max_bound_z, \
            local_origin_x, local_origin_y, local_origin_z, \
            radius, \
            root_bone_location_x, root_bone_location_y, root_bone_location_z \
            = struct.unpack(MDXFrameInfo.format,
                            file.read(MDXFrameInfo.format_size))

        mdx_frame_info \
            = MDXFrameInfo((min_bound_x, min_bound_y, min_bound_z),
                           (max_bound_x, max_bound_y, max_bound_z),
                           (local_origin_x, local_origin_y, local_origin_z),
                           radius,
                           (root_bone_location_x, root_bone_location_y,
                            root_bone_location_z))

        return mdx_frame_info

    def write(self, file, file_ofs):
        """Writes MDXFrameInfo object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDXFrameInfo.format,
                               self.min_bound[0], self.min_bound[1],
                               self.min_bound[2], self.max_bound[0],
                               self.max_bound[1], self.max_bound[2],
                               self.local_origin[0], self.local_origin[1],
                               self.local_origin[2], self.radius,
                               self.root_bone_location[0],
                               self.root_bone_location[1],
                               self.root_bone_location[2]))


class MDXFrame:
    """An animation frame. Holds references to general frame information, as
    well as each bones location and orientation values.

    Attributes:

        frame_info (MDXFrameInfo): reference to MDXFrameInfo object.
        bone_frames_compressed (list): list of MDXBoneFrameCompressed objects,
            size=num_bones.
    """

    def __init__(self):

        self.frame_info = None
        self.bone_frames_compressed = []

    @staticmethod
    def read(file, file_ofs, num_bones):
        """Reads file data into an MDXFrame object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.
            num_bones (int): number of bones.

        Returns:

            mdx_frame (MDXFrame): MDXFrame object.
        """

        mdx_frame = MDXFrame()

        # mdx_frame.header
        mdx_frame.frame_info = MDXFrameInfo.read(file, file_ofs)

        # mdx_frame.bone_frames_compressed
        file_ofs = file_ofs + MDXFrameInfo.format_size

        for i in range(0, num_bones):
            bone_frame_compressed = MDXBoneFrameCompressed.read(file, file_ofs)
            mdx_frame.bone_frames_compressed.append(bone_frame_compressed)

            file_ofs = file_ofs + MDXBoneFrameCompressed.format_size

        return mdx_frame

    def write(self, file, file_ofs):
        """Writes MDXFrame object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        # mdx_frame.frame_info
        self.frame_info.write(file, file_ofs)

        # mdx_frame.bone_frames_compressed
        file_ofs = file_ofs + MDXFrameInfo.format_size

        for bone_frame_compressed in self.bone_frames_compressed:
            file.seek(file_ofs)

            bone_frame_compressed.write(file, file_ofs)

            file_ofs = file_ofs + MDXBoneFrameCompressed.format_size


class MDXHeader:
    """General information about MDX data.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, reads "MDXW".
        version (int): version number, latest known is 4.
        name (bytes): model name, usually its pathname, ASCII encoded,
            null-terminated, length 64.
        num_frames (int): number of animation frames.
        num_bones (int): number of bones.
        ofs_frames (int): file offset to field of frames.
        ofs_bone_infos (int): file offset to field of bone infos.
        torso_parent_bone (int): TODO
        ofs_end (int): file offset to end of file.

    File encodings:

        ident: 4*ASCII.
        version: UINT32.
        name: 64*ASCII (C-String).
        num_frames: UINT32.
        num_bones: UINT32.
        ofs_frames: UINT32.
        ofs_bone_infos: UINT32.
        torso_parent_bone: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4sI64s6I'
    format_size = struct.calcsize(format)
    ident = b'MDXW'
    version = 2
    name_len = 64

    def __init__(self, ident, version, name, num_frames, num_bones, ofs_frames,
                 ofs_bone_infos, torso_parent_bone, ofs_end):

        self.ident = ident
        self.version = version
        self.name = name

        self.num_frames = num_frames
        self.num_bones = num_bones
        self.ofs_frames = ofs_frames
        self.ofs_bone_infos = ofs_bone_infos

        self.torso_parent_bone = torso_parent_bone

        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an MDXHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            mdx_header (MDXHeader): MDXHeader object.
        """

        file.seek(file_ofs)

        ident, version, name, num_frames, num_bones, ofs_frames, \
            ofs_bone_infos, torso_parent_bone, ofs_end \
            = struct.unpack(MDXHeader.format,
                            file.read(MDXHeader.format_size))

        mdx_file_header = MDXHeader(ident, version, name, num_frames,
                                    num_bones, ofs_frames, ofs_bone_infos,
                                    torso_parent_bone, ofs_end)

        return mdx_file_header

    def write(self, file, file_ofs):
        """Writes MDXHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(MDXHeader.format, self.ident, self.version,
                               self.name, self.num_frames, self.num_bones,
                               self.ofs_frames,
                               self.ofs_bone_infos, self.torso_parent_bone,
                               self.ofs_end))


class MDX:
    """Holds references to all MDX data.

    Attributes:

        header (MDXHeader): reference to MDXHeader object.
        frames (list): list of MDXFrame objects, size=num_frames.
        bone_infos (list): list of MDXBoneInfo objects, size=num_bones.
    """

    # TODO max_frames?
    min_torso_weight = 0.0
    max_torso_weight = 1.0

    def __init__(self):

        self.header = None
        self.frames = []
        self.bone_infos = []

    @staticmethod
    def read(file_path):
        """Reads a binary encoded MDX file into an MDX object.

        Args:

            file_path (str): path to MDX file.

        Returns:

            mdx (MDX): MDX object.
        """

        with open(file_path, 'rb') as file:

            mdx = MDX()

            # mdx.header
            file_ofs = 0
            mdx.header = MDXHeader.read(file, file_ofs)

            # mdx.frames
            file_ofs = mdx.header.ofs_frames
            for i in range(0, mdx.header.num_frames):

                mdx_frame = MDXFrame.read(file, file_ofs, mdx.header.num_bones)
                mdx.frames.append(mdx_frame)

                file_ofs = file_ofs + MDXFrameInfo.format_size + \
                    mdx.header.num_bones * MDXBoneFrameCompressed.format_size

            # mdx.bone_infos
            file_ofs = mdx.header.ofs_bone_infos
            for i in range(0, mdx.header.num_bones):

                mdx_bone_info = MDXBoneInfo.read(file, file_ofs)
                mdx.bone_infos.append(mdx_bone_info)

                file_ofs = file_ofs + MDXBoneInfo.format_size

            return mdx

    def write(self, file_path):

        """Writes MDX object to file with binary encoding.

        Args:

            file_path (str): path to MDX file.
        """

        with open(file_path, 'wb') as file:

            # mdx.header
            file_ofs = 0
            self.header.write(file, file_ofs)

            # mdx.frames
            file_ofs = self.header.ofs_frames
            for frame in self.frames:

                frame.write(file, file_ofs)

                file_ofs = file_ofs + MDXFrameInfo.format_size + \
                    self.header.num_bones * MDXBoneFrameCompressed.format_size

            # mdx.bone_infos
            file_ofs = self.header.ofs_bone_infos
            for mdx_bone_info in self.bone_infos:

                mdx_bone_info.write(file, file_ofs)

                file_ofs = file_ofs + MDXBoneInfo.format_size
