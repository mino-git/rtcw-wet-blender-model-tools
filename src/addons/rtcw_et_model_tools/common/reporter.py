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

"Logging combined with storing a list of warnings."

import sys
import logging
from logging.handlers import RotatingFileHandler

remt_logger = None
remt_warnings = []

def init(log_filepath = None):

    logger = logging.getLogger('remt_logger')
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    logger.setLevel(logging.DEBUG)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)15s %(levelname)-6s %(message)s')
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_filepath != None:

        p_filename = log_filepath
        p_mode='a'
        p_max_bytes=3 * 1024 * 1024
        p_backup_count=1
        # p_encoding=None
        # p_delay=0

        rotating_file_handler = \
            logging.handlers.RotatingFileHandler(filename=p_filename,
                                                 mode=p_mode,
                                                 maxBytes=p_max_bytes,
                                                 backupCount=p_backup_count)
        rotating_file_handler.setFormatter(formatter)
        logger.addHandler(rotating_file_handler)

    global remt_logger
    remt_logger = logger

def deinit():

    logger = logging.getLogger('remt_logger')
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    global remt_logger
    remt_logger = None

def get_warnings(num_max_chars = 0):

    if num_max_chars > 0:

        pass  # TODO

    return remt_warnings

def reset_state():

    if not remt_logger:
        init()

    global remt_warnings
    remt_warnings = []

def debug(msg):

    remt_logger.debug(msg)

def info(msg):

    remt_logger.info(msg)

def warning(msg):

    remt_logger.warning(msg)
    remt_warnings.append(msg)

def exception(error):

    remt_logger.exception(error)


# def prepare_report(self):

#     cancel_report = ""
#     if self.was_canceled:
#         cancel_report = "Cancelled. Reason: {}.".format(self.cancel_msg)

#     warning_report = ""
#     for warning_msg in self.warning_msgs:
#         warning_report = \
#             "{}[{}] ".format(warning_report, warning_msg)

#     return (cancel_report, warning_report)
