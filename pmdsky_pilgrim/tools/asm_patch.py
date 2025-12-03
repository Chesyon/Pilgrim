 #  Copyright 2025 Chesyon
 #
 #  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
 #  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
 #  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

from ndspy.rom import NintendoDSRom
from skytemple_files.patch.patches import Patcher
from skytemple_files.common.util import get_ppmdu_config_for_rom
from skytemple_files.patch.errors import PatchNotConfiguredError
from os import listdir
from os.path import isfile, join
from .colors import BLUE_TEXT, RED_TEXT, CLEAR_TEXT

SKYPATCH_FOLDER = "skypatches"


def apply_patches(rom: NintendoDSRom, patches_to_apply: list[str], config):
    # Initialize
    ppmdu_config = get_ppmdu_config_for_rom(rom)
    patcher = Patcher(rom, ppmdu_config)
    patch_configs = config["Patches"]["Include"]
    load_all_custom_patches(patcher, config)
    for patch in patches_to_apply:
        print(f"{BLUE_TEXT}Applying {patch}...{CLEAR_TEXT}")
        patch_config = None
        if patch in patch_configs:
            patch_config = patch_configs[patch]
        try:
            patcher.apply(patch, patch_config)
        except PatchNotConfiguredError as e:
            print(
                f"{RED_TEXT}Config error encountered for parameter {e.config_parameter} while applying {patch}. Error info: {e}\nAborting :({CLEAR_TEXT}"
            )
            exit(1)


def verify_patch_parameters(patcher: Patcher, patch: str, config) -> list[str]:
    '''Ensures Pilgrim config provides any needed config for a given patch. Returns a list containing issues with a patch if any are present, otherwise returns ["OK!]"'''
    if patch not in patcher._config.asm_patches_constants.patches:
        return [
            f"Patch {patch} could not be found. Make sure you spelled it right, and provided the skypatch file if not bundled with SkyTemple."
        ]
    required_patch_params = patcher._config.asm_patches_constants.patches[patch].parameters
    issues = []
    if len(required_patch_params) != 0:
        # Config needed
        if patch not in config["Patches"]["Include"]:  # Patch has no info in config
            patch_missing_info = f"Patch {patch} has parameters but is missing from Pilgrim config! Please add it under Include with the following parameters:"
            for required_param in required_patch_params:
                patch_missing_info += f"\n{required_param} - Param info: {required_patch_params[required_param]}"
            issues = [patch_missing_info]
        else:
            provided_params = config["Patches"]["Include"][patch]
            for required_param in required_patch_params:
                if provided_params is None or required_param not in provided_params:
                    issues.append(
                        f"Patch {patch} is missing param {required_param}. Please add this to config. Param info: {required_patch_params[required_param]}"
                    )
    if len(issues) != 0:
        return issues
    return ["OK!"]


def sort_by_dependencies(patcher: Patcher, patches: list[str]) -> list[str]:
    """Sort a list of patches to put any dependants after their dependencies."""
    recursion_detect = 0
    for i in range(len(patches)):
        patch_name = patches[i]
        patch = patcher.get(patch_name)
        if hasattr(patch, "depends_on"):
            for patch_dependency in patch.depends_on():
                if patches.index(patch_dependency) > i:
                    # Dependency is later than the list than the dependant patch!!! bad!!!
                    recursion_detect += 1
                    if recursion_detect >= 100:
                        raise RecursionError(
                            "Infinite recursion detected while sorting patches by dependants. This likely means you have two patches that depend on each other, or Chesyon messed up."
                        )
                    patches.pop(i)
                    patches.append(patch_name)
                    i = 0
                    break
    return patches


def get_applied_list(rom: NintendoDSRom, config):
    """Creates a list of ASM patches that should be applied to the ROM, and verifies that any needed parameters are present in config. Returns a list of patches, and a list of any issues found with config."""
    ppmdu_config = get_ppmdu_config_for_rom(rom)
    patcher = Patcher(rom, ppmdu_config)
    load_all_custom_patches(patcher, config)
    applied_ready = []
    applied_not_ready = []
    issues = []
    exclude = config["Patches"]["Exclude"]
    for patch in patcher._loaded_patches:
        if exclude is None or patch not in exclude:  # Skip running checks for anything listed under Exclude
            try:
                patch_is_applied = patcher.is_applied(patch)
            except NotImplementedError:
                continue
            if patch_is_applied:
                verification = verify_patch_parameters(patcher, patch, config)
                if verification[0] == "OK!":
                    applied_ready.append(patch)
                else:
                    applied_not_ready.append(patch)
                    issues += verification
    # force add any patches that are listed in config but weren't automatically found by Pilgrim
    for patch in config["Patches"]["Include"]:
        if patch not in applied_ready and patch not in applied_not_ready:
            verification = verify_patch_parameters(patcher, patch, config)
            if verification[0] == "OK!":
                applied_ready.append(patch)
            else:
                applied_not_ready.append(patch)
                issues += verification
    applied_ready = sort_by_dependencies(patcher, applied_ready)
    return applied_ready, issues


def load_all_custom_patches(patcher: Patcher, config):
    """Add all skypatches in the projects skypatches folder to the patcher's patch list."""
    skypatch_folder_abs = join(config["Root"], SKYPATCH_FOLDER)
    for f in listdir(skypatch_folder_abs):
        path = join(skypatch_folder_abs, f)
        if isfile(path) and f.endswith(".skypatch"):
            print(f"Loading {f}...")
            patcher.add_pkg(path)
