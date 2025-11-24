from .find_offset import OffsetMapper, UnmappableOffsetException, AddressOverlay, overlay_of_offset
from capstone import Cs, CS_ARCH_ARM, CS_MODE_ARM
from skytemple_files.data.data_cd.model import DataCD
from ndspy.rom import NintendoDSRom
from .colors import CLEAR_TEXT, BLUE_TEXT, RED_TEXT
# from offsets.asm_reader import FindTargetAddressStatus, Region, XmapReader, print_addresses

# TODO: All of this code is atrocious, rewrite it eventually. Surely there are better ways to keep track of information relevant to an SP than five billion different dictionaries. Probably use a dataclass...?

PROC_START_ADDRESS_EU = 0x22E7B88
PROC_START_ADDRESS_EU_STR = hex(PROC_START_ADDRESS_EU)
PROCESS_BIN_PATH = "BALANCE/process.bin"

FIRST_CUSTOM_SP_ID = 61


class SP:
    def __init__(self, raw_bytes: bytes, id: int, capstone: Cs):
        """Disassembles an SP from bytes using Capstone, and finds potential convertible offsets."""
        print(f"{BLUE_TEXT}Disassembling SP {id}...{CLEAR_TEXT}")
        self.id = id
        disassembled = capstone.disasm_lite(raw_bytes, PROC_START_ADDRESS_EU)
        # Entry in convertible_offsets: { address: (overlay, [line_nums])}
        self.source = f'.relativeinclude on\n.nds\n.arm\n\n; File creation\n.create "./code_out.bin", {PROC_START_ADDRESS_EU_STR}\n    .org {PROC_START_ADDRESS_EU_STR}\n'
        self.convertible_offsets = {PROC_START_ADDRESS_EU_STR[2:]: (AddressOverlay.OVERLAY_11, [5, 6])}
        load_addresses = []
        for instruction in disassembled:
            # instruction[0]: address
            # instruction[1]: size
            # instruction[2]: mnemonic
            # instruction[3]: op_str
            address = instruction[0]
            if instruction[1] != 4:
                raise ValueError(
                    "A disassembled SP instruction wasn't length 4! Pilgrim does not know how to handle this!"
                )
            mnemonic = instruction[2]
            mnemonic = mnemonic.replace("ldm", "ldmia")
            op_str = instruction[3]
            # NOTE: this idea of detecting pool loads probably breaks if the load falls AFTER the address its loading from. might be worth reworking this to just do a second pass over everything.
            if address in load_addresses:
                # This is a pool address! Convert it to a .word!
                offset = address - PROC_START_ADDRESS_EU
                # Next two lines might be optimizable
                raw_val = raw_bytes[offset : offset + 4]
                raw_hex = raw_val[::-1].hex()
                self.try_add_new_offset(raw_hex, self.source.count("\n"))
                self.source += f"        .word 0x{raw_hex}\n"
            else:
                if mnemonic.startswith("ldr") and "[pc" in op_str:
                    # this is a pool load
                    offset = int(op_str.split("#")[-1][:-1], 16) + 8
                    load_addresses.append(address + offset)
                # Check for BL/B functions. Currently we do this by filtering to starting with 'b', and then making sure no letters from "non-bl/b" instructions are present. Jank but if it works it works?
                elif (
                    mnemonic.startswith("b")
                    and "f" not in mnemonic
                    and "i" not in mnemonic
                    and "k" not in mnemonic
                    and "x" not in mnemonic
                ):
                    potential_offset = op_str[3:]
                    self.try_add_new_offset(potential_offset, self.source.count("\n"))
                # TODO: Determine how Capstone decompiles words that aren't valid instructions. Is it just .word like armips? Please tell me it is.
                self.source += f"        {mnemonic} {op_str}\n"
        self.source += ".close"
        # print(self.source)
        # print(self.convertible_offsets)

    def try_add_new_offset(self, offset: str, line: int):
        """Checks if an offset is convertible. If it is, it'll either add the line to an existing entry for the offset, or make a new entry if one doesn't already exist for this offset."""
        if offset in self.convertible_offsets.keys():
            self.convertible_offsets[offset][1].append(line)
        else:
            overlay = overlay_of_offset(int(offset, 16))
            if overlay != AddressOverlay.UNKNOWN:
                self.convertible_offsets.update({offset: (overlay, [line])})

    def apply_offsets(self, offset_maps: dict[str, str]) -> str:
        """Given a map of old offsets to new offsets, generates a new source with the converted offsets from the original source."""
        lines = self.source.splitlines(True)
        for convertible_offset in self.convertible_offsets:
            lines_to_edit = self.convertible_offsets[convertible_offset][1]
            for line_num in lines_to_edit:
                lines[line_num] = lines[line_num].replace(convertible_offset, offset_maps[convertible_offset])
        converted_source = ""
        for line in lines:
            converted_source += line
        return converted_source


class SPConverter:
    def __init__(self, rom: NintendoDSRom, config):
        try:
            process_bin = rom.getFileByName(PROCESS_BIN_PATH)
        except ValueError:
            raise FileNotFoundError(
                "BALANCE/process.bin couldn't be found. This likely means SPs aren't extracted and you don't need SPConverter."
            )
        self.data_cd = DataCD(process_bin)
        self.cs = Cs(CS_ARCH_ARM, CS_MODE_ARM)
        self.sps = []
        self.all_convertible_offsets = {}
        self.offset_mapper = OffsetMapper()
        self.config = config
        self.offset_maps = None

    def prepare_all(self):
        for i in range(FIRST_CUSTOM_SP_ID, len(self.data_cd.effects_code)):
            self.prepare_sp(i)

    def prepare_sp(self, id: int):
        """Disassemble an SP and find any new convertible offsets."""
        effect_code = bytearray(self.data_cd.get_effect_code(id))
        sp = SP(effect_code, id, self.cs)
        self.sps.append(sp)
        new_convertible_offsets = [
            offset for offset in sp.convertible_offsets.keys() if offset not in self.all_convertible_offsets.keys()
        ]
        for new_convertible_offset in new_convertible_offsets:
            # add {offset: overlay}
            self.all_convertible_offsets.update(
                {new_convertible_offset: sp.convertible_offsets[new_convertible_offset][0]}
            )

    def log_convertible_offsets(self):
        for convertible_offset in self.all_convertible_offsets:
            print(self.convertible_offset_tostr(convertible_offset))

    def convertible_offset_tostr(self, convertible_offset: str) -> str:
        overlay = self.all_convertible_offsets[convertible_offset]
        match overlay:
            case AddressOverlay.ARM9:
                overlay_name = "arm9"
            case AddressOverlay.OVERLAY_10:
                overlay_name = "overlay10"
            case AddressOverlay.OVERLAY_11:
                overlay_name = "overlay11"
            case _:
                raise ValueError(f"Invalid overlay {overlay} given to convertible_offset_tostr")
        return f"0x{convertible_offset} [EU] in {overlay_name}"

    def create_map(self):
        if len(self.all_convertible_offsets) == 0:
            print("No offsets to convert!")
            return {}
        if "OffsetMaps" not in self.config:
            print(f"{RED_TEXT}OffsetMaps was missing from config. Aborting :({CLEAR_TEXT}")
            exit(1)
        else:
            offset_maps = self.config["OffsetMaps"]
            if offset_maps is None:
                offset_maps = {}
            missing_offsets = []
            for eu_offset in self.all_convertible_offsets:
                if eu_offset not in offset_maps:
                    try:
                        na_offset = self.offset_mapper.find_na_offset(
                            int(eu_offset, 16)
                        )[
                            2:
                        ]  # This [2:] is just to remove the 0x at the start, because otherwise we have 2 0xs and everything explodes.
                        offset_maps.update({eu_offset: na_offset})
                    except UnmappableOffsetException:
                        missing_offsets.append(eu_offset)
            if len(missing_offsets) != 0:  # Abort because some offsets couldn't be found
                print(
                    f"{len(missing_offsets)} offsets could not be automatically converted! Please find them manually and provide them through config. Missing offsets:"
                )
                for missing_offset in missing_offsets:
                    print(self.convertible_offset_tostr(missing_offset))
                print("Aborting :(")
                exit(1)
        self.offset_maps = offset_maps

    def convert_all(self, output_rom: NintendoDSRom):
        """Applies offset maps to SPs. create_map must be called before this. Afterwards, writes the converted SPs into the given ROM."""
        if self.offset_maps is None:
            raise TypeError("Offsets map was never made (did you call create_map?)")
        try:
            process_bin = output_rom.getFileByName(PROCESS_BIN_PATH)
        except ValueError:
            raise FileNotFoundError(
                "BALANCE/process.bin couldn't be found in the output ROM. Is ExtractSPCode applied?"
            )
        out_data_cd = DataCD(process_bin)
        for sp in self.sps:
            print(f"{BLUE_TEXT}Converting and importing SP {sp.id}...{CLEAR_TEXT}")
            while sp.id >= len(out_data_cd.effects_code):
                out_data_cd.add_effect_code(bytes("TEMP", "ascii"))
            applied_offsets = sp.apply_offsets(self.offset_maps)
            try:
                out_data_cd.import_armips_effect_code(sp.id, applied_offsets)
            except Exception as e:
                print(f"{RED_TEXT}Error encountered! SP source is as follows:\n{applied_offsets}\nOriginal error:\n{e}{CLEAR_TEXT}")
                exit(1)
