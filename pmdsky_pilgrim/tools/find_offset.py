#  Copyright 2025 Chesyon
#
#  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
#  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
#  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

from enum import Enum
from pmdsky_debug_py.protocol import Symbol
from pmdsky_debug_py.eu import EuArm9Section, EuOverlay10Section, EuOverlay11Section
from pmdsky_debug_py.na import NaArm9Section, NaOverlay10Section, NaOverlay11Section

AddressOverlay = Enum(
    "AddressOverlay", ["UNKNOWN", "ARM9", "OVERLAY_10", "OVERLAY_11", "SPECIAL_PROCESS", "OVERLAY_36"]
)

# These are pretty much just constants and the calculations *should* be pretty fast, so I just load them off the bat.
ARM9_EU_START = EuArm9Section.loadaddress
ARM9_EU_END = ARM9_EU_START + EuArm9Section.length
ARM9_NA_START = NaArm9Section.loadaddress
OV10_EU_START = EuOverlay10Section.loadaddress
OV10_EU_END = OV10_EU_START + EuOverlay10Section.length
OV10_NA_START = NaOverlay10Section.loadaddress
OV11_EU_START = EuOverlay11Section.loadaddress
OV11_EU_END = OV11_EU_START + EuOverlay11Section.length
OV11_NA_START = NaOverlay11Section.loadaddress
SP_EU_START = 0x22E7B88
SP_EU_END = SP_EU_START + 0x810
SP_NA_START = 0x22E7248
OV36_START = 0x23A7080
OV36_END = OV36_START + 0x38F80


class OffsetMapper:
    def __init__(self):
        # Initialize to none, load as needed.
        self.arm9_eu_table = None
        self.arm9_na_table = None
        self.ov10_eu_table = None
        self.ov10_na_table = None
        self.ov11_eu_table = None
        self.ov11_na_table = None

    def find_na_offset(self, eu_offset: int) -> str:
        match overlay_of_offset(eu_offset):
            case AddressOverlay.ARM9:
                if (
                    self.arm9_eu_table is None
                ):  # we can assume that if the EU table isn't initialized, the NA one isn't either
                    self.arm9_eu_table = init_generic_eu_table(EuArm9Section, ARM9_EU_START)
                    self.arm9_na_table = init_generic_na_table(NaArm9Section, ARM9_NA_START)
                eu_table = self.arm9_eu_table
                na_table = self.arm9_na_table
            case AddressOverlay.OVERLAY_10:
                if (
                    self.ov10_eu_table is None
                ):  # we can assume that if the EU table isn't initialized, the NA one isn't either
                    self.ov10_eu_table = init_generic_eu_table(EuOverlay10Section, OV10_EU_START)
                    self.ov10_na_table = init_generic_na_table(NaOverlay10Section, OV10_NA_START)
                eu_table = self.ov10_eu_table
                na_table = self.ov10_na_table
            case AddressOverlay.OVERLAY_11:
                if (
                    self.ov11_eu_table is None
                ):  # we can assume that if the EU table isn't initialized, the NA one isn't either
                    self.ov11_eu_table = init_generic_eu_table(EuOverlay11Section, OV11_EU_START)
                    self.ov11_na_table = init_generic_na_table(NaOverlay11Section, OV11_NA_START)
                eu_table = self.ov11_eu_table
                na_table = self.ov11_na_table
            case AddressOverlay.SPECIAL_PROCESS:
                return hex(eu_offset + SP_NA_START - SP_EU_START)
            case AddressOverlay.OVERLAY_36:
                return hex(eu_offset)
            case _:
                raise UnmappableOffsetException(
                    f"Offset {hex(eu_offset)} isn't within arm9, ov10, ov11, ov36, or an SP"
                )
        lesser_eu_table_offset = 0
        for eu_table_offset in eu_table:  # REQUIRES DICT TO BE SORTED BY OFFSET TO WORK
            if eu_offset > eu_table_offset:
                lesser_eu_table_offset = eu_table_offset
            elif eu_offset < eu_table_offset:
                # This is our greater offset
                greater_eu_table_offset = eu_table_offset
                break
            else:
                # If our offset falls exactly on a symbol, skip doing any math and just get the exact symbol NA offset.
                return hex(na_table[eu_table[eu_table_offset]])
        nearest_eu_symbols_distance = (
            greater_eu_table_offset - lesser_eu_table_offset
        )  # How far apart are the nearest two symbols?
        # Get NA offsets of nearest symbols
        lesser_na_table_offset = na_table[eu_table[lesser_eu_table_offset]]
        greater_na_table_offset = na_table[eu_table[greater_eu_table_offset]]
        nearest_na_symbols_distance = (
            greater_na_table_offset - lesser_na_table_offset
        )  # How far apart are the NA equivalents of the nearest two symbols?
        if nearest_eu_symbols_distance != nearest_na_symbols_distance:
            raise UnmappableOffsetException(
                f"Offset {hex(eu_offset)} is not mappable, distance between nearest symbols ({eu_table[lesser_eu_table_offset]} and {eu_table[greater_eu_table_offset]}) differs between EU ({hex(nearest_eu_symbols_distance)}) and NA ({hex(nearest_na_symbols_distance)})"
            )
        # Symbols are the same distance apart in NA and EU
        return hex(eu_offset - lesser_eu_table_offset + lesser_na_table_offset)


class UnmappableOffsetException(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

    def __str__(self):
        return self.message


def overlay_of_offset(offset: int) -> AddressOverlay:
    if ARM9_EU_START <= offset and offset <= ARM9_EU_END:
        return AddressOverlay.ARM9
    elif OV10_EU_START <= offset and offset <= OV10_EU_END:
        return AddressOverlay.OVERLAY_10
    elif OV11_EU_START <= offset and offset <= OV11_EU_END:
        return AddressOverlay.OVERLAY_11
    elif SP_EU_START <= offset and offset <= SP_EU_END:
        return AddressOverlay.SPECIAL_PROCESS
    elif OV36_START <= offset and offset <= OV36_END:
        return AddressOverlay.OVERLAY_36
    return AddressOverlay.UNKNOWN


def init_generic_eu_table(section, section_start) -> dict[int, str]:
    """Compile a sorted dictionary of offset:symbolname for a section (overlay)."""
    symbol_dict = dict(section.functions.__dict__)
    symbol_dict.update(section.data.__dict__)
    symbol_table = {section_start: "SECTION_START"}
    for symbol_name in symbol_dict:
        symbol = symbol_dict[symbol_name]
        if type(symbol) is Symbol and symbol.absolute_addresses is not None:
            for i in range(len(symbol.absolute_addresses)):
                symbol_table.update({symbol.absolute_addresses[i]: f"{symbol_name}{i}"})
    symbol_table.update({section_start + section.length: "SECTION_END"})
    symbol_table = dict(sorted(symbol_table.items()))  # sort by key value
    return symbol_table


def init_generic_na_table(section, section_start) -> dict[str, int]:
    """Compile a dictionary of symbolname:offset for a section (overlay)."""
    symbol_dict = dict(section.functions.__dict__)
    symbol_dict.update(section.data.__dict__)
    symbol_table = {"SECTION_START": section_start}
    for symbol_name in symbol_dict:
        symbol = symbol_dict[symbol_name]
        if type(symbol) is Symbol and symbol.absolute_addresses is not None:
            for i in range(len(symbol.absolute_addresses)):
                symbol_table.update({f"{symbol_name}{i}": symbol.absolute_addresses[i]})
    symbol_table.update({"SECTION_END": section_start + section.length})
    return symbol_table
