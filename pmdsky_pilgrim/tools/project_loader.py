#  Copyright 2025 Chesyon
#
#  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
#  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
#  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

from yaml import safe_load
from os import path, listdir
from pathlib import Path
from shutil import copytree
from ndspy.rom import NintendoDSRom


def load_project(project_dir: str) -> dict:
    """Given a path to a Pilgrim project, returns the config. If the directory does not exist or is empty, it will instead create a project in the directory."""
    pilgrim_root = str(Path(project_dir).resolve())
    # Validate project
    if not path.exists(pilgrim_root):
        print("No project found at the given directory! Creating one...")
        init_project_directory(pilgrim_root)
    elif path.isfile(pilgrim_root):
        print("Provided path is a file, not a directory. Remove this file or use a different path.")
        exit(1)
    # Check if dir is empty
    elif len(listdir(pilgrim_root)) <= 0:
        print("Given directory is empty! Creating a project inside...")
        init_project_directory(pilgrim_root)
    # Ensure config.yml exists and is a file
    config_path = path.join(pilgrim_root, "config.yml")
    if not path.exists(config_path):
        print("config.yml was missing. This likely isn't a Pilgrim project.")
        exit(1)
    elif not path.isfile(config_path):
        print("config.yml exists but isn't a file. What???")  # Alternate text: "Huh?"
        exit(1)
    # Project validated!
    with open(config_path) as config_file:
        config = safe_load(config_file)
    if type(config) is not dict:
        raise TypeError(
            "Config was not a dict. This probably means you really screwed up, or Chesyon really screwed up."
        )
    config.update({"Root": pilgrim_root})
    return config


def init_project_directory(project_directory: str):
    """Given a path to an existing directory, populates the directory with the necessary files for a Pilgrim project."""
    copytree(
        path.join(Path(__file__).parent.parent.resolve(), "template_project"), project_directory, dirs_exist_ok=True
    )
    exit(0)


def get_rom_if_exists(config, key: str) -> NintendoDSRom:
    if key not in config["Roms"]:
        print(f"{key} not present in config!")
        exit(1)
    rom_path = path.join(config["Root"], config["Roms"][key])
    try:
        rom = NintendoDSRom.fromFile(rom_path)
    except FileNotFoundError:
        print()
        print(f"ROM for {key} could not be found at {rom_path}. Make sure it exists.")
        exit(1)
    return rom
