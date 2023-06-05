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

script_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(script_path)
parent_dir = os.path.dirname(script_path)
sys.path.append(parent_dir)
print(parent_dir)
parent_file = os.path.join(parent_dir, "voice_translator.py")

# <editor-fold desc="[Methods] Loading Packages">
def progress_bar(cur_progress, total):
    if cur_progress == 0:
        return 0
    percent = 100 * (cur_progress / float(total))
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


def background_imports():
    print(parent_file)
    module_list = get_module_names(parent_file)
    print(module_list)
    imported_modules = []
    global module_size
    module_size = len(module_list)

    global cur_module_count
    global cur_module_name

    for module_name in module_list:
        try:
            cur_module_name = module_name
            print(
                f"loading modules: {module_name} || progress: [{cur_module_count}/{module_size}] {progress_bar(cur_module_count, module_size)}%")
            imported_module = importlib.import_module(module_name)
            imported_modules.append(imported_module)
            cur_module_count = cur_module_count + 1
        except ImportError as e:
            print(f"Failed to import module {module_name}: {e}")

    print(
        f"loaded all modules: [{cur_module_count}/{module_size}] {progress_bar(cur_module_count, module_size)}%")


console_thread = threading.Thread(target=background_imports, daemon=True)


# </editor-fold>

def crop_percent(image_path, percent):
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


def load(window):
    global module_size
    global cur_module_count
    global cur_progression
    global load_thread_started

    if not load_thread_started:
        console_thread.start()
        load_thread_started = True

    # if i <= 100:
    if console_thread.is_alive() or cur_progression < 100:
        percent = progress_bar(cur_module_count, module_size)
        if cur_progression < percent:
            cur_progression = delta_anim(cur_progression, percent, 0.01)
        else:
            cur_progression = percent

        cur_progression = round(cur_progression, 2)
        txt = f"Loading modules... [ {cur_module_name} ] [{cur_module_count}/{module_size}]"
        percent_txt = f"{str(cur_progression)} %"
        time.sleep(0.05)
        window.loading_message.setText(f"{txt}")
        window.percentage_text.setText(f"{percent_txt}")

        new_pixmap = QPixmap.fromImage(crop_percent("ico/images/blessingAILogo.png", cur_progression))
        window.ProgressTitle.setPixmap(QPixmap(new_pixmap))

        time.sleep(0.05)
        load(window)

        # progress_label.configure(text=txt)
        # progress_percent_label.configure(text=precent_txt)
        # progress_label.after(10, load)
        # progress.set(cur_progression * 0.01)

        # print(f"{txt} {percent_txt}")
    else:
        top(window)


def background_load(window):
    loading_thread = threading.Thread(target=load, args=[window, ], daemon=True)
    loading_thread.start()
    print("loading thread started")


def top(window):
    print("loading all done")
    window.callMainWindow()



def delta_anim(a, b, t):
    result = a + (100 * t)

    if result >= b:
        result = b

    return result


cur_progression = 0

if __name__ == "__main__":
    print("testing loading system")
