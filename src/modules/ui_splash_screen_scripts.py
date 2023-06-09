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

# GUI
from PySide6.QtGui import QPixmap

loading_image = "ico/images/blessingAILogo.png"

script_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_path)
parent_dir = os.path.dirname(script_path)
sys.path.append(parent_dir)
# print(parent_dir)
parent_file = os.path.join(parent_dir, "voice_translator.py")


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

    return module_names


cur_module_count = 0
module_size = 0
cur_module_name = None
load_thread_started = False
cur_progress = 0


def background_imports():
    print(parent_file)
    module_list = get_module_names(parent_file)
    print(module_list)
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

    print(
        f"loaded all modules: [{cur_module_count}/{module_size}] {cur_progress}%")


console_thread = threading.Thread(target=background_imports, daemon=True)
loading_thread = None

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


# Unused
def load(loading_window):
    global module_size
    global cur_module_count
    global fake_cur_progress
    global load_thread_started
    global cur_progress

    if not load_thread_started:
        console_thread.start()

        load_thread_started = True

    # if i <= 100:
    if console_thread.is_alive() or fake_cur_progress < 100:
        if fake_cur_progress < cur_progress:
            fake_cur_progress = delta_anim(fake_cur_progress, cur_progress, 0.03)
        else:
            fake_cur_progress = cur_progress

        fake_cur_progress = round(fake_cur_progress, 2)
        txt = f"Loading modules... [ {cur_module_name} ] [{cur_module_count}/{module_size}]"
        percent_txt = f"{str(fake_cur_progress)} %"
        time.sleep(0.05)
        loading_window.ui.loading_message.setText(f"{txt}")
        loading_window.ui.percentage_text.setText(f"{percent_txt}")

        new_pixmap = QPixmap.fromImage(crop_percent(loading_image, fake_cur_progress, 105))
        loading_window.ui.ProgressTitle.setPixmap(QPixmap(new_pixmap))

        time.sleep(0.01)
        done_load(loading_window)

        # progress_label.configure(text=txt)
        # progress_percent_label.configure(text=precent_txt)
        # progress_label.after(10, load)
        # progress.set(cur_progression * 0.01)

        # print(f"{txt} {percent_txt}")
    else:
        done_load(loading_window)


def background_load(loading_window):
    global loading_thread
    if loading_thread is not None:
        return

    loading_thread = threading.Thread(target=load, args=[loading_window, ], daemon=True)
    loading_thread.start()
    print("loading thread started")


def splash_ui_load(loading_window):
    global module_size
    global cur_module_count
    global fake_cur_progress
    global load_thread_started
    global cur_progress

    if not load_thread_started:
        console_thread.start()

        load_thread_started = True

    # if i <= 100:
    if console_thread.is_alive() or fake_cur_progress < 100:
        if fake_cur_progress < cur_progress:
            fake_cur_progress = delta_anim(fake_cur_progress, cur_progress, 0.03)
        else:
            fake_cur_progress = cur_progress

        fake_cur_progress = round(fake_cur_progress, 2)
        txt = f"Loading modules... [ {cur_module_name} ] [{cur_module_count}/{module_size}]"
        percent_txt = f"{str(fake_cur_progress)} %"
        loading_window.ui.loading_message.setText(f"{txt}")
        loading_window.ui.percentage_text.setText(f"{percent_txt}")

        new_pixmap = QPixmap.fromImage(crop_percent(loading_image, fake_cur_progress, 105))
        loading_window.ui.ProgressTitle.setPixmap(QPixmap(new_pixmap))
    else:
        done_load(loading_window)


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
