global program_name,version_discriminator
program_name = 'YHAM'
version_discriminator='v4.0'
# Webapp dependency
import codecs
import json
import sys
import os
from datetime import datetime
from random import randint
import shutil
# manage save data using pickle
import pickle

# FUNCTIONS
# plyer for desktop notifications
from plyer import notification as plyer_notification
# pyperclip for clipboard
from pyperclip import copy as clipboard


def notify(m="An Unknown Error Occured", t_o=0.3):
    plyer_notification.notify(
        app_name=program_name,
        app_icon=load_resource("resources/icon.ico"),
        message=m,
        # displaying time
        timeout=t_o
    )

# define the ad creation function with random paramters


def send_source():
    return sources

def append_mask(text):
            # don't question the length of this string. it's discord, do you expect this to make any fucking sense?
            text_mask = "||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||||​||"
            return(text+text_mask)

def create_ad(
    mode,
    lock_text,
    lock_affil,
    lock_invite,
    lock_top,
    lock_bottom,
    current_ad,
    ad,
    affil,
    inv,
    imgtop,
    imgbottom,
):
    def set_effects():
        rand_ad = (
            current_ad[0]
            if lock_text
            else
            ads[randint(0, len(ads)-1)]
        )
        rand_affil = (
            current_ad[1]
            if lock_affil
            else
            affiliates[randint(0, len(affiliates)-1)]
        )
        rand_inv = (
            current_ad[2]
            if lock_invite
            else
            invites[randint(0, len(invites) - 1)]
        )
        rand_imgtop = (
            current_ad[3]
            if lock_top
            else top_images[randint(0, len(top_images) - 1)]
        )
        rand_imgbottom = (
            current_ad[4]
            if lock_bottom
            else bottom_images[randint(0, len(bottom_images) - 1)]
        )
        return [rand_ad, rand_affil, rand_inv, rand_imgtop, rand_imgbottom]
    # try to parse the user input as Integer data. If it is string or other false data, push an error
    advertisement = None
    if mode:
        try:
            advertisement = [ads[int(ad)-1], affiliates[int(affil)-1], invites[int(
                inv)-1], top_images[int(imgtop)-1], bottom_images[int(imgbottom)-1]]
        except ValueError:
            notify("Input must be a number")
        except IndexError:
            notify("Inputs out of range")
    else:
        advertisement = set_effects()
    if advertisement != None:
        return advertisement
# pickle save event


def save_object(obj):
    try:
        pickledata = (f"{DIRPATH}""/userdat/data.pickle")
        with open(pickledata, "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        notify(f"Error during saving data (Possibly unsupported):{ex}", 2)
    return (obj)

def save_config(obj):
    try:
        pickledata = (f"{DIRPATH}""/userdat/config.pickle")
        with open(pickledata, "wb") as f:
            pickle.dump(obj, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as ex:
        notify(f"Error during saving config (Possibly unsupported):{ex}", 2)
    return (obj)
    
def load_resource(relative_path):
    base_path = getattr(
        sys,
        '_MEIPASS',
        os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)


# pyperclip copy event
def copy(advertisement, value, hide_links):
    string_list = (
        (
            advertisement[0],
            advertisement[1],
            advertisement[2],
            advertisement[3],
        )
        if value.get()
        else (
            advertisement[0],
            advertisement[2],
            advertisement[3],
            advertisement[4],
        )
    )
    try:
        text_description = append_mask(string_list[0]) if hide_links == True else string_list[0]
        string_to_copy = (f"{text_description}\n{string_list[1]}\n{string_list[2]}\n{string_list[3]}")  
        clipboard(string_to_copy)
    except Exception:
        notify("Add to clipboard could not be completed due to error")


# parse backend data from text config file
# load and cache the config file
DIRPATH = os.path.dirname(sys.executable)

default_config = load_resource("resources/config.txt")
current_config = f"{DIRPATH}/config.txt"

def regenerate_config():
    # config not found, regenerate file
    config_file = load_resource("resources/config.txt")
    shutil.copy(config_file, DIRPATH)
    notify("session/config not found, loading defaults")


def backup_config():
    print("<BACKEND> Backing up")
    if current_config is None:
        print("<BACKEND> No backup found at location")
    else:
        config_new_filename = "config-recovery" + \
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".txt"
        # create backup
        os.rename(
            current_config,
            f"{DIRPATH}/userdat/backups/{config_new_filename}",
        )
        data_new_filename = "data-recovery" + \
            datetime.now().strftime('%Y-%m-%d-%H-%M-%S') + ".pickle"
        os.rename(f"{DIRPATH}/userdat/data.pickle",
                  f"{DIRPATH}/userdat/backups/{data_new_filename}")
        regenerate_config()
        os.execl(sys.executable, sys.executable,
                 os.path.relpath(r"main_app.py"))


try:
    config_file = f"{DIRPATH}/config.txt"
    config = codecs.open(config_file, encoding="utf8")
except Exception:
    regenerate_config()
    config_file = f"{DIRPATH}/config.txt"
    config = codecs.open(config_file, encoding="utf8")

tabloid = config.read()
config.close()
sources = json.loads(tabloid, strict=False)

ads = sources["Advertisements"]
affiliates = sources["Affiliates"]
invites = sources["Invites"]
top_images = sources["TopImage"]
bottom_images = sources["BottomImage"]

# Default Advertisement Variable
try:
    default_advertisement = (
        ads[0], affiliates[0], invites[0], top_images[0], bottom_images[0])
except IndexError:
    backup_config()


# pickle load event
DEFAULT_SESSION = {
    "text_lock": 0,
    "affiliate_lock": 0,
    "invite_lock": 0,
    "top_image_lock": 0,
    "bottom_image_lock": 0,
    "rate_enabled": 0,
    "random_enabled": 0,
    "preset_switch": 0,
    "rate": 0,
    "appearance": "System",
    "theme": "blue",
    "ui_scale": "100%",
    "hide_links": False,
    "last_advertisement": default_advertisement,
    "preset_1": ("Unsed Preset", default_advertisement),
    "preset_2": ("Unused Preset", default_advertisement),
    "preset_3": ("Unused Preset", default_advertisement),
    "preset_4": ("Unused Preset", default_advertisement),
    "preset_5": ("Unused Preset", default_advertisement),
    "preset_6": ("Unsed Preset", default_advertisement),
    "preset_7": ("Unused Preset", default_advertisement),
    "preset_8": ("Unused Preset", default_advertisement),
    "preset_9": ("Unused Preset", default_advertisement),
    "preset_10": ("Unused Preset", default_advertisement),
    "preset_11": ("Unused Preset", default_advertisement),
    "preset_12": ("Unused Preset", default_advertisement)
}


def load_session_with_fallback():
    try:
        session = (f"{DIRPATH}""/userdat/data.pickle")
        with open(session, "rb") as f:
            return pickle.load(f)
    except Exception as ex:
        notify(f"No save found, starting new session \n\n{ex}", 2)
        return DEFAULT_SESSION
