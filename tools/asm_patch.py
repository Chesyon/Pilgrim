from ndspy.rom import NintendoDSRom
from skytemple_files.patch.patches import Patcher
from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_files.common.ppmdu_config.data import Pmd2PatchParameterType
from skytemple_files.patch.errors import PatchNotConfiguredError
from os import listdir
from os.path import isfile, join
import sys
import yaml
SKYPATCH_FOLDER = "skypatches"

def do_thing(rom: NintendoDSRom):
    # Initialize
    ppmdu_config = get_ppmdu_config_for_rom(rom)
    patcher = Patcher(rom, ppmdu_config)
    with open('asm_patch_list.yml') as config_file:
        pilgrim_config = yaml.safe_load(config_file)
    pilgrim_patches = pilgrim_config['Patches']
    patches_to_apply = list(pilgrim_patches.keys())
    print(patches_to_apply)
    # Load skypatches from folder
    for f in listdir(SKYPATCH_FOLDER):
        path = join(SKYPATCH_FOLDER, f)
        if isfile(path) and f.endswith(".skypatch"):
            print(f"Loading {f}...")
            patcher.add_pkg(path)
    for patch in patches_to_apply:
        print(f"Applying {patch}...")
        patch_config = pilgrim_patches[patch]
        try:
            patcher.apply(patch, patch_config)
        except PatchNotConfiguredError as e:
            print(f"Config error encountered for parameter {e.config_parameter} while applying {patch}. Aborting :(")
            exit(1)
