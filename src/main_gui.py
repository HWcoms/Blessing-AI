# import modules
import ast
import importlib
import sys
import threading

import customtkinter

value = 0

# pre-define
global _adm


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
    module_list = get_module_names("voice_translator.py")
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

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

width = 576
height = 820

loading_root = customtkinter.CTk()
loading_root.title("Loading... Blessing-AI")
loading_root.iconbitmap("ico/blessing-soft.ico")

x = (loading_root.winfo_screenwidth() // 2) - (width // 2)
y = (loading_root.winfo_screenheight() // 2) - (height // 2)

# Loadning_Program GUI
loading_root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

# loading_root.geometry("500x350")
loading_root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

loading_background_frame = customtkinter.CTkFrame(master=loading_root, fg_color="grey13", width=width, height=height)
loading_background_frame.place(x=0, y=0)

loading_title_frame = customtkinter.CTkFrame(master=loading_root)
# loading_frame.configure(fg_color="blue")
loading_title_frame.pack(side="top", fill="x")
loading_label = customtkinter.CTkLabel(master=loading_title_frame, text="Blessing-AI", font=("Roboto", 30))
loading_label.pack(side="top", pady=12, padx=10)

# progress_label.pack(pady=5, padx=10)
loading_frame = customtkinter.CTkFrame(master=loading_root)
loading_frame.place(relx=0.5, rely=0.5, anchor="center")

progress_label = customtkinter.CTkLabel(master=loading_frame, text="Loading...", font=("Roboto", 16))
progress_label.pack(pady=0, padx=10)

progress = customtkinter.CTkProgressBar(master=loading_frame, border_width=1, border_color="#aaaaaa",
                                        orientation="horizontal", width=400, height=25,
                                        mode="determinate")
progress.pack(pady=1, padx=10)

progress_percent_label = customtkinter.CTkLabel(master=loading_frame, text="%", font=("Roboto", 16))
progress_percent_label.pack(pady=0, padx=10)


def buttonf():
    import voice_translator

    print("Button pressed")
    string = entry1.get()
    if string == '' or string is None:
        return
    print(voice_translator.DoTranslate(string, 'en', 'ko'))


mic_switch_var = customtkinter.StringVar(value="on")


def load_chatlog():
    import voice_translator
    import LangAIComm
    character_name, tts_character_name, tts_language, voice_id, voice_volume, USE_D_BOT = voice_translator.load_tts_setting()

    ch_name_label.configure(text=f"Charcter name: {character_name}")

    # Load ChatLog
    chatlog_file_path = LangAIComm.check_chatlog(character_name)
    chatlog_srt = LangAIComm.load_chatlog(chatlog_file_path)

    if chatlog_srt is None:
        print(f"Error on [GUI]: could not load chatlog!")
        return

    chatlogdialog.configure(state="normal")
    chatlogdialog.delete("0.0", "end")
    chatlogdialog.insert("0.0", chatlog_srt)
    chatlogdialog.configure(state="disabled")


def mic_switch_event():
    print("switch toggled, current value:", mic_switch_var.get())


def load_device_info():
    import aud_device_manager as adm

    global _adm
    _adm = adm.AudioDevice()

    str_device_list = str(_adm.get_all_device())

    # Split the string by new lines
    str_device_list = str_device_list.split('\n')

    # Remove leading/trailing white spaces and store in a list
    result_str_list = [line.strip() for line in str_device_list]

    mic_list = []
    speaker_list = []

    #
    for item in result_str_list:
        if "(2 in, 0 out)" in item:
            # Mics
            mic_list.append(item)
        if "(0 in, 2 out)" in item:
            # Speakers
            speaker_list.append(item)
    return mic_list, speaker_list


def init_device_selector(mic_list, spk_list):
    import aud_device_manager as adm

    global _adm
    _adm = adm.AudioDevice()
    _adm.init_selected_device()
    mic, spk = _adm.get_selected_device()
    if isinstance(mic, tuple):
        mic = mic[0]
    if isinstance(spk, tuple):
        spk = spk[0]

    mic_name = mic['name']
    spk_name = spk['name']
    for item in mic_list:
        if mic_name in item:
            result_mic = mic_name
            break

    for item in spk_list:
        if spk_name in item:
            result_spk = spk_name
            break

    mic_selector_var = customtkinter.StringVar(value=mic_name)
    spk_selector_var = customtkinter.StringVar(value=spk_name)


# Main Program GUI
root = customtkinter.CTk()
root.title("Blessing-AI")
root.iconbitmap("ico/blessing-soft.ico")

# Create A Main Frame
# main_frame = customtkinter.CTkFrame(master=root)
# main_frame.pack(pady=20, padx=60, fill="both", expand=True)

# Create A Canvas

# Add a Scrollbar To The Canvas
main_frame = customtkinter.CTkScrollableFrame(master=root)
main_frame.pack(pady=20, padx=10, fill="both", expand=True)

label = customtkinter.CTkLabel(master=main_frame, text="Blessing AI", font=("Roboto", 24))
label.pack(pady=12, padx=10)

entry1 = customtkinter.CTkEntry(master=main_frame, placeholder_text="Username", )
entry1.pack(pady=12, padx=10)

entry2 = customtkinter.CTkEntry(master=main_frame, placeholder_text="pass", show="*")
entry2.pack(pady=12, padx=10)

# Character Info
ch_name_label = customtkinter.CTkLabel(master=main_frame, text="Character_name: ", font=("Roboto", 16))
ch_name_label.pack(pady=12, padx=10)

# ChatLog Text Box
chatlogdialog = customtkinter.CTkTextbox(master=main_frame,
                                         border_width=1, border_color="#aaaaaa",
                                         width=int(width * 0.8),
                                         height=int(height * 0.6),
                                         activate_scrollbars=True)
chatlogdialog.configure(state="disabled")
chatlogdialog.pack(pady=12, padx=10, fill="x")

# Audio Settings


# Audio Device Selector
mic_selector_list, speaker_selector_list = load_device_info()

drdown_font = ("Gulim", 14)
mic_selector = customtkinter.CTkComboBox(master=main_frame, values=mic_selector_list,
                                         width=500,
                                         font=drdown_font, dropdown_font=drdown_font)
mic_selector.pack(pady=12, padx=10)
speaker = customtkinter.CTkComboBox(master=main_frame, values=speaker_selector_list,
                                    width=500,
                                    font=drdown_font, dropdown_font=drdown_font)
speaker.pack(pady=12, padx=10)

# Mic Toggle
mic_switch_1 = customtkinter.CTkSwitch(master=main_frame,
                                       switch_width=38, switch_height=20,
                                       text="Mic Toggle", command=mic_switch_event, font=("Roboto", 16),
                                       variable=mic_switch_var, onvalue="on", offvalue="off")

mic_switch_1.pack(pady=12, padx=10)

button = customtkinter.CTkButton(master=main_frame, command=load_chatlog)
button.pack(pady=12, padx=10)
checkbox = customtkinter.CTkCheckBox(master=main_frame, text="checkbox test")
checkbox.pack(pady=12, padx=10)

init_device_selector()


def on_closing():
    try:
        print("Quit Blessing-AI")
        sys.exit()
    except Exception as e:
        print(f"Error on [GUI]: {e}")


def top():
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))

    loading_root.withdraw()
    # add code: run main program

    # print(voice_translator.DoTranslate("hello", 'en', 'ko'))    # test
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

    loading_root.destroy()


def delta_anim(a, b, t):
    result = a + (100 * t)

    if result >= b:
        result = b

    return result


cur_progression = 0


def load():
    global module_size
    global cur_module_count
    global cur_progression
    global load_thread_started

    if not load_thread_started:
        console_thread.start()
        load_thread_started = True

    # if i <= 100:
    if console_thread.is_alive():
        percent = progress_bar(cur_module_count, module_size)
        if cur_progression < percent:
            cur_progression = delta_anim(cur_progression, percent, 0.01)
        else:
            cur_progression = percent

        cur_progression = round(cur_progression, 2)
        txt = f"Loading... {cur_module_name}  [{cur_module_count}/{module_size}]"
        precent_txt = f"{str(cur_progression)} %"
        progress_label.configure(text=txt)
        progress_percent_label.configure(text=precent_txt)
        progress_label.after(10, load)
        progress.set(cur_progression * 0.01)
    else:
        top()


# Testing main Program
top()

# Start with Loading Program
# load()
# loading_root.protocol("WM_DELETE_WINDOW", on_closing)
# loading_root.resizable(False, False)
# loading_root.mainloop()
