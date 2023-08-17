import os
import pyaudio

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"   # hide pygame print

import pygame   # noqa: E402
import pygame._sdl2 as sdl2_audio  # noqa

if __name__ == '__main__' or "modules" not in __name__:
    from device import *
else:
    from .device import *


class AudioDevice:
    device_list: list  # List of Device - List of Audio Devices

    default_mic: MicDevice  # MicDevice - Default Mic
    default_speaker: SpeakerDevice  # SpeakerDevice - Default Speaker

    selected_mic: MicDevice  # MicDevice - Selected Mic
    selected_speaker: SpeakerDevice  # SpeakerDevice - Selected Speaker

    mic_list: list  # List of MicDevice - List of Mics
    speaker_list: list  # SpeakerDevice - Selected Speaker

    def __init__(self):
        self.device_list = []
        self.mic_list = []
        self.speaker_list = []
        self.selected_speaker = SpeakerDevice()
        self.selected_mic = MicDevice()
        self.get_all_device()
        # self.set_selected_device_to_default()
        # self.get_spk_mic_list("compact")

    def clear_all_lists(self):
        self.device_list.clear()
        self.mic_list.clear()
        self.speaker_list.clear()

    def get_all_device(self):
        self.clear_all_lists()

        mic_list = self.get_devices(capture_devices=True)
        spk_list = self.get_devices(capture_devices=False)

        p = pyaudio.PyAudio()
        d_mic = p.get_default_input_device_info()
        d_spk = p.get_default_output_device_info()

        for i, mic in enumerate(mic_list):
            isDef = False
            if d_mic['name'] in mic:
                # print(f"default mic: {mic}")
                isDef = True

            _dvc = MicDevice(isDef, i, mic, 2, 0, "SDL2")

            if isDef:
                self.default_mic = _dvc

            self.mic_list.append(_dvc)
            self.device_list.append(_dvc)

        for i, spk in enumerate(spk_list):
            isDef = False
            if d_spk['name'] in spk:
                # print(f"default spk: {spk}")
                isDef = True

            _dvc = SpeakerDevice(isDef, i, spk, 0, 2, "SDL2")

            if isDef:
                self.default_speaker = _dvc

            self.speaker_list.append(_dvc)
            self.device_list.append(_dvc)

    def set_selected_mic_index(self, index):
        self.selected_mic = self.mic_list[index]

    def set_selected_speaker_index(self, index):
        self.selected_speaker = self.speaker_list[index]

    def set_selected_mic(self, name):
        for item in self.mic_list:
            if name in item.name:
                if item.input_count == 0:
                    print(
                        f"\033[31mError [Audio Device]: trying to select {self.selected_mic.input_count} input channel device to Mic: {item.name}\033[0m")
                    return None

                self.selected_mic = item
                return item
        print(f"\033[31mError [Audio Device]: Could not find any Mic Device with given name: {name}\033[0m")

    def set_selected_speaker(self, name):
        for item in self.speaker_list:
            if name in item.name:
                if item.output_count == 0:
                    print(
                        f"\033[31mError [Audio Device]: trying to select {self.selected_speaker.output_count} output channel device to Speaker: {item.name}\033[0m")
                    return None

                self.selected_speaker = item
                return item

        print(f"\033[31mError [Audio Device]: Could not find any Speaker Device with given index: {name}\033[0m")

    def get_default_mic(self):
        for device_info in self.mic_list:
            if device_info.isDefault:
                return device_info

        print("\033[31mError [Audio Device Manager]: Could not find any default Mic\033[0m")
        return None

    def get_default_speaker(self):
        for device_info in self.speaker_list:
            if device_info.isDefault:
                return device_info

        print("\033[31mError [Audio Device Manager]: Could not find any default Speaker\033[0m")
        return None

    def set_selected_device_to_default(self):
        self.selected_mic = self.get_default_mic()
        self.selected_speaker = self.get_default_speaker()

    # noinspection PyMethodMayBeStatic
    def get_devices(self, capture_devices: bool = False):
        init_by_me = not pygame.mixer.get_init()
        if init_by_me:
            pygame.mixer.init()
        devices = tuple(sdl2_audio.get_audio_device_names(capture_devices))
        if init_by_me:
            pygame.mixer.quit()
        return devices

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
        _line_str = '\033[33m================================================================\033[0m'
        _split_str = '\033[34m----------------------------------------------------------------\033[0m'
        # Test print
        result_str = f'{_line_str}\n'
        result_str += 'mic_list:'

        for mic_info in self.mic_list:
            # print("*"+repr(mic_info))
            result_str = result_str + '\n' + repr(mic_info)

        result_str = result_str + f'\n{_split_str}\n' + "speaker_list:"

        for speaker_info in self.speaker_list:
            # print(speaker_info)
            result_str = result_str + '\n' + repr(speaker_info)

        result_str += f'\n{_line_str}'
        return result_str


if __name__ == '__main__':
    newAudDevice = AudioDevice()
    newAudDevice.set_selected_speaker("VoiceMeeter")
    print(newAudDevice)
    print(newAudDevice.selected_speaker)
    # newAudDevice.get_all_device()

    # newAudDevice.init_selected_device()
    # newAudDevice.load_device_info()
    # newAudDevice.load_device_info()
    # newAudDevice.set_selected_mic()
    # print(newAudDevice.get_speaker_name_list())
