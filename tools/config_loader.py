import yaml
from os.path import join
import pathlib
from sys import argv

# Once things are further along, we should rework this such we're only opening the file once for the entire Pilgrim run. That'll have to come in when we're combining scripts, though.
def get_config():
    pilgrim_root = str(pathlib.Path(__file__).parent.parent.resolve())
    config_path = join(pilgrim_root, 'config.yml')
    with open(config_path) as config_file:
        config = yaml.safe_load(config_file)
    if type(config) != dict:
        raise TypeError("Config was not a dict")
    config["Root"] = pilgrim_root 
    return config