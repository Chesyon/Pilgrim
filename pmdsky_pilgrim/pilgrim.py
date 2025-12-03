 #  Copyright 2025 Chesyon
 #
 #  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
 #  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
 #  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from tools.project_loader import load_project, get_rom_if_exists
from tools.hash_validation import verify_vanilla_eu, verify_vanilla_na
from tools.asm_patch import get_applied_list, apply_patches
from tools.bg_list import create_na_bg_list
from tools.special_process_converter import SPConverter
from tools.colors import RED_TEXT, GREEN_TEXT, YELLOW_TEXT, BLUE_TEXT, CLEAR_TEXT, BOLD_TEXT


def main() -> None:
    parser = ArgumentParser(
        prog="pmdsky-pilgrim",
        description="Tool to port EU ROMhacks of PMD:EoS to the NA release",
        usage="pmdsky-pilgrim [project_dir] [options]",
        formatter_class=RawDescriptionHelpFormatter,
        add_help=False,
    )

    # args
    parser.add_argument("-h", "--help", action="help", help="Show this help message and exit")
    parser.add_argument(
        "project_dir",
        type=str,
        help="""Required. Path to Pilgrim project directory. If the project does not exist, one will be created at the provided path.""",
    )
    parser.add_argument(
        "-c",
        "--check",
        action="store_true",
        default=False,
        help="Show a list of which converters Pilgrim will need to run for the provided ROMs.",
    )

    if len(argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    print(f"{BLUE_TEXT}Loading project...{CLEAR_TEXT}")
    config = load_project(args.project_dir)
    # Validate ROMs:
    if "Roms" not in config:
        print(f"{RED_TEXT}Roms not present in config!{CLEAR_TEXT}")
        exit(1)
    if not config["Roms"]["Ignore hashes"]:
        print(f"{YELLOW_TEXT}Verifying ROMs...{CLEAR_TEXT}")
        if not verify_vanilla_eu(config):
            print(f"{RED_TEXT}Vanilla EU did not match expected hash. This ROM isn't vanilla.{CLEAR_TEXT}")
            exit(1)
        if not verify_vanilla_na(config):
            print(f"{RED_TEXT}Vanilla NA did not match expected hash. This ROM isn't vanilla.{CLEAR_TEXT}")
            exit(1)
        print(f"{GREEN_TEXT}ROMs OK!{CLEAR_TEXT}")
    vanilla_eu = get_rom_if_exists(config, "Vanilla EU")
    na = get_rom_if_exists(config, "Vanilla NA")
    mod_eu = get_rom_if_exists(config, "Mod EU")

    print(f"{YELLOW_TEXT}Checking ASM patches...{CLEAR_TEXT}")
    applied_ready, issues = get_applied_list(mod_eu, config)
    if len(issues) > 0:
        print(f"{RED_TEXT}{len(issues)} issue(s) were encountered preparing to apply ASM patches.{CLEAR_TEXT}")
        for i in range(len(issues)):
            print(f"{RED_TEXT}Issue {i + 1}: {issues[i]}{CLEAR_TEXT}")
        exit(1)
    if len(applied_ready) > 0:
        print(f"{GREEN_TEXT}ASM patches OK!{CLEAR_TEXT}\n{BLUE_TEXT}{BOLD_TEXT}Applying ASM to NA...{CLEAR_TEXT}")
        apply_patches(na, applied_ready, config)
        print(f"{BLUE_TEXT}{BOLD_TEXT}Applying ASM to vanilla EU...{CLEAR_TEXT} (this is only to improve difference detection!)")
        apply_patches(vanilla_eu, applied_ready, config)
    else:
        print(f"No ASM to apply!{CLEAR_TEXT}")
    create_na_bg_list(vanilla_eu, mod_eu, na) # Port bg_list.dat if needed
    if "ExtractSPCode" in applied_ready:
        print(f"{BLUE_TEXT}{BOLD_TEXT}Converting custom SPs...{CLEAR_TEXT}")
        spc = SPConverter(mod_eu, config)
        spc.prepare_all()
        spc.create_map()
        spc.convert_all(na)
    # TODO: idfk everything??? make the list of what requires conversion
