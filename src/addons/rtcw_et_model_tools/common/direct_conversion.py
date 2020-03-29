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

"Direct Conversion"

# =====================================
# MD3
# =====================================

def md3_to_md3(md3_source_path, md3_target_path):

    import rtcw_et_model_tools.md3.facade as md3_facade

    bind_frame = 0
    mdi_model = md3_facade.read(md3_source_path, bind_frame)
    md3_facade.write(mdi_model, md3_target_path)

def md3_to_mdc(md3_source_path, mdc_target_path):

    import rtcw_et_model_tools.md3.facade as md3_facade
    import rtcw_et_model_tools.mdc.facade as mdc_facade

    bind_frame = 0
    mdi_model = md3_facade.read(md3_source_path, bind_frame)
    mdc_facade.write(mdi_model, mdc_target_path)

def md3_to_mds(md3_source_path, mds_target_path):

    raise Exception("MD3 to MDS conversion not supported.")

def md3_to_mdmmdx(md3_source_path, mdm_target_path, mdx_target_path):

    raise Exception("MD3 to MDM/MDX conversion not supported.")

# =====================================
# MDC
# =====================================

def mdc_to_md3(mdc_source_path, md3_target_path):

    import rtcw_et_model_tools.mdc.facade as mdc_facade
    import rtcw_et_model_tools.md3.facade as md3_facade

    bind_frame = 0
    mdi_model = mdc_facade.read(mdc_source_path, bind_frame)
    md3_facade.write(mdi_model, md3_target_path)

def mdc_to_mdc(mdc_source_path, mdc_target_path):

    import rtcw_et_model_tools.mdc.facade as mdc_facade

    bind_frame = 0
    mdi_model = mdc_facade.read(mdc_source_path, bind_frame)
    mdc_facade.write(mdi_model, mdc_target_path)

def mdc_to_mds(mdc_source_path, mds_target_path):

    raise Exception("MDC to MDS conversion not supported.")

def mdc_to_mdmmdx(mdc_source_path, mdm_target_path, mdx_target_path):

    raise Exception("MDC to MDM/MDX conversion not supported.")

# =====================================
# MDS
# =====================================

def mds_to_md3(mds_source_path, md3_target_path):

    import rtcw_et_model_tools.mds.facade as mds_facade
    import rtcw_et_model_tools.md3.facade as md3_facade

    bind_frame = 0
    mdi_model = mds_facade.read(mds_source_path, bind_frame)
    md3_facade.write(mdi_model, md3_target_path)

def mds_to_mdc(mds_source_path, mdc_target_path):

    import rtcw_et_model_tools.mds.facade as mds_facade
    import rtcw_et_model_tools.mdc.facade as mdc_facade

    bind_frame = 0
    mdi_model = mds_facade.read(mds_source_path, bind_frame)
    mdc_facade.write(mdi_model, mdc_target_path)

def mds_to_mds(mds_source_path, mds_target_path, collapse_frame):

    import rtcw_et_model_tools.mds.facade as mds_facade

    bind_frame = 0
    mdi_model = mds_facade.read(mds_source_path, bind_frame)
    mds_facade.write(mdi_model, mds_target_path, collapse_frame)

def mds_to_mdmmdx(mds_source_path, mdm_target_path, mdx_target_path,
                  collapse_frame):

    import rtcw_et_model_tools.mds.facade as mds_facade
    import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade

    bind_frame = 0
    mdi_model = mds_facade.read(mds_source_path, bind_frame)
    mdmmdx_facade.write(mdi_model, mdm_target_path, mdx_target_path,
                        collapse_frame)

# =====================================
# MDM/MDX
# =====================================

def mdmmdx_to_md3(mdm_source_path, mdx_source_path, md3_target_path):

    import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade
    import rtcw_et_model_tools.md3.facade as md3_facade

    bind_frame = 0
    mdi_model = \
        mdmmdx_facade.read(mdm_source_path, mdx_source_path, bind_frame)
    md3_facade.write(mdi_model, md3_target_path)

def mdmmdx_to_mdc(mdm_source_path, mdx_source_path, mdc_target_path):

    import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade
    import rtcw_et_model_tools.mdc.facade as mdc_facade

    bind_frame = 0
    mdi_model = \
        mdmmdx_facade.read(mdm_source_path, mdx_source_path, bind_frame)
    mdc_facade.write(mdi_model, mdc_target_path)

def mdmmdx_to_mds(mdm_source_path, mdx_source_path, mds_target_path,
                  collapse_frame):

    import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade
    import rtcw_et_model_tools.mds.facade as mds_facade

    bind_frame = 0
    mdi_model = \
        mdmmdx_facade.read(mdm_source_path, mdx_source_path, bind_frame)
    mds_facade.write(mdi_model, mds_target_path, collapse_frame)

def mdmmdx_to_mdmmdx(mdm_source_path, mdx_source_path,
                     mdm_target_path, mdx_target_path,
                     collapse_frame):

    import rtcw_et_model_tools.mdmmdx.facade as mdmmdx_facade

    bind_frame = 0
    mdi_model = \
        mdmmdx_facade.read(mdm_source_path, mdx_source_path, bind_frame)
    mdmmdx_facade.write(mdi_model, mdm_target_path, mdx_target_path, collapse_frame)
