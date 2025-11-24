from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from tools.project_loader import load_project, get_rom_if_exists
from tools.hash_validation import verify_vanilla_eu, verify_vanilla_na
from tools.asm_patch import get_applied_list, apply_patches

RED_TEXT = "\033[31;91m"
GREEN_TEXT = "\033[31;92m"
CLEAR_TEXT = "\033[0m"


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

    print("Loading project...")
    config = load_project(args.project_dir)
    # Validate ROMs:
    if "Roms" not in config:
        print(f"{RED_TEXT}Roms not present in config!{CLEAR_TEXT}")
        exit(1)
    if not config["Roms"]["Ignore hashes"]:
        print("Verifying ROMs...")
        if not verify_vanilla_eu(config):
            print(f"{RED_TEXT}Vanilla EU did not match expected hash. This ROM isn't vanilla.{CLEAR_TEXT}")
            exit(1)
        if not verify_vanilla_na(config):
            print(f"{RED_TEXT}Vanilla NA did not match expected hash. This ROM isn't vanilla.{CLEAR_TEXT}")
            exit(1)
        print(f"{GREEN_TEXT}ROMs OK!{CLEAR_TEXT}")
    vanilla_eu = get_rom_if_exists(config, "Vanilla EU")
    vanilla_na = get_rom_if_exists(config, "Vanilla NA")
    mod_eu = get_rom_if_exists(config, "Mod EU")

    print("Checking ASM patches...")
    applied_ready, issues = get_applied_list(mod_eu, config)
    if len(issues) > 0:
        print(f"{RED_TEXT}{len(issues)} issue(s) were encountered preparing to apply ASM patches.{CLEAR_TEXT}")
        for i in range(len(issues)):
            print(f"{RED_TEXT}Issue {i + 1}: {issues[i]}{CLEAR_TEXT}")
        exit(1)
    if len(applied_ready) > 0:
        print(f"{GREEN_TEXT}ASM patches OK!{CLEAR_TEXT}Applying ASM to NA...")
        apply_patches(vanilla_na, applied_ready, config)
        print("Applying ASM to vanilla EU... (this is only to improve difference detection!)")
        apply_patches(vanilla_eu, applied_ready, config)
    else:
        print("No ASM to apply!\033[0m")
    # TODO: idfk everything??? make the list of what requires conversion
