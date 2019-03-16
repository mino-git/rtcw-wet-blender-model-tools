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

import rtcw_et_model_tools.misc.status as status


class Status(status.Status):
    """Uses the status object to report errors and warnings to the Blender UI.
    """

    def __init__(self):

        super().__init__()

    def report(self, operator):

        cancel_report, warning_report = self.prepare_report()
        if cancel_report:
            operator.report({'ERROR'}, cancel_report)
        if warning_report:
            operator.report({'WARNING'}, warning_report)
