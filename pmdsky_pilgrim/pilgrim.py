from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from tools.project_loader import load_project, get_rom_if_exists
from tools.hash_validation import verify_vanilla_eu, verify_vanilla_na


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
        "-c", "--check",
        action="store_true",
        default=False,
        help="Show a list of which converters Pilgrim will need to run for the provided ROMs."
    )

    if len(argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    if(args.check):
        print("check REAL")
    else:
        print("check NOT real")

    config = load_project(args.project_dir)
    # Validate ROMs:
    if "Roms" not in config:
        print("Roms not present in config!")
        exit(1)
    vanilla_eu = get_rom_if_exists(config, "Vanilla EU")
    vanilla_na = get_rom_if_exists(config, "Vanilla NA")
    mod_eu = get_rom_if_exists(config, "Mod EU")
    if not config["Roms"]["Ignore hashes"]:
        if not verify_vanilla_eu(config):
            print("Vanilla EU did not match expected hash. This ROM isn't vanilla.")
            exit(1)
        if not verify_vanilla_na(config):
            print("Vanilla NA did not match expected hash. This ROM isn't vanilla.")
            exit(1)
    # TODO: idfk everything??? make the list of what requires conversion