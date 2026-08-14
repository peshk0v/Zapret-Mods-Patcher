from fileinput import filename
import os
import json
from importlib import resources
import zipfile, time

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

    def get_lists(self):
        arch = self.define()
        if arch is not None:
            listsDirArch = os.listdir(os.path.join(self.ptz, self.zaprets[arch]["lists"]))
            lists = {}
            for i in listsDirArch:
                if i.endswith(".txt"):
                    lists[i] = os.path.join(self.ptz, self.zaprets[arch]["lists"], i)
            return lists
        else:
            return None

    def get_mod_lists(self, mod_path):
        if not os.path.exists(mod_path):
            raise FileNotFoundError(f"Mod file '{mod_path}' does not exist.")
            return None
        with zipfile.ZipFile(mod_path, "r") as zip_ref:
            mod_lists = [f for f in zip_ref.namelist() if f.endswith(".txt")]
            return mod_lists

    def unpack_mod(self, mod_path):
        if not os.path.exists(mod_path):
            raise FileNotFoundError(f"Mod file '{mod_path}' does not exist.")
            return None
        if "mod" in os.listdir(self.ptz):
            os.rmdir(self.ptz + "/mod")
        with zipfile.ZipFile(mod_path, "r") as zip_ref:
            os.mkdir(self.ptz + "/mod")
            zip_ref.extractall(self.ptz + "/mod")

    def patchMod(self, mod_path):
        self.unpack_mod(mod_path)
        arch = self.define()
        if arch is None:
            raise ValueError("Could not determine the architecture of the Zapret directory.")
            return None
        lists = self.get_lists()
        if lists is None:
            raise ValueError("Could not find any lists in the Zapret directory.")
            return None
        for i in lists:
            list_path = lists[i]
            mod_list_path = os.path.join(self.ptz, "mod", i)
            if os.path.exists(mod_list_path):
                with open(list_path, "a", encoding="utf-8") as f:
                    with open(mod_list_path, "r", encoding="utf-8") as mod_f:
                        f.write("\n")
                        f.write(mod_f.read())
        for i in os.listdir(os.path.join(self.ptz, "mod")):
            if i.endswith(".bat"):
                if not self.zaprets[arch]["bats"] == "/":
                    os.command(f"mv {os.path.join(self.ptz, 'mod', i)} {os.path.join(self.ptz, self.zaprets[arch]['bats'], i)}")
                else:
                    os.command(f"mv {os.path.join(self.ptz, 'mod', i)} {os.path.join(self.ptz, i)}")
        os.rmdir(self.ptz + "/mod")