from osrparse import Replay
from PIL import Image, ImageFilter, ImageDraw, ImageFont
from os.path import *
import requests
import json
import os

API_URL = r"https://osu.ppy.sh/api/v2"
SONGS_FOLDER = "Songs"
OAUTH_TOKEN_URL = r"https://osu.ppy.sh/oauth/token"
BEATMAP_LOOKUP_URL = r"https://osu.ppy.sh/api/v2/beatmaps/lookup"
WIDTH = 0
HEIGHT = 1
PATHS = {
    "replay_path": "replays",
    "images_path": "images",
    "mod_icon": r"images\mod_icons",
    "default": r"images\mod_icons\default",
    "output_path": "output",
    "cropped_bg": r"output\cropped_bg"
}


def replay_info():
    """
    Gets replay information
    :return: return replay instance
    """
    while True:
        print("Make sure the file is in the replays folder")
        try:
            replay = Replay.from_path("replays/" + input("Replay File Name (include .osr): "))
            return replay

        except ValueError:
            print("File Type Error! Please enter .osr only!")

        except FileNotFoundError:
            print("Path/Wrong File Error! Please type in the correct path (.osr should be in the replays folder!!!)")

        except:
            print("Error: Unresolvable")


def get_token():
    while True:
        try:
            response = requests.post(OAUTH_TOKEN_URL, data=api_info)
            return response.json().get('access_token')

        except:
            print("lease enter ID and Secret!")
            print("token", api_info)
            new_api(api_info)


def find_file(mapset_id, maps):
    for files in maps:
        if str(mapset_id) in files:
            return files


def find_bg(game_dir, folder, diff):
    osu_map_dir = os.listdir(fr"{game_dir}\{SONGS_FOLDER}\{folder}")

    for osu_file in osu_map_dir:
        if diff + "].osu" in osu_file.split("["):
            with open(fr"{game_dir}\{SONGS_FOLDER}\{folder}\{osu_file}", "r", encoding="utf8") as osu_diff:
                print(fr"{game_dir}\{SONGS_FOLDER}\{folder}\{osu_file}")
                file_lines = osu_diff.readlines()

                for line_num in range(0, 100):
                    if "[Events]" in str(file_lines[line_num]):
                        for possible_line in range(line_num, line_num + 5):
                            the_line = str(file_lines[possible_line]).split(',')
                            print(the_line)
                            if len(the_line) > 1 and "0" == the_line[0] and "0" == the_line[1]:
                                return str(file_lines[possible_line]).split('"')[1]


def get_user_api_info():
    user_api = {
        "client_id": "",
        "client_secret": "",
        "grant_type": "client_credentials",
        "scope": "public"
    }

    with open("user.json", "r") as stored_keys_file:
        user_info = json.load(stored_keys_file)
        user_api["client_id"] = user_info["clientID"]
        user_api["client_secret"] = user_info["clientSecret"]

    return user_api


def new_api(user_api):
    user_api["client_id"] = input("Enter Client ID: ")
    user_api["client_secret"] = input("Enter Client Secret: ")

    with open("user.json", "r") as edit_json:
        data = json.load(edit_json)
        data["clientID"] = user_api["client_id"]
        data["clientSecret"] = user_api["client_secret"]

    with open("user.json", "w") as fixed_json:
        json.dump(data, fixed_json, indent=4)


def get_file_dir():
    if "user.json" not in os.listdir():
        with open("user.json", "w") as new_file:
            json.dump({"directory": "", "clientID": "", "clientSecret": ""}, new_file, indent=4)

    while True:
        with open("user.json", "r") as directory_file:
            directory = json.load(directory_file)['directory']
            if exists(fr"{directory}\{SONGS_FOLDER}"):
                return directory

        with open("user.json", "r") as fixing_file:
            data = json.load(fixing_file)
            data['directory'] = input("Enter osu! Main Directory: ")

        with open("user.json", "w") as edited_file:
            json.dump(data, edited_file, indent=4)


