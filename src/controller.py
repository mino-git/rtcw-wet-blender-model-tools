
import os

from md3 import facade as md3_facade
from mdc import facade as mdc_facade
from mds import facade as mds_facade
from mdmmdx import facade as mdmmdx_facade

"""
file_path_in = os.path.abspath("../dev/import/head.md3")
file_path_out = os.path.abspath("../dev/export/head.md3")
mdi = md3_facade.read(file_path_in)
"""

"""
file_path_in = os.path.abspath("../dev/import/head.mdc")
file_path_out = os.path.abspath("../dev/export/head.mdc")
mdi = mdc_facade.read(file_path_in)
"""

"""
file_path_in = os.path.abspath("../dev/import/body.mds")
file_path_out = os.path.abspath("../dev/export/body.mds")
mdi = mds_facade.read(file_path_in)
"""

"""
file_path_mdm_in = os.path.abspath("../dev/import/body.mdm")
file_path_mdm_out = os.path.abspath("../dev/export/body.mdm")
file_path_mdx_in = os.path.abspath("../dev/import/body.mdx")
file_path_mdx_out = os.path.abspath("../dev/export/body.mdx")
mdi = mdmmdx_facade.read(file_path_mdm_in, file_path_mdx_in)
"""

if __name__ == '__main__':

    import tests.unittests.runner
    tests.unittests.runner.run()

print("SUCCESS")
