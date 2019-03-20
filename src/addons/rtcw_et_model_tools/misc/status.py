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


class Status:
    """Used for reporting back warnings and errors.

    Attributes:

        was_canceled (bool): indicates an error.
        cancel_msg (str): cancel message.
        warning_msgs (list): a list of strings for warnings.
    """

    class Canceled(Exception):
        pass

    def __init__(self):

        self.was_canceled = False
        self.cancel_msg = ""
        self.warning_msgs = []

    def set_canceled(self, cancel_msg):

        self.was_canceled = True
        self.cancel_msg = cancel_msg
        raise self.Canceled

    def add_warning_msg(self, warning_msg):

        self.warning_msgs.append(warning_msg)

    def prepare_report(self):

        cancel_report = ""
        if self.was_canceled:
            cancel_report = "Cancelled. Reason: {}.".format(self.cancel_msg)

        warning_report = ""
        for warning_msg in self.warning_msgs:
            warning_report = \
                "{}[{}] ".format(warning_report, warning_msg)

        return (cancel_report, warning_report)