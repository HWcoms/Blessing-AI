import os
import re

import pyaudio
import sounddevice as sd
from .device import *


class AudioDevice:
    device_list: list  # List of Device - List of Audio Devices

    default_mic: MicDevice  # MicDevice - Default Mic
    default_speaker: SpeakerDevice  # SpeakerDevice - Default Speaker

    selected_mic: MicDevice  # MicDevice - Selected Mic
    selected_speaker: SpeakerDevice  # SpeakerDevice - Selected Speaker

    mic_list: list  # List of MicDevice - List of Mics
    speaker_list: list  # SpeakerDevice - Selected Speaker

    def __init__(self, mode="normal"):
        self.device_list = []
        self.mic_list = []
        self.speaker_list = []
        self.get_all_device(mode)
        self.set_selected_device_to_default()
        self.init_selected_device()
        # self.get_spk_mic_list("compact")

    def get_all_device(self, mode):
        q_list = sd.query_devices()
        self.device_list.clear()

        str_list = repr(q_list).split('\n')
        first_seen_driver = None
        # Split List type with string condition
        for item in str_list:
            isDefault = False

            name_match = re.search(r'(\d+)(.*)', item)
            index_str = name_match.group(1)  # index
            remain_str = name_match.group(2)

            start_str = item[0]  # isDefault ['>' input, '<' output, ' ' not default]

            name_with_driver = ""

            inout_info = ""
            in_number = 0
            out_number = 0
            device: Device

            # split name, inout_info
            match = re.search(r'^(.*?)\s*\((\d+)\s*in,\s*(\d+)\s*out\)$', remain_str)
            if match:
                name_with_driver = match.group(1)  # name
                in_number = int(match.group(2))  # input_count
                out_number = int(match.group(3))  # output_count
            else:
                name_with_driver = ""
                in_number = 0
                out_number = 0
                print("Error [Audio Device Manager]: Could not find device information")

            if '>' in start_str or '<' in start_str:
                # default device"
                isDefault = True

            split_string = name_with_driver.split(',')
            split_string = [s.strip() for s in split_string]
            result_name = split_string[0]
            driver = split_string[1]

            if first_seen_driver is None:
                first_seen_driver = driver
            if mode == "compact" and driver != first_seen_driver:
                continue

            if in_number > 0:
                device = MicDevice(isDefault, int(index_str), result_name, in_number, out_number, driver)

                self.mic_list.append(device)
            else:
                device = SpeakerDevice(isDefault, int(index_str), result_name, in_number, out_number, driver)
                self.speaker_list.append(device)

            self.device_list.append(device)

    def set_selected_mic(self, name):
        for item in self.mic_list:
            if item.name == name:
                if self.selected_mic.input_count == 0:
                    print(
                        f"Error [Audio Device]: trying to select {self.selected_mic.input_count} input channel device to Mic")
                    return None

                self.selected_mic = item
                return item
        print(f"Error [Audio Device]: Could not find any Mic Device with given name: {name}")

    def set_selected_speaker(self, name):
        for item in self.speaker_list:
            if item.name == name:
                if self.selected_speaker.output_count == 0:
                    print(
                        f"Error [Audio Device]: trying to select {self.selected_speaker.output_count} output channel device to Speaker")
                    return None

                self.selected_speaker = item
                return item

        print(f"Error [Audio Device]: Could not find any Speaker Device with given index: {name}")

    def get_default_mic(self):
        for device_info in self.mic_list:
            if device_info.isDefault:
                return device_info

        print("Error [Audio Device Manager]: Could not find any default Mic")
        return None

    def get_default_speaker(self):
        for device_info in self.speaker_list:
            if device_info.isDefault:
                return device_info

        print("Error [Audio Device Manager]: Could not find any default Speaker")
        return None

    def set_selected_device_to_default(self):
        self.selected_mic = self.get_default_mic()
        self.selected_speaker = self.get_default_speaker()

    def init_selected_device(self):
        if self.selected_mic is None or self.selected_speaker is None:
            self.set_selected_device_to_default()

    # noinspection PyMethodMayBeStatic
    def get_mic_name_list(self):
        str_list = []
        for item in self.mic_list:
            str_list.append(item.name)

        return str_list

    def get_speaker_name_list(self):
        str_list = []
        for item in self.speaker_list:
            str_list.append(item.name)

        return str_list

    def __str__(self):
        # Test print
        result_str = 'mic_list:'

        for mic_info in self.mic_list:
            # print("*"+repr(mic_info))
            result_str = result_str + '\n' + repr(mic_info)

        result_str = result_str + '\n\n' + "speaker_list:"

        for speaker_info in self.speaker_list:
            # print(speaker_info)
            result_str = result_str + '\n' + repr(speaker_info)
        return result_str


if __name__ == '__main__':
    newAudDevice = AudioDevice("compact")

    # newAudDevice.init_selected_device()
    # newAudDevice.load_device_info()
    # newAudDevice.load_device_info()
    # newAudDevice.set_selected_mic()
    print(newAudDevice.get_speaker_name_list())
