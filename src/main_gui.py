# import modules
import ast
import importlib
import sys
import threading

import customtkinter

value = 0

# pre-define
import modules.aud_device_manager as adm

_adm = adm.AudioDevice("compact")


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
# </editor-fold>


customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("dark-blue")

width = 576
height = 820

# <editor-fold desc="[GUI] Loading CTK settings">
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
# </editor-fold>


# <editor-fold desc="[GUI] Main-Program Methods">
mic_switch_var = customtkinter.StringVar(value="on")


def buttonf():
    import voice_translator

    print("Button pressed")
    string = entry1.get()
    if string == '' or string is None:
        return
    print(voice_translator.DoTranslate(string, 'en', 'ko'))


def mic_switch_event():
    print("switch toggled, current value:", mic_switch_var.get())


# ChatLog Button
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


# Device Selector
def update_combobox(mic_val, spk_val):
    global mic_selector_combo
    global speaker_selector_combo

    mic_selector_combo.set(mic_val)
    speaker_selector_combo.set(spk_val)


def mic_combobox_callback(choice):
    print("Changed Mic Device:", choice)
    set_device_selector(mic=choice)


def spk_combobox_callback(choice):
    print("Changed Speaker Device:", choice)
    set_device_selector(spk=choice)


def init_combobox():
    return _adm.get_mic_name_list(), _adm.get_speaker_name_list(), _adm.selected_mic.name, _adm.selected_speaker.name


def set_device_selector(mic=None, spk=None):
    mic_selected = None
    spk_selected = None

    if mic is None:
        mic_selected = _adm.selected_mic.name
    else:
        mic_selected = _adm.set_selected_mic(mic).name
    if spk is None:
        spk_selected = _adm.selected_speaker.name
    else:
        spk_selected = _adm.set_selected_speaker(spk).name

    update_combobox(mic_selected, spk_selected)


def on_closing():
    try:
        print("Quit Blessing-AI")
        sys.exit()
    except Exception as e:
        print(f"Error on [GUI]: {e}")


# </editor-fold>


# <editor-fold desc="[GUI] Main-Program Settings">
# Main Program GUI
root = customtkinter.CTk()
root.title("Blessing-AI")
root.iconbitmap("ico/blessing-soft.ico")



# Add a Scrollbar To The Canvas
main_frame = customtkinter.CTkScrollableFrame(master=root,fg_color="blue")


# main_frame.pack(pady=20, padx=10, fill="both", expand=True)
# main_frame.grid(row=0, column=0,columnspan=2, padx=20, pady=(20, 0),sticky="nesw")

chatlog_frame = customtkinter.CTkFrame(master=main_frame,fg_color="white")

chatlog_frame.grid_rowconfigure(0, weight=1)
chatlog_frame.grid_columnconfigure((0, 1), weight=1)
chatlog_frame.pack(fill="both")

label = customtkinter.CTkLabel(master=chatlog_frame, text="Blessing AI", font=("Roboto", 24),fg_color="yellow")
label.grid(row=0, column=0,columnspan=2)

entry1 = customtkinter.CTkEntry(master=chatlog_frame, placeholder_text="Username", )
entry1.grid(row=1,column=0, padx=20, pady=20, sticky="ew")

entry2 = customtkinter.CTkEntry(master=main_frame, placeholder_text="pass", show="*")
entry2.grid(row=1,column=1, padx=20, pady=20, sticky="ew")
#
# # Character Info
# ch_name_label = customtkinter.CTkLabel(master=main_frame, text="Character_name: ", font=("Roboto", 16))
# ch_name_label.pack(pady=12, padx=10)
#
# # ChatLog Text Box
# chatlogdialog = customtkinter.CTkTextbox(master=main_frame,
#                                          border_width=1, border_color="#aaaaaa",
#                                          width=int(width * 0.8),
#                                          height=int(height * 0.6),
#                                          activate_scrollbars=True)
# chatlogdialog.configure(state="disabled")
# chatlogdialog.pack(pady=12, padx=10, fill="x")
#
# # Audio Settings
#
#
# # Audio Device Selector
#
# mic_selector_list, speaker_selector_list, selected_mic, selected_spk = init_combobox()
#
#
# drdown_font = ("Gulim", 14)
# mic_selector_label = customtkinter.CTkLabel(master=main_frame, text="Mic", font=("Roboto", 16))
# mic_selector_label.pack(side="left",)
# mic_selector_combo = customtkinter.CTkComboBox(master=main_frame, values=mic_selector_list,
#                                                width=500,
#                                                font=drdown_font, dropdown_font=drdown_font,
#                                                command=mic_combobox_callback)
# mic_selector_combo.pack(side="left")
#
# blank_label = customtkinter.CTkLabel(master=main_frame)
# blank_label.pack(pady=30)
#
# speaker_selecto_label = customtkinter.CTkLabel(master=main_frame, text="Speaker", font=("Roboto", 16))
# speaker_selecto_label.pack(side="left", fill="both")
# speaker_selector_combo = customtkinter.CTkComboBox(master=main_frame, values=speaker_selector_list,
#                                                    width=500,
#                                                    font=drdown_font, dropdown_font=drdown_font,
#                                                    command=spk_combobox_callback)
# speaker_selector_combo.pack(side="left")
#
# # Update after init
# update_combobox(selected_mic, selected_spk)
#
# # Mic Toggle
# mic_switch_1 = customtkinter.CTkSwitch(master=main_frame,
#                                        switch_width=38, switch_height=20,
#                                        text="Mic Toggle", command=mic_switch_event, font=("Roboto", 16),
#                                        variable=mic_switch_var, onvalue="on", offvalue="off")
#
# mic_switch_1.pack(pady=12, padx=10)
#
# button = customtkinter.CTkButton(master=main_frame, command=load_chatlog)
# button.pack(pady=12, padx=10)
# checkbox = customtkinter.CTkCheckBox(master=main_frame, text="checkbox test")
# checkbox.pack(pady=12, padx=10)
#

# </editor-fold>


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


fake_cur_progress = 0


def load():
    global module_size
    global cur_module_count
    global fake_cur_progress
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
