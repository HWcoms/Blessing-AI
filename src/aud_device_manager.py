import os
import pyaudio
import sounddevice as sd


class AudioDevice:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.device_list = sd.DeviceList()
        self.default_mic = None
        self.default_speaker = None

        self.selected_mic = None
        self.selected_speaker = None

    def get_all_device(self):
        self.device_list = sd.query_devices()

        return self.device_list

    def set_selected_mic(self, index):
        self.selected_mic = sd.query_devices(device=index)
        if self.selected_mic['max_input_channels'] == 0:
            print(f"Error [Audio Device]: trying to select {self.selected_mic['max_input_channels']} input channel device to Mic")

    def set_selected_speaker(self, index):
        self.selected_speaker = sd.query_devices(device=index)
        if self.selected_mic['max_output_channels'] == 0:
            print(f"Error [Audio Device]: trying to select {self.selected_mic['max_output_channels']} output channel device to Speaker")

    def get_default_mic(self):
        self.default_mic = sd.query_devices(kind="input")
        return self.default_mic,

    def get_default_speaker(self):
        self.default_speaker = sd.query_devices(kind="output")
        return self.default_speaker

    def get_selected_mic(self, index):
        return self.selected_mic

    def get_selected_speaker(self, index):
        return self.selected_speaker

    def get_selected_device(self):
        return self.selected_mic, self.selected_speaker

    def set_selected_device_to_default(self):
        self.selected_mic = self.get_default_mic()
        self.selected_speaker = self.get_default_speaker()

    def init_selected_device(self):
        if self.selected_mic is None:
            self.selected_mic = self.get_default_mic()
        if self.selected_speaker is None:
            self.selected_speaker = self.get_default_speaker()


if __name__ == '__main__':
    newAudDevice = AudioDevice()

    devices = newAudDevice.get_all_device()  # 1,6 default
    newAudDevice.init_selected_device()
    print(devices)
