#  Copyright 2025 Chesyon
#
#  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
#  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
#  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

from ndspy.rom import NintendoDSRom
from skytemple_files.graphics.bg_list_dat.handler import BgListDatHandler
from skytemple_files.graphics.bg_list_dat._model import BgListEntry, BgList
from .colors import BLUE_TEXT, YELLOW_TEXT, CLEAR_TEXT, GREEN_TEXT

BG_LIST_DAT_FILE = "MAP_BG/bg_list.dat"


class BGToCopy:
    def __init__(self, entry: BgListEntry, eu_index: int, added: bool):
        self.entry = entry  # Note: This is the MODIFIED entry!
        self.eu_index = eu_index  # The index the entry was found in in the modified bg_list.dat.
        self.added = (
            added  # Was this index outside the vanilla list? (In other words, was this added onto the end of the list?)
        )
        self.na_index = None  # The index that Pilgrim should put this entry in for the NA ROM.

    def __str__(self) -> str:
        return f"Index {self.eu_index}: {str(self.entry)}"


def create_na_bg_list(vanilla_eu: NintendoDSRom, mod_eu: NintendoDSRom, vanilla_na: NintendoDSRom):
    """Creates the MAP_BG/bg_list.dat file for mod_na."""
    print(f"{YELLOW_TEXT}Checking MAP_BG/bg_list.dat...{CLEAR_TEXT}")
    handler = BgListDatHandler()
    bg_list_vanilla_eu = handler.deserialize(vanilla_eu.getFileByName(BG_LIST_DAT_FILE))
    bg_list_mod_eu = handler.deserialize(mod_eu.getFileByName(BG_LIST_DAT_FILE))
    bg_list_vanilla_na = handler.deserialize(vanilla_na.getFileByName(BG_LIST_DAT_FILE))

    bgs_to_copy = compare_base_to_mod(bg_list_vanilla_eu, bg_list_mod_eu)
    if len(bgs_to_copy) <= 0:
        print(f"{GREEN_TEXT}bg_list.dat is unmodified! Skipping...{CLEAR_TEXT}")
        return
    else:
        print(f"{BLUE_TEXT}bg_list.dat is modified! Porting...{CLEAR_TEXT}")
    find_na_indexes(bgs_to_copy, bg_list_vanilla_eu, bg_list_vanilla_na)
    for bg_to_copy in bgs_to_copy:
        if bg_to_copy.added:
            bg_list_vanilla_na.add_level(bg_to_copy.entry)
        else:
            bg_list_vanilla_na.set_level(bg_to_copy.na_index, bg_to_copy.entry)
    vanilla_na.setFileByName(BG_LIST_DAT_FILE, handler.serialize(bg_list_vanilla_na))


def compare_base_to_mod(base: BgList, modified: BgList) -> list[BGToCopy]:
    """Compile a list of entries in bg_list.dat that have been modified. Note that this does NOT check file contents, only the names of the files that make up a background."""
    level_base = base.level
    level_modified = modified.level
    bgs_to_copy = []
    if len(level_modified) < len(level_base):
        raise ValueError("Modified ROM has a shorter bg_list.dat than the base ROM. This shouldn't be possible?")
    for i in range(len(level_base)):
        base_entry = level_base[i]
        modified_entry = level_modified[i]
        if str(base_entry) != str(
            modified_entry
        ):  # There's probably a more efficient way to compare BgListEntries than this.
            print(f"Entry {i} does not match")
            bgs_to_copy.append(BGToCopy(modified_entry, i, False))
    for i in range(len(level_base), len(level_modified)):
        modified_entry = level_modified[i]
        print(f"Entry {i} is newly added")
        bgs_to_copy.append(BGToCopy(modified_entry, i, True))
    return bgs_to_copy


def find_na_indexes(bgs_to_copy: list[BGToCopy], eu: BgList, na: BgList):
    """Fills in the na_index value for every entry in the bgs_to_copy list."""
    eu_list = eu.level
    na_list = na.level
    na_str_list = [str(x) for x in na_list]
    for bg_to_copy in bgs_to_copy:
        if not bg_to_copy.added:
            try:
                eu_str = str(
                    eu_list[bg_to_copy.eu_index]
                )  # Get the vanilla version of the entry at this index so we can search for it.
                na_index = na_str_list.index(eu_str)  # Find the index of the matching entry in NA.
                bg_to_copy.na_index = na_index  # Write that index to NA.
            except ValueError:
                print(f"EU entry [{str(eu_str)}], index {bg_to_copy.eu_index}, is not present in NA's list.")
        print(f"EU index {bg_to_copy.eu_index} maps to NA index {bg_to_copy.na_index}")
