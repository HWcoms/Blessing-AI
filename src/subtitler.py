from datetime import datetime
from threading import Thread
from time import sleep

load_ready = False
start_time = datetime.utcnow()

load_emote_index = 3


def loading_emote():
    global load_emote_index
    str = ''

    for i in range(load_emote_index):
        str += '.'

    for i in range(3 - load_emote_index):
        str += ' '

    if (load_emote_index > 2):
        load_emote_index = 0
        # print(load_emote_index)
    else:
        # print(load_emote_index,end="")
        load_emote_index += 1

    return str


def voice_ready(str):
    print(f"\r{str}{loading_emote()}          ", end="")


def loading(str):
    while (load_ready == False):
        delta_t = (datetime.utcnow() - start_time)
        print(f"\r{str}{loading_emote()} [{delta_t.total_seconds()} sec]          ", end="")
        sleep(0.05)

    print()


t_loading = Thread(target=loading, args=["Initiating"])
t_loading.start()

import signal
import sys
import textwrap
import threading
import tkinter as tk
from os import getenv
from queue import Queue

from dotenv import load_dotenv

from modules.audio_translate import translate_audio

load_dotenv()

OFFSET_X = int(getenv('OFFSET_X'))
OFFSET_Y = int(getenv('OFFSET_Y'))
SUBTITLE_FONT_SIZE = int(getenv('SUBTITLE_FONT_SIZE'))
SUBTITLE_COLOR = getenv('SUBTITLE_COLOR')
SUBTITLE_BG_COLOR = getenv('SUBTITLE_BG_COLOR')
SACRIFICIAL_COLOR = getenv('SACRIFICIAL_COLOR')


# pyglet.font.add_file('a땅콩M.ttf')

def subtitle_updater(root, queue, label):
    # font_ = tkinter.font.Font("맑은 고딕", size = SUBTITLE_FONT_SIZE, slant = 'bold')

    # Check if there is something new in the queue to display.
    while not queue.empty():
        # destroy old label since new message inbound
        label.destroy()
        if root.wm_state() == 'withdrawn':
            # show root window
            root.deiconify()

        # create subtitle based on message in queue
        msg = queue.get()
        label = tk.Label(
            text=textwrap.fill(msg, 64),
            # font=('a땅콩M.ttf', SUBTITLE_FONT_SIZE, 'bold'),
            font=("Noto Sans KR", SUBTITLE_FONT_SIZE),
            fg=SUBTITLE_COLOR,
            bg=SUBTITLE_BG_COLOR
        )

        # hide root and destroy label after 3s
        label.after(3000, root.withdraw)
        label.after(3000, label.destroy)

        # place subtitle at bottom middle of screen
        label.pack(side='bottom', anchor='s')
        root.update_idletasks()

    # run every 0.5s
    root.after(50, lambda: subtitle_updater(root, queue, label))


def setup_overlay():
    # set tkinter gui to be topmost without window
    root = tk.Tk()
    root.overrideredirect(True)
    root.geometry(f'{root.winfo_screenwidth()}x{root.winfo_screenheight()}+{OFFSET_X}+{OFFSET_Y}')
    root.lift()
    root.wm_attributes('-topmost', True)
    root.wm_attributes('-disabled', True)

    # Sacrifice random color for transparency
    root.wm_attributes('-transparentcolor', SACRIFICIAL_COLOR)
    root.wm_attributes('-alpha', 0.7)

    root.config(bg=SACRIFICIAL_COLOR)

    # hide initial window
    root.withdraw()

    return root


def close_app(*_):
    print('Closing subtitler.')
    sys.exit(0)


def start_app():
    # catch keyboard interrupt to stop main thread
    signal.signal(signal.SIGINT, close_app)

    overlay = setup_overlay()
    subtitle = tk.Label()
    subtitle_queue = Queue()

    # thread to listen and translate audio
    threading.Thread(target=translate_audio, args=[subtitle_queue], daemon=True).start()

    # updates subtitles every 0.5s by checking queue
    subtitle_updater(overlay, subtitle_queue, subtitle)

    # set full-screen applications to borderless window for subtitles to appear over it
    overlay.mainloop()


if __name__ == '__main__':
    load_ready = True
    start_app()
