from sys import argv
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from tools.project_loader import load_project


def main() -> None:
    parser = ArgumentParser(
        prog="pmdsky-pilgrim",
        description="Tool to port EU ROMhacks of PMD:EoS to the NA release",
        usage="pmdsky-pilgrim [PROJECT_DIR]",
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

    if len(argv) == 1:
        parser.print_help()
        parser.exit()

    args = parser.parse_args()

    config = load_project(args.project_dir)
