from os.path import *
import os

paths = {
    "replay_path": "replays",
    "images_path": "images",
    "mod_icon": r"images\mod_icons",
    "default": r"images\mod_icons\default",
    "output_path": "output",
    "cropped_bg": r"output\cropped_bg"
}

for path in paths:
    if not exists(paths[path]):
        os.makedirs(paths[path])
