from ndspy.rom import NintendoDSRom
from skytemple_files.common.util import get_files_from_rom_with_extension


# Creates FOUR lists based on ROM contents to determine porting process.
# List 1: Files that were added to the modified ROM from the base. Can usually be directly copied to the port target, assuming the code that interacts with them is functionally identical between regions.
# List 2: Files that were modified from the base ROM, but are identical in the base and port target. Can be copied directly to the port target.
# List 3: Files that were modified from the base ROM, and are NOT identical in the base and port target. Will require conversion to function on the port.
# List 4: Files that were modified from the base ROM, but are completely missing from the port target. These cannot be ported easily.
# First input: base ROM that the modified ROM was built from.
# Second input: modified ROM that you're trying to port.
# Third input: the target ROM you're trying to port modifications to.
def create_lists(base_rom: NintendoDSRom, mod_rom: NintendoDSRom, target_rom: NintendoDSRom):
    base_files = get_files_from_rom_with_extension(base_rom, "")
    target_files = get_files_from_rom_with_extension(target_rom, "")
    modified_files = get_files_from_rom_with_extension(mod_rom, "")
    added, _, mod_base_share = categorize_lists(modified_files, base_files)
    _, modified = categorize_shared_files(mod_rom, base_rom, mod_base_share)
    _, target_missing, base_target_share = categorize_lists(target_files, base_files)
    base_target_identical, base_target_different = categorize_shared_files(target_rom, base_rom, base_target_share)
    _, _, modified_base_target_identical = categorize_lists(modified, base_target_identical)
    _, _, modified_base_target_different = categorize_lists(modified, base_target_different)
    _, _, modified_target_missing = categorize_lists(modified, target_missing)
    return added, modified_base_target_identical, modified_base_target_different, modified_target_missing


def categorize_lists(list1: list[any], list2: list[any]):
    '''Categorizes the contents of lists into 3 categories: members that are present in only the first list, members that are present in only the second list, and members that are present in both lists.'''
    list1_exclusive = []
    list2_exclusive = []
    shared = []
    for member in list1:
        if member in list2:
            shared.append(member)
        else:
            list1_exclusive.append(member)
    for member in list2:
        if member not in shared:
            list2_exclusive.append(member)
    return list1_exclusive, list2_exclusive, shared


def categorize_filetypes(filelist_1: list[any], filelist_2: list[any]):
    '''Categorizes extensions by their presence in two separate file lists. Return matches that of categorize_lists.'''
    filelist_1_extensions = extensions_in_list(filelist_1)
    filelist_2_extensions = extensions_in_list(filelist_2)
    always_identical_types, always_different_types, sometimes_different_types = categorize_lists(
        filelist_1_extensions, filelist_2_extensions
    )
    print("Filetypes that are ALWAYS identical between ROMs: " + str(always_identical_types) + "\n")
    print(
        "Filetypes that are sometimes identical and sometimes different between ROMS: "
        + str(sometimes_different_types)
        + "\n"
    )
    print("Filetypes that are ALWAYS different between ROMs: " + str(always_different_types))


def categorize_shared_files(rom1: NintendoDSRom, rom2: NintendoDSRom, file_list: list[str]):
    '''Sort files into two lists, based on if they're identical or different between two ROMs. Expects that all files in the list are present in both ROMs.'''
    identical = []
    different = []
    for shared_file in file_list:
        rom1_shared_file = rom1.getFileByName(shared_file)
        rom2_shared_file = rom2.getFileByName(shared_file)
        if rom1_shared_file == rom2_shared_file:
            identical.append(shared_file)
        else:
            different.append(shared_file)
    return identical, different


def extensions_in_list(file_list: list[str]):
    extension_list = []
    for single_file in file_list:
        extension = single_file.split(".")[-1]
        if extension not in extension_list:
            extension_list.append(extension)
    return extension_list