def calc_crop(bg_img, bg_dim, bg_ratio, yt_dim, yt_ratio):
    if not bg_ratio == yt_ratio:
        # If Both are bigger
        if bg_dim[WIDTH] > yt_dim[WIDTH] and bg_dim[HEIGHT] > yt_dim[HEIGHT]:
            center_width = int(bg_dim[WIDTH] / 2)
            center_height = int(bg_dim[HEIGHT] / 2)
            bg_img = bg_img.crop((center_width - (yt_dim[WIDTH] / 2),
                                  center_height - (yt_dim[HEIGHT] / 2),
                                  center_width + (yt_dim[WIDTH] / 2),
                                  center_height + (yt_dim[HEIGHT] / 2)))
            print(bg_img.size, bg_img.size[WIDTH] / float(bg_img.size[HEIGHT]))

        # If Width is smaller
        elif bg_dim[WIDTH] < yt_dim[WIDTH] and bg_dim[HEIGHT] > yt_dim[HEIGHT]:
            new_height = int(bg_dim[WIDTH] / yt_ratio)
            start_height = int((bg_dim[HEIGHT] - new_height) / 2)
            bg_img = bg_img.crop((0,
                                  start_height,
                                  bg_dim[WIDTH],
                                  bg_dim[HEIGHT] - start_height))
            print(bg_img.size, bg_img.size[WIDTH] / float(bg_img.size[HEIGHT]))

        # If Height is smaller
        elif bg_dim[WIDTH] > yt_dim[WIDTH] and bg_dim[HEIGHT] < yt_dim[HEIGHT]:
            new_width = int(bg_dim[HEIGHT] * yt_ratio)
            start_width = int((bg_dim[WIDTH] - new_width) / 2)
            bg_img = bg_img.crop((start_width,
                                 0,
                                 bg_dim[WIDTH] - start_width,
                                 bg_dim[HEIGHT]))
            print(bg_img.size, bg_img.size[WIDTH] / float(bg_img.size[HEIGHT]))

    if not (bg_dim[WIDTH] == yt_dim[WIDTH] and bg_dim[HEIGHT] == yt_dim[HEIGHT]):
        bg_img = bg_img.resize((yt_dim[WIDTH], yt_dim[HEIGHT]), Image.ANTIALIAS)

    print(bg_img.size)
    bg_img.show()
    save_cropped_bg(bg_img, mapset_id, difficulty)


def save_cropped_bg(bg_img, mapset_id, diff):
    bg_img.save(fr"output\cropped_bg\{mapset_id}_{diff}.png")


def get_background(song_dir):
    folder_name = find_file(mapset_id, song_dir)
    while not folder_name:
        print(f"Missing map! Download Link: https://osu.ppy.sh/beatmapsets/{beatmap.json()['beatmapset_id']}")
        input("Press any key to continue...")
        song_dir = os.listdir(fr"{osu_dir}\{SONGS_FOLDER}")
        folder_name = find_file(mapset_id, song_dir)

    bg_name = find_bg(osu_dir, folder_name, difficulty)
    bg_path = fr"{osu_dir}\{SONGS_FOLDER}\{folder_name}\{bg_name}"
    print(bg_path)

    # Image Manipulation
    with Image.open(bg_path) as background_image:
        source_dimension = [background_image.size[WIDTH], background_image.size[HEIGHT]]
        source_ratio = background_image.size[WIDTH] / float(background_image.size[HEIGHT])

        thumbnail_dimension = (1280, 720)
        thumbnail_ratio = 1280 / float(720)

        calc_crop(background_image, source_dimension, source_ratio, thumbnail_dimension, thumbnail_ratio)


def check_cropped_bg_exist():
    cropped_bg_dir = os.listdir(fr"output\cropped_bg")
    if f"{mapset_id}_{difficulty}.png" in cropped_bg_dir:
        return True

    return False


def generate_thumbnail(bg_path, player_name, max_combo):
    bg_file = Image.open(bg_path)
    bg_file = bg_file.filter(ImageFilter.BoxBlur(3))
    my_font = ImageFont.truetype('comic.ttf', 90)
    width, height = bg_file.size
    bg = ImageDraw.Draw(bg_file)

    message_width, message_height = bg.textsize(player_name)
    bg.text(((width-message_width)/2, 0), player_name, font=my_font, fill=(255, 0, 0))

    message_width, message_height = bg.textsize(str(max_combo))
    bg.text(((width-message_width)/2, (height-message_height)/2), str(max_combo), font=my_font, fill=(255, 0, 0))
    bg_file.show()
    bg_file.save(bg_path)


if __name__ == "__main__":
    osu_dir = get_file_dir()
    file_dir = os.listdir(fr"{osu_dir}\{SONGS_FOLDER}")
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": ""
    }

    beatmap_params = {
        "checksum": ""
    }

    api_info = get_user_api_info()
    headers["Authorization"] = f"Bearer {get_token()}"

    file = replay_info()
    beatmap_params["checksum"] = file.beatmap_hash

    print(file.username, file.beatmap_hash, file.mods,
          file.max_combo, file.perfect, file.count_miss)
    print(api_info)

    beatmap = requests.get(BEATMAP_LOOKUP_URL, params=beatmap_params, headers=headers)
    player = requests.get(r"https://osu.ppy.sh/api/v2/users/1/osu")
    print(player.json())
    print(beatmap.json())
    difficulty = beatmap.json()['version']
    mapset_id = beatmap.json()['beatmapset_id']

    if not check_cropped_bg_exist():
        get_background(file_dir)

    generate_thumbnail(fr"{PATHS['cropped_bg']}\{mapset_id}_{difficulty}.png", file.username, file.max_combo)