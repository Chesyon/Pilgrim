import os
import sys

from ndspy.rom import NintendoDSRom
from pmdsky_pilgrim.tools.asm_patch import apply_patches
from pmdsky_pilgrim.tools.project_loader import get_config


def main(rom_path: str):
    rom = NintendoDSRom.fromFile(rom_path)
    apply_patches(rom, get_config())
    rom.saveToFile("modified.nds")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Please provide a ROM path.", file=sys.stderr)
        exit(1)
    if not os.path.exists(sys.argv[1]):
        print(f"ROM {sys.argv[1]} not found.", file=sys.stderr)
        exit(1)
    main(sys.argv[1])
