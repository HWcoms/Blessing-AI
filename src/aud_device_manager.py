import os
import re

import pyaudio
import sounddevice as sd


class DeviceDict:
    def __init__(self):
        self.isDefault = False  # is Default device?
        self.index = 0  # index of audio device (sd.query_devices(index))
        self.name = ""  # audio device name
        self.inout_info = ""  # "input" or "ouput" device?
        self.input_count = 0  # number of inputs
        self.output_count = 0  # number of outputs
        self.driver = "MME"  # Sound Driver (MME, WDM, ASIO...)

    def print_dict(self):
        print(
            f"{self.isDefault} {self.index}: {self.name} [{self.driver} {self.inout_info}] ({self.input_count} In, {self.output_count} Out)")

    def __repr__(self):
        return f"{self.isDefault} {self.index}: {self.name} [{self.driver} {self.inout_info}] ({self.input_count} In, {self.output_count} Out)"

    def __str__(self):
        return f"{self.isDefault} {self.index}: {self.name} [{self.driver} {self.inout_info}] ({self.input_count} In, {self.output_count} Out)"


class AudioDevice:
    def __init__(self):
        self.device_list = []  # List of DeviceDict() - List of Audio Devices
        self.default_mic = None  # DeviceDict - Default Mic
        self.default_speaker = None  # DeviceDict - Default Speaker

        self.selected_mic = None  # DeviceDict - Selected Mic
        self.selected_speaker = None  # DeviceDict - Selected Speaker

        self.mic_list = []  # List of DeviceDict() - List of Mics
        self.speaker_list = []  # List of DeviceDict() - List of Speakers

    def get_all_device(self):
        q_list = sd.query_devices()
        self.device_list.clear()

        str_list = repr(q_list).split('\n')

        # Split List type with string condition
        for item in str_list:
            cur_dict = DeviceDict()
            isDefault = False

            name_match = re.search(r'(\d+)(.*)', item)
            index_str = name_match.group(1)  # index
            remain_str = name_match.group(2)

            start_str = item[0]  # isDefault ['>' input, '<' output, ' ' not default]

            name_with_driver = ""

            inout_info = ""
            in_number = 0
            out_number = 0

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

            if in_number > 0:
                inout_info = "input"
            else:
                inout_info = "output"

            split_string = name_with_driver.split(',')
            split_string = [s.strip() for s in split_string]
            result_name = split_string[0]
            driver = split_string[1]

            cur_dict.isDefault = isDefault
            cur_dict.index = int(index_str)
            cur_dict.name = result_name
            cur_dict.inout_info = inout_info
            cur_dict.input_count = in_number
            cur_dict.output_count = out_number
            cur_dict.driver = driver

            self.device_list.append(cur_dict)

        return self.device_list

    # load only devices type of drive at top
    def get_driver_device(self):
        all_device_list = self.get_all_device()

        new_device_list = []
        driver_name_ontop = all_device_list[0].driver

        for item in all_device_list:
            if item.driver == driver_name_ontop:
                new_device_list.append(item)

        self.device_list.clear()
        self.device_list = new_device_list

        return self.device_list

    # mode (    normal = load all devices, compact = get_driver_device()   )
    def load_device_info(self, mode="normal"):
        if len(self.device_list) == 0 and mode == "normal":
            self.get_all_device()
        elif len(self.device_list) == 0 and mode == "compact":
            self.get_driver_device()

        self.mic_list.clear()
        self.speaker_list.clear()

        mic_list = []
        speaker_list = []

        for dict_info in self.device_list:
            if dict_info.inout_info == "input":
                mic_list.append(dict_info)
            else:
                speaker_list.append(dict_info)

        self.mic_list, self.speaker_list = mic_list, speaker_list

    def set_selected_mic(self, index):
        self.selected_mic = sd.query_devices(device=index)
        if self.selected_mic['max_input_channels'] == 0:
            print(
                f"Error [Audio Device]: trying to select {self.selected_mic['max_input_channels']} input channel device to Mic")

    def set_selected_speaker(self, index):
        self.selected_speaker = sd.query_devices(device=index)
        if self.selected_mic['max_output_channels'] == 0:
            print(
                f"Error [Audio Device]: trying to select {self.selected_mic['max_output_channels']} output channel device to Speaker")

    def get_default_mic(self):
        if not self.device_list:
            device_list = self.get_all_device()

        for device_info in self.device_list:
            if device_info.isDefault and device_info.inout_info == "input":
                return device_info

        print("Error [Audio Device Manager]: Could not find any default Mic")
        return None

    def get_default_speaker(self):
        if not self.device_list:
            device_list = self.get_all_device()

        for device_info in self.device_list:
            if device_info.isDefault and device_info.inout_info == "output":
                return device_info

        print("Error [Audio Device Manager]: Could not find any default Speaker")
        return None

    def get_selected_mic(self, index):
        return self.selected_mic

    def get_selected_speaker(self, index):
        return self.selected_speaker

    def get_selected_devices(self):
        return self.selected_mic, self.selected_speaker

    def set_selected_device_to_default(self):
        self.selected_mic = self.get_default_mic()
        self.selected_speaker = self.get_default_speaker()

    def init_selected_device(self):
        if self.selected_mic is None or self.selected_speaker is None:
            self.set_selected_device_to_default()

    # noinspection PyMethodMayBeStatic
    def dictlist_to_strlist(self, dict_list):
        str_list = []
        for item in dict_list:
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
    newAudDevice = AudioDevice()

    # devices = newAudDevice.get_all_device()  # 1,6 default
    # newAudDevice.init_selected_device()
    newAudDevice.load_device_info()
    # newAudDevice.load_device_info()
    print(newAudDevice)
    # print(newAudDevice.get_default_mic())
