from PySide6.QtCore import QThread, QObject

import os
import pyaudio
import audioop
from math import log10
import numpy as np
import wave
import time
from color_log import print_log

from aud_device_manager import AudioDevice

from voice_detect import is_human_voice, is_wav_human_voice

FORMAT = pyaudio.paInt16
CHANNELS = 1

root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
cache_dir = os.path.join(root_dir, 'cache', 'user_mic')
dest_file_path = os.path.join(cache_dir, 'test.wav')

# CHECK VOICE CACHE FOLDER
if not os.path.exists(cache_dir):
    os.makedirs(cache_dir)
    print_log("warning", "Created user voice cache folder!", cache_dir)


class MicRecorder(QThread):
    def __init__(self, target_gui: QObject, timeout_gui: QObject, is_sub: bool):
        super().__init__()
        self.toggle_on = True   # Toggle to Save Audio file and create prompt_thread

        # for meter settings
        self.adm = None
        self.init_meters()
        self.target_gui = target_gui  # ex) Slider_mic_threshold or Slider_sub_mic_threshold
        self.timeout_gui = timeout_gui  # ex) Slider_main_phrase_timeout or Slider_sub_phrase_timeout
        self.main_program = None
        self.is_sub = is_sub

        # human voice detection
        self.ignore_silence = True  # prevent to save, if not human voice detected
        self.energy_threshold = 150  # minimum audio energy to consider for recording [default: 300]

        # Log
        self.log = True

    def init_meters(self):
        self.device_name = None

        self.p = pyaudio.PyAudio()

        self.sample_rate = 0
        self.frames = []

        self.rms = 0
        self.cur_db = 0
        self.stream = None
        # self.adm = None
        self.rec_duration = -1
        self.done = False
        self.is_recording = False
        self.is_phrase_time = False

        self.margin = 1
        self.samples_per_section = int(720.0 / 3.0 - 2 * self.margin)

        self.sound_tracks = [[0] * self.samples_per_section] * 3
        self.max_value = [0] * 3

        self.current_section = 0

        self.samples = []
        self.ac, self.avg, self.max_db = 0, 0, 0

    def run(self):
        self.record_mic(_adm=self.adm, duration=self.rec_duration)

    def stop(self):
        self.close_stream()
        self.init_meters()
        self.quit()
        self.wait(5000)

    def record_mic(self, _adm: AudioDevice, chunk=1024, duration=-1):
        log_str = ''
        if self.is_sub:
            log_str = 'Sub '

        print_log("red", f"{log_str}Mic Recorder start..", custom_logging=self.log)

        if _adm is None:
            raise RuntimeError("ADM is None")

        adm_mic = None

        if self.is_sub:
            if _adm.selected_sub_mic:
                if not _adm.selected_sub_mic.name:
                    raise RuntimeError("No Sub Mic Device Set")
                adm_mic = _adm.selected_sub_mic
        else:
            if _adm.selected_mic:
                if not _adm.selected_mic.name:
                    raise RuntimeError("No Mic Device Set")
                adm_mic = _adm.selected_mic

        self.sample_rate = int(self.p.get_default_input_device_info()['defaultSampleRate'])

        device_index, _ = _adm.get_pyaudio_index(adm_mic.name)

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=CHANNELS,
                                  rate=self.sample_rate,
                                  input=True,
                                  output=False,
                                  frames_per_buffer=chunk,
                                  input_device_index=device_index)
        cur_i = 0

        if not self.target_gui:
            print_log("error", "No target gui(threshold) found!",
                      "Check Error, if this code called from other python file",
                      custom_logging=self.log)
            cur_threshold = 50
        if not self.timeout_gui:
            print_log("error", "No timeout gui found!",
                      "Check Error, if this code called from other python file",
                      custom_logging=self.log)
            cur_timeout = 3.0

        while not self.done:
            # Get current threshold
            if self.target_gui:
                cur_threshold = self.target_gui.value()

            if self.timeout_gui:
                cur_timeout = self.timeout_gui.value() / 100.0

            toggle = self.check_toggle()

            if duration != -1:  # Loop if duration -1
                max_i = int(self.sample_rate / chunk * duration)
                if cur_i > max_i:
                    print('Mic Recorder Loop Finished' + f' duration: {duration}')
                    self.done = True
                cur_i = cur_i + 1
            # for i in range(0, int(self.sample_rate / chunk * seconds)):
            total = 0

            data = self.stream.read(chunk,
                                    exception_on_overflow=False)
            # self.frames.append(data)

            reading = audioop.max(data, 2)

            # scaling factor
            total = 20 * (log10(abs(reading)))
            db = self.ag_samples(total)

            color_type = ""
            if float(db) > 70:
                color_type = "error"
            elif float(db) > 50:
                color_type = "warning"
            elif float(db) > 30:
                color_type = "log"
            else:
                color_type = "white"

            self.cur_db = round(float(db), 2)
            self.draw_mic_threshold()
            # print_log(color_type, f'[{self.cur_db}] db, max: {self.max_db}', print_func_name=False)

            # delta_time = [-1.0, -1.0]

            # Compare with threshold
            if toggle:
                if not self.is_recording:
                    if cur_threshold <= self.cur_db:
                        print_log("white", f"{log_str}Mic exceed Threshold! Recording Started!", custom_logging=self.log)
                        self.is_recording = True
                        start_time = time.time()
                    self.draw_phrase_timeout(0)  # reset timeout GUI
                else:
                    # Recording...
                    cur_time = time.time()
                    remain_time = cur_timeout

                    if cur_threshold <= self.cur_db:
                        self.is_phrase_time = False
                        self.frames.append(data)
                    else:
                        # append blank frames
                        silence_frame = b'\x00' * len(data)
                        self.frames.append(silence_frame)
                        # self.frames.append(bytes(0))

                    # IF pharse_time has no activated & cur_db is below than threshold
                    if not self.is_phrase_time:
                        if cur_threshold > self.cur_db:
                            self.is_phrase_time = True
                            phrase_start_time = time.time()
                            # print_log("white", f"{log_str}Mic is lower than threshold! Phrase timer Start")
                    # In phrase time
                    else:
                        delta_time = abs(cur_time - phrase_start_time)
                        remain_time = cur_timeout - delta_time
                        if 0 >= remain_time:
                            self.save_audio_file(round(cur_time - start_time, 1))
                            self.frames.clear()
                            self.is_phrase_time = False
                            self.is_recording = False
                            remain_time = 0.0
                        else:
                            # print(f'phrase time {cur_time - phrase_start_time:.2f}', " secs")
                            pass

                    self.draw_phrase_timeout(remain_time)
            else:
                self.draw_phrase_timeout(0)
                self.frames.clear()
                self.is_phrase_time = False
                self.is_recording = False

            time.sleep(0.01)
        self.done = False
        self.cur_db = 0
        self.draw_mic_threshold()  # clear threshold drawn to 0 level
        self.draw_phrase_timeout(0)
        self.is_recording = False
        self.is_phrase_time = False

        self.close_stream()
        print_log("red", f"{log_str}Mic Recorder Stop", custom_logging=self.log)

    def close_stream(self):
        # Terminate Stream
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def save_audio_file(self, audio_length_info=-1.0):
        if not self.toggle_on or not self.check_toggle():
            return

        file_path = self.new_audio_path()

        if self.is_sub:
            prefix = 'Sub'
        else:
            prefix = 'Main'

        if audio_length_info > 0.0:
            l_info = f' [{audio_length_info} sec]'
        else:
            l_info = ''

        s_file = wave.open(file_path, "wb")
        s_file.setnchannels(CHANNELS)
        s_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        s_file.setframerate(self.sample_rate)
        s_file.writeframes(b''.join(self.frames))
        s_file.close()

        detect_result = is_wav_human_voice(file_path, self.energy_threshold)

        if not detect_result:
            os.remove(file_path)
            print_log("warning", f'this is not human voice: {file_path}', custom_logging=self.log)
        else:
            print_log("log", f"{prefix} Mic Recorded your Voice", f'{file_path}{l_info}', custom_logging=self.log)

            # Send Signal to run Speech to text
            self.stt_request(file_path, audio_length_info)

    def stt_request(self, audio_file, audio_length):
        if self.main_program:
            try:
                self.main_program.gen_prompt_thread_as_audio(audio_file, audio_length)
            except RuntimeError as e:
                print_log("warning", "no main program! maybe program ended", e)
                self.stop()


    def ag_samples(self, sample):
        """ collect samples and average if needed. """
        if sample == 0:
            return 0
        if self.ac < 1:
            if sample > 1:
                self.samples.append(sample)
                self.ac = self.ac + 1
        else:
            self.avg = sum(self.samples) / len(self.samples)
            if float(self.avg) > float(self.max_db):
                self.max_db = "%.2f" % self.avg
            self.ac = 0
            self.samples = []

        return "%.2f" % self.avg

    def check_mic_changed(self):
        if self.adm:
            if self.is_sub:
                if self.adm.selected_sub_mic:
                    if not self.adm.selected_sub_mic.name:
                        self.done = True
                else:
                    self.done = True
            else:
                if self.adm.selected_mic:
                    if not self.adm.selected_mic.name:
                        self.done = True
                else:
                    self.done = True
        if self.done:
            return
        # check changed
        if self.is_sub:
            adm_mic = self.adm.selected_sub_mic
        else:
            adm_mic = self.adm.selected_mic
        if adm_mic:
            if adm_mic.name != self.device_name:
                print_log('warning', "mic device got changed", custom_logging=self.log)
                self.device_name = adm_mic.name
                self.done = True

    def draw_mic_threshold(self):
        # [Mic Threshold GUI] Call Signal from main program
        if self.main_program:
            try:
                self.main_program.update_threshold_gui_signal.emit(self.cur_db, self.target_gui)
            except RuntimeError as e:
                print_log("warning", "no main program! maybe program ended", e)
                self.stop()

    def draw_phrase_timeout(self, remain_time):
        # [Phrase time GUI] Call Signal from main program
        # [Mic Threshold GUI] Call Signal from main program
        if self.main_program:
            try:
                self.main_program.update_phrase_timeout_gui_signal.emit(remain_time, self.timeout_gui)
            except RuntimeError as e:
                print_log("warning", "no main program! maybe program ended", e)
                self.stop()

    def new_audio_path(self):
        import glob

        if self.is_sub:
            prefix = 'sub'
        else:
            prefix = 'main'

        num = 0
        while True:
            check_name = f'mic_{num}_*.wav'
            file_path = os.path.join(cache_dir, check_name)
            file_list = glob.glob(file_path)
            if not file_list:
                file_name = f'mic_{num}_{prefix}.wav'
                new_file_path = os.path.join(cache_dir, file_name)
                return new_file_path

            # if not os.path.exists(file_path):
            #     return file_path
            num += 1

    def check_toggle(self):
        toggle_widget = None
        result = False

        if self.main_program:
            if not self.is_sub:
                if self.main_program.ui.pushButton_main_mic_toggle:
                    toggle_widget = self.main_program.ui.pushButton_main_mic_toggle
            else:
                if self.main_program.ui.pushButton_sub_mic_toggle:
                    toggle_widget = self.main_program.ui.pushButton_sub_mic_toggle
        if toggle_widget:
            result = toggle_widget.isChecked()
            # print(toggle_widget.objectName(), f': {result}')
        return result


if __name__ == "__main__":
    adm = AudioDevice()
    # print(adm)
    # adm.set_selected_mic("VoiceMeeter Aux Output")
    adm.set_selected_mic("라인")
    print(adm.selected_mic)

    mic_rec = MicRecorder(None, None, False)
    mic_rec.adm = adm
    mic_rec.rec_duration = -1.0

    mic_rec.start()
    # print(mic_rec.new_audio_path())
    time.sleep(100)
    # print(dest_file_path)
