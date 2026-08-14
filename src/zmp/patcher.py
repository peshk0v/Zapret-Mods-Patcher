import json
import shutil
import zipfile
from importlib import resources
from pathlib import Path


class Patcher:

  def __init__(self, pathToZapret):
    self.ptz = Path(pathToZapret).resolve()
    self.zaprets = self.load_json_data("zaprets.json")

  def load_json_data(self, filename):
    data_path = resources.files("zmp.data").joinpath(filename)
    with data_path.open("r", encoding="utf-8") as f:
      return json.load(f)

  def define(self):
    if not self.ptz.exists():
      return None

    arch_contents = {item.name for item in self.ptz.iterdir()}

    for name, config in self.zaprets.items():
      if all(target in arch_contents for target in config["targets"]):
        return name
    return None

  def get_lists(self):
    arch = self.define()
    if arch is None:
      return None

    lists_rel = self.zaprets[arch]["lists"].strip("/\\")
    lists_dir = self.ptz / lists_rel

    if not lists_dir.exists():
      return None

    return {
        f.name: f
        for f in lists_dir.iterdir()
        if f.is_file() and f.suffix.lower() == ".txt"
    }

  def unpack_mod(self, mod_path):
    mod_path = Path(mod_path).resolve()
    if not mod_path.exists():
      raise FileNotFoundError(f"Mod file '{mod_path}' does not exist.")

    mod_dir = self.ptz / "mod"

    if mod_dir.exists():
      shutil.rmtree(mod_dir)

    with zipfile.ZipFile(mod_path, "r") as zip_ref:
      zip_ref.extractall(mod_dir)

  def patchMod(self, mod_path):
    self.unpack_mod(mod_path)

    arch = self.define()
    if arch is None:
      raise ValueError("Could not determine the architecture of Zapret.")

    lists = self.get_lists()
    if lists is None:
      raise ValueError("Could not find any lists directory.")

    mod_dir = self.ptz / "mod"

    mod_txt_files = {}
    script_files = []

    for file_path in mod_dir.rglob("*"):
      if file_path.is_file():
        ext = file_path.suffix.lower()
        if ext == ".txt":
          mod_txt_files[file_path.name] = file_path
        elif ext in (".bat", ".cmd", ".sh"):
          script_files.append(file_path)

    for list_name, target_txt_path in lists.items():
      if list_name in mod_txt_files:
        content = mod_txt_files[list_name].read_text(encoding="utf-8").strip()
        if content:
          with open(target_txt_path, "a", encoding="utf-8") as f:
            f.write(f"\n{content}\n")

    raw_bats = self.zaprets[arch]["bats"].strip("/\\")
    if not raw_bats:
      target_bat_dir = self.ptz
    else:
      target_bat_dir = self.ptz / raw_bats

    target_bat_dir.mkdir(parents=True, exist_ok=True)

    for script_path in script_files:
      dest_path = target_bat_dir / script_path.name
      shutil.move(str(script_path), str(dest_path))

      try:
        dest_path.chmod(dest_path.stat().st_mode | 0o111)
      except OSError:
        pass
      
    shutil.rmtree(mod_dir)