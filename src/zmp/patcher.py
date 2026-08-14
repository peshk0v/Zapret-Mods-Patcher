from fileinput import filename
import os
import json
from importlib import resources

class Patcher:
    def __init__(self, pathToZapret):
        self.ptz = pathToZapret
        self.zaprets = self.load_json_data("zaprets.json")

    def load_json_data(self, filename):
        data_path = resources.files("zmp.data").joinpath(filename)
    
        with data_path.open("r", encoding="utf-8") as f:
            return json.load(f)
    
    def define(self):
        arch = os.listdir(self.ptz)
        for i in self.zaprets:
            for target in self.zaprets[i]["targets"]:
                if target not in arch:
                    break
            else:
                return i
        return None