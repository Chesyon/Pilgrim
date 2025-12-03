 #  Copyright 2025 Chesyon
 #
 #  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
 #  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
 #  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

import sys
import os

from ndspy.rom import NintendoDSRom

from pmdsky_pilgrim.tools.special_process_converter import SPConverter
from pmdsky_pilgrim.tools.project_loader import get_config


def main(mod_eu_path: str, vanilla_na_path: str):
    mod_eu = NintendoDSRom.fromFile(mod_eu_path)
    vanilla_na = NintendoDSRom.fromFile(vanilla_na_path)
    spc = SPConverter(mod_eu, get_config())
    spc.prepare_all()
    # spc.log_convertible_offsets()
    spc.create_map()
    spc.convert_all(vanilla_na)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Please provide a modified EU ROM and a vanilla NA ROM.", file=sys.stderr)
        exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"Modified EU ROM {sys.argv[1]} not found.", file=sys.stderr)
        exit(1)
    if not os.path.exists(sys.argv[2]):
        print(f"Vanilla NA ROM {sys.argv[2]} not found.", file=sys.stderr)
        exit(1)
    main(sys.argv[1], sys.argv[2])
