#############################################
#   methods for running Splash Screen GUI   #
#############################################

# import modules
import ast
import importlib
import os
import sys
import threading
import time

import signal

# GUI
from PySide6.QtGui import QPixmap

loading_image = "ico/images/blessingAILogo.png"

###################################################
##  Add System Evn Path
###################################################

# this_script.py
script_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_path)

# src.voice_translator.py
parent_dir = os.path.dirname(script_path)
sys.path.append(parent_dir)
parent_file = os.path.join(parent_dir, "voice_translator.py")

# PyDracula.main
draculaGuiDir = os.path.join(parent_dir, "PyDracula")
sys.path.append(draculaGuiDir)
draculaGUIFile = os.path.join(draculaGuiDir, "main.py")


###################################################
##  Add System Evn Path [END]
###################################################


# <editor-fold desc="[Methods] Loading Packages">
def progress_bar(pg_percent, total):
    if pg_percent == 0:
        return 0
    percent = 100.0 * (float(pg_percent) / float(total))
    return round(percent, 2)


def get_module_names(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    tree = ast.parse(content)
    module_names = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                module_names.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                module_names.append(node.module)

    if len(module_names) == 1:
        return module_names[0]

    return module_names


def merge_string_lists(list1, list2):
    merged_set = set(list1).union(set(list2))
    merged_list = list(merged_set)
    return merged_list


module_list = None
cur_module_count = 0
module_size = 0
cur_module_name = None
cur_progress = 0

console_thread = None
loading_thread = None


def exit_program(loading_window):
    # loading_window.close()
    print("[ERROR]: Quit Program! Please try to restart the Program!")
    loading_window.error_message()


# not using [only for thread]
def background_imports(loading_window):
    global module_list
    # print(parent_file)
    module_list = get_module_names(parent_file)

    module_list = merge_string_lists(module_list, get_module_names(draculaGUIFile))  # Add PyDracula.main.py
    # print(module_list)
    imported_modules = []
    global module_size
    module_size = len(module_list)

    global cur_module_count
    global cur_module_name
    global cur_progress

    for module_name in module_list:
        try:
            cur_module_name = module_name
            cur_progress = progress_bar(cur_module_count, module_size)
            # cur_progress = progress_bar(cur_module_count, module_size)
            print(
                f"loading modules: {module_name} || progress: [{cur_module_count}/{module_size}] {cur_progress}%")
            imported_module = importlib.import_module(module_name)
            imported_modules.append(imported_module)
            cur_module_count = cur_module_count + 1
            cur_progress = progress_bar(cur_module_count, module_size)
        except ImportError as e:
            print(f"Failed to import module {module_name}: {e}")
            exit_program(loading_window)
            # break

    print(
        f"loaded all modules: [{cur_module_count}/{module_size}] {cur_progress}%")


# </editor-fold>

def crop_percen_og(image_path, percent, padx=0):  # todo: using padx set offest to set start pos + end pos
    from PIL import Image
    from PIL.ImageQt import ImageQt

    # Load the original image
    original_image = Image.open(image_path)

    # Calculate the crop width based on the percentage
    width = original_image.width
    crop_width = int(width * (percent / 100))

    # Define the cropping region
    crop_box = (crop_width, 0, width, original_image.height)

    # Create a new image with transparent background
    cropped_image = Image.new("RGBA", original_image.size, (0, 0, 0, 0))

    # Paste the original image onto the cropped image, preserving alpha values
    cropped_image.paste(original_image, (0, 0), mask=original_image)

    # Replace the cropped region with transparent pixels
    cropped_image.paste((0, 0, 0, 0), crop_box)

    # Save the cropped image as QPixmap
    qim = ImageQt(cropped_image)
    return qim


def init_loading_GUI(loading_window):
    txt = "Loading modules... [  ] [0/0]"
    percent_txt = "0 %"
    loading_window.loading_message.setText(f"{txt}")
    loading_window.percentage_text.setText(f"{percent_txt}")
    new_pixmap = QPixmap.fromImage(crop_percent(loading_image, 0, 105))
    loading_window.ProgressTitle.setPixmap(QPixmap(new_pixmap))


def crop_percent(image_path, percent, padx=0):
    from PIL import Image
    from PIL.ImageQt import ImageQt

    # Load the original image
    original_image = Image.open(image_path)

    # Calculate the crop width based on the percentage
    offset = (padx * 2)

    width = original_image.width - offset
    crop_width = int(width * (percent / 100))

    # Define the cropping region
    crop_box = (padx + crop_width, 0, original_image.width, original_image.height)

    # Create a new image with transparent background
    cropped_image = Image.new("RGBA", original_image.size, (0, 0, 0, 0))

    # Paste the original image onto the cropped image, preserving alpha values
    cropped_image.paste(original_image, (0, 0), mask=original_image)

    # Replace the cropped region with transparent pixels
    cropped_image.paste((0, 0, 0, 0), crop_box)

    # Save the cropped image as QPixmap
    qim = ImageQt(cropped_image)
    return qim


def splash_ui_load(loading_window):
    global module_list
    global module_size
    global cur_module_count
    global fake_cur_progress
    global cur_progress

    global cur_module_name

    # initial
    if module_list is None:
        # print("init module_list")
        module_list = get_module_names(parent_file)
        module_list = merge_string_lists(module_list, get_module_names(draculaGUIFile))  # Add PyDracula.main.py
        # print(module_list)
        module_size = len(module_list)

    ############################################################### update loading GUI
    # if fake_cur_progress < 100:
    #     if fake_cur_progress < cur_progress:
    #         fake_cur_progress = delta_anim(fake_cur_progress, cur_progress, 0.03)
    #     else:
    #         fake_cur_progress = cur_progress
    #
    #     fake_cur_progress = round(fake_cur_progress, 2)
    if fake_cur_progress < 100.0:
        fake_cur_progress = cur_progress
        txt = f"Loading modules... [ {cur_module_name} ] [{cur_module_count}/{module_size}]"
        percent_txt = f"{str(fake_cur_progress)} %"
        loading_window.ui.loading_message.setText(f"{txt}")
        loading_window.ui.percentage_text.setText(f"{percent_txt}")

        new_pixmap = QPixmap.fromImage(crop_percent(loading_image, fake_cur_progress, 105))
        loading_window.ui.ProgressTitle.setPixmap(QPixmap(new_pixmap))
    else:
        print(
            f"loaded all modules: [{cur_module_count}/{module_size}] {cur_progress}%")
        done_load(loading_window)

    ############################################################### module importing
    if cur_module_count < module_size:
        module_size = len(module_list)

        module_name = module_list[cur_module_count]
        try:
            cur_module_name = module_name
            cur_progress = progress_bar(cur_module_count, module_size)

            print(
                f"loading modules: {module_name} || progress: [{cur_module_count}/{module_size}] {cur_progress}%")
            imported_module = importlib.import_module(module_name)
            cur_module_count = cur_module_count + 1
            cur_progress = progress_bar(cur_module_count, module_size)
        except ImportError as e:
            print(f"Failed to import module {module_name}: {e}")
            exit_program(loading_window)
            # break


def done_load(loading_window):
    # print("loading all done")
    loading_window.callMainWindow()


def delta_anim(a, b, t):
    result = a + (100 * t)

    if result >= b:
        result = b

    return result


fake_cur_progress = 0

if __name__ == "__main__":
    print("testing loading system")
