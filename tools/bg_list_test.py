import os
import sys

from ndspy.rom import NintendoDSRom
from bg_list import create_na_bg_list

def main(vanilla_eu_name: str, vanilla_na_name: str, mod_eu_name: str):
    eu = NintendoDSRom.fromFile(vanilla_eu_name)
    na = NintendoDSRom.fromFile(vanilla_na_name)
    mod_eu = NintendoDSRom.fromFile(mod_eu_name)
    create_na_bg_list(eu, mod_eu, na)
    

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Please provide three ROMs: a vanilla EU ROM, a vanilla NA ROM, and a modified EU ROM.", file=sys.stderr)
        exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"Vanilla EU ROM {sys.argv[1]} not found.", file=sys.stderr)
        exit(1)
    if not os.path.exists(sys.argv[2]):
        print(f"Vanilla NA ROM {sys.argv[2]} not found.", file=sys.stderr)
        exit(1)
    if not os.path.exists(sys.argv[3]):
        print(f"Modified EU ROM {sys.argv[3]} not found.", file=sys.stderr)
        exit(1)
    main(sys.argv[1], sys.argv[2], sys.argv[3])
