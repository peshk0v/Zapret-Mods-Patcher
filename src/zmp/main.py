from zmp import patcher


patcher

def cli():
    pa = patcher.Patcher("/home/peach/Apps/zapret-discord-youtube-linux/")
    arch = pa.define()
    print(f"Hello World from ZMP! {arch}")