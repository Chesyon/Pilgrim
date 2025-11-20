import os
import sys

from ndspy.rom import NintendoDSRom
from pmdsky_pilgrim.tools.compare import create_lists


def main(vanilla_eu_name: str, vanilla_na_name: str, mod_eu_name: str):
    # Setup
    eu = NintendoDSRom.fromFile(vanilla_eu_name)
    na = NintendoDSRom.fromFile(vanilla_na_name)
    mod_eu = NintendoDSRom.fromFile(mod_eu_name)
    archi_added, archi_modified_eu_na_identical, archi_modified_eu_na_different, archi_modified_na_missing = (
        create_lists(eu, mod_eu, na)
    )
    print("The following files were added for Archipelago: " + str(archi_added) + "\n")
    print(
        "The following files were modified for Archipelago, are present in NA, and vanilla EU/NA files match: "
        + str(archi_modified_eu_na_identical)
        + "\n"
    )
    print(
        "The following files were modified for Archipelago, are present in NA, but vanilla EU/NA files do NOT match: "
        + str(archi_modified_eu_na_different)
        + "\n"
    )
    print(
        "The following files were modified for Archipelago, but are missing in NA: "
        + str(archi_modified_na_missing)
        + "\n"
    )


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
