from hashlib import file_digest

def sha256_file(file_path: str) -> str:
    with open(file_path, "rb") as f:
        digest = file_digest(f, "sha256")
    return digest.hexdigest()

def verify_vanilla_eu(eu_path: str) -> bool:
    '''Checks if a given file is a vanilla NA EoS ROM.'''
    return sha256_file(eu_path) == "1fa39d35873b58e02f3623438414c334ad93b840651a8a9ac13ee3c789f170c1"

def verify_vanilla_na(na_path: str) -> bool:
    '''Checks if a given file is a vanilla EU EoS ROM.'''
    return sha256_file(na_path) == "91161cb227c44a3e79fa2a622060385815f565647357062d7887f13f49d591e2"