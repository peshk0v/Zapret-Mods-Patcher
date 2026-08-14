import sys
from zmp import patcher


patcher

def cli():
    pa = patcher.Patcher(sys.argv[1])
    arch = pa.define()
    lists = pa.get_lists()
    print(f"Hello World from ZMP! {arch}, Lists: {lists}")
    pa.patchMod(sys.argv[2])