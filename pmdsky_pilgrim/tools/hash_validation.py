 #  Copyright 2025 Chesyon
 #
 #  This source code is licensed under the MIT license: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_MIT
 #  However, the distribution is licensed under GPLv3: https://github.com/Chesyon/Pilgrim/blob/main/LICENSE_GPLv3
 #  For a non-legalese version of what this means, see https://chesyon.me/eos-licenses.html.

from hashlib import file_digest
from os.path import join


def sha256_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        digest = file_digest(f, "sha256")
    return digest.hexdigest()


def verify_vanilla_eu(config) -> bool:
    """Checks if a given file is a vanilla NA EoS ROM."""
    return (
        sha256_file(join(config["Root"], config["Roms"]["Vanilla EU"]))
        == "1fa39d35873b58e02f3623438414c334ad93b840651a8a9ac13ee3c789f170c1"
    )


def verify_vanilla_na(config) -> bool:
    """Checks if a given file is a vanilla EU EoS ROM."""
    return (
        sha256_file(join(config["Root"], config["Roms"]["Vanilla NA"]))
        == "91161cb227c44a3e79fa2a622060385815f565647357062d7887f13f49d591e2"
    )
