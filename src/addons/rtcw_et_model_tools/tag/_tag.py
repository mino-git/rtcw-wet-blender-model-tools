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

"""In-memory representation of the TAG file format. Provides file read and file
write functions to deal with the formats binary encoding.

Notes:

    The file format is stored as a byte stream to file. Data types are encoded
    in little-endian byte order. If not else specified, all coordinates are
    given in cartesian space. Convention is right-handed: x points forward,
    y points left, z points up.

Background:

    TODO
"""

import struct

import rtcw_et_model_tools.common.timer as timer_m
import rtcw_et_model_tools.common.reporter as reporter_m


class TAGData:
    """TODO.

    Attributes:

        name (bytes): name of tag, ASCII encoded, null-terminated, length 64.
        location (tuple): location coordinates in first frame as tuple of
            floats.
        orientation (tuple): orientation as rotation matrix in first frame
            as tuple of floats. Each sequence of 3 floats make up the
            coordinates of a basis vector. The first 3 floats make up the x
            basis vector, etc.

    File encodings:

        name: 64*ASCII (C-String).
        location: 3*F32, IEEE-754.
        orientation: 9*F32, IEEE-754.
    """

    format = '<64s12f'
    format_size = struct.calcsize(format)
    name_len = 64

    def __init__(self, name, location, orientation):

        self.name = name
        self.location = location
        self.orientation = orientation

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an TAGData object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            tag_data (TAGData): TAGData object.
        """

        file.seek(file_ofs)

        name, \
            location_x, location_y, location_z, \
            orientation_x1, orientation_x2, orientation_x3, \
            orientation_y1, orientation_y2, orientation_y3, \
            orientation_z1, orientation_z2, orientation_z3 \
            = struct.unpack(TAGData.format,
                            file.read(TAGData.format_size))

        location = (location_x, location_y, location_z)
        orientation = (orientation_x1, orientation_x2, orientation_x3,
                       orientation_y1, orientation_y2, orientation_y3,
                       orientation_z1, orientation_z2, orientation_z3)

        tag_data = TAGData(name, location, orientation)

        return tag_data

    def write(self, file, file_ofs):
        """Writes TAGData object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(TAGData.format,
                               self.name, self.location[0], self.location[1],
                               self.location[2], self.orientation[0],
                               self.orientation[1], self.orientation[2],
                               self.orientation[3], self.orientation[4],
                               self.orientation[5], self.orientation[6],
                               self.orientation[7], self.orientation[8]))


class TAGHeader:
    """General information about TAG data.

    Attributes:

        ident (bytes): magic number, ASCII encoded, length 4, reads "TAG1".
        version (int): version number, latest known is 1.
        num_tags (int): number of tags.
        ofs_end (int): file offset to end of file.

    File encodings:

        ident: 4*ASCII.
        version: UINT32.
        num_tags: UINT32.
        ofs_end: UINT32.

    Notes:

        Used mainly to navigate file data.
    """

    format = '<4s3I'
    format_size = struct.calcsize(format)
    ident = b'TAG3'
    version = 1
    name_len = 64

    def __init__(self, ident, version, num_tags, ofs_end):

        self.ident = ident
        self.version = version

        self.num_tags = num_tags
        self.ofs_end = ofs_end

    @staticmethod
    def read(file, file_ofs):
        """Reads file data into an TAGHeader object.

        Args:

            file (File): file object.
            file_ofs (int): file offset from which data will be read.

        Returns:

            tag_header (TAGHeader): TAGHeader object.
        """

        file.seek(file_ofs)

        ident, version, num_tags, ofs_end \
            = struct.unpack(TAGHeader.format,
                            file.read(TAGHeader.format_size))

        if ident != TAGHeader.ident:
            raise Exception("Failed reading TAG file. Reason: TAGHeader.ident."
                            " Make sure the file is indeed TAG.")

        tag_header = TAGHeader(ident, version, num_tags, ofs_end)

        return tag_header

    def write(self, file, file_ofs):
        """Writes TAGHeader object to file.

            Args:

                file (File): file object.
                file_ofs (int): file offset to which data is written.
        """

        file.seek(file_ofs)

        file.write(struct.pack(TAGHeader.format, self.ident, self.version,
                               self.num_tags, self.ofs_end))


class TAG:
    """Holds references to all TAG data.

    Attributes:

        header (TAGHeader): reference to TAGHeader object.
        tags (list): list of list objects, size=num_tags.
    """

    def __init__(self):

        self.header = None
        self.tags = []

    @staticmethod
    def read(file_path):
        """Reads a binary encoded TAG file into an TAG object.

        Args:

            file_path (str): path to TAG file.

        Returns:

            tag (TAG): TAG object.
        """

        with open(file_path, 'rb') as file:

            timer = timer_m.Timer()
            reporter_m.info("Reading TAG file: {} ...".format(file_path))

            tag = TAG()

            # tag.header
            file_ofs = 0
            tag.header = TAGHeader.read(file, file_ofs)

            # tag.tags
            file_ofs = TAGHeader.format_size
            for _ in range(tag.header.num_tags):

                tag_data = TAGData.read(file, file_ofs)
                tag.tags.append(tag_data)

                file_ofs = file_ofs + TAGData.format_size

            time = timer.time()
            reporter_m.info("Reading TAG file DONE (time={})".format(time))

            return tag

    def write(self, file_path):
        """Writes TAG object to file with binary encoding.

        Args:

            file_path (str): path to TAG file.
        """

        with open(file_path, 'wb') as file:

            timer = timer_m.Timer()
            reporter_m.info("Writing TAG file: {} ...".format(file_path))

            # tag.header
            file_ofs = 0
            self.header.write(file, file_ofs)

            # tag.tags
            file_ofs = TAGHeader.format_size

            for tag_data in self.tags:

                tag_data.write(file, file_ofs)

                file_ofs = file_ofs + TAGData.format_size

            time = timer.time()
            reporter_m.info("Writing TAG file DONE (time={})".format(time))
