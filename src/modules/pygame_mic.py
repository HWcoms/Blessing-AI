from PySide6.QtCore import QThread, QObject

import pyaudio
import audioop
from math import log10
import numpy as np
import wave
import time
from color_log import print_log

from aud_device_manager import AudioDevice

FORMAT = pyaudio.paInt16
CHANNELS = 1


class MicRecorder(QThread):
    def __init__(self, target_gui: QObject, is_sub: bool):
        super().__init__()

        # for meter settings
        self.adm = None
        self.init_meters()
        self.target_gui = target_gui  # ex) Slider_mic_threshold or Slider_sub_mic_threshold
        self.main_program = None
        self.is_sub = is_sub

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

        self.margin = 1
        self.samples_per_section = int(720.0 / 3.0 - 2 * self.margin)

        self.sound_tracks = [[0] * self.samples_per_section] * 3
        self.max_value = [0] * 3

        self.current_section = 0

        self.samples = []
        self.ac, self.avg, self.max_db = 0, 0, 0

    def run(self):
        self.record_mic(_adm=self.adm, duration=self.rec_duration)

    def record_mic(self, _adm: AudioDevice, chunk=1024, duration=-1):
        log_str = ''
        if self.is_sub:
            log_str = 'Sub '

        print_log("red", f"{log_str}Mic start recording..")

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

        while not self.done:

            if duration != -1:  # Loop if duration -1
                max_i = int(self.sample_rate / chunk * duration)
                if cur_i > max_i:
                    print('Record Mic Loop Finished' + f' duration: {duration}')
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
            time.sleep(0.02)
        self.done = False
        self.cur_db = 0
        self.draw_mic_threshold()   # clear threshold drawn to 0 level

        self.close_stream()
        print_log("red", f"{log_str}Mic Stop recording")

    def close_stream(self):
        # Terminate Stream
        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()

        # self.save_audio_file()

    def save_audio_file(self):
        s_file = wave.open("testing.wav", "wb")
        s_file.setnchannels(CHANNELS)
        s_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        s_file.setframerate(self.sample_rate)
        s_file.writeframes(b''.join(self.frames))
        s_file.close()

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
                print_log('warning', "mic device got changed")
                self.device_name = adm_mic.name
                self.done = True

    def draw_mic_threshold(self):
        if self.main_program:
            try:
                self.main_program.update_threshold_gui_signal.emit(self.cur_db, self.target_gui)
            except RuntimeError as e:
                print_log("warning", "no main program! maybe program ended", e)
                del self.main_program
                self.done = True


if __name__ == "__main__":
    adm = AudioDevice()
    # print(adm)
    adm.set_selected_mic("VoiceMeeter Aux Output")
    print(adm.selected_mic)

    mic_rec = MicRecorder()
    mic_rec.adm = adm
    mic_rec.rec_duration = -1.0

    mic_rec.start()
