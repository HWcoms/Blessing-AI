# LanguageModel
from LangAIComm import generate_reply

# Load Program Settings
from setting_info import SettingInfo
import json

from pathlib import Path

# Speak MoeGoe
from modules.translator import DoTranslate, detect_language
from modules.convert_roma_ja import english_to_katakana
from MoeGoe.Main import speech_text

from discordbot import SendDiscordMessage, ExcuteDiscordWebhook

# BotCommand
from modules.sing_command import BotCommand

# Play
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"  # hide pygame print
import pygame  # noqa: E402

tts_wav_path = Path(__file__).resolve().parent / r'audio\tts.wav'


class Generator:
    def __init__(self):
        super().__init__()
        self.logging = True

    def generate(self, text, settings_list: list = None):
        log_str = ""
        # Load Program Settings
        audio_settings, character_settings, prompt_settings, other_settings = None, None, None, None

        if settings_list is None or len(settings_list) == 0:
            log_str = "[Generator.generate]: No loaded settings exist! loading them now..."
            settings_list = SettingInfo.load_all_settings()

        else:
            log_str = "[Generator.generate]: Using loaded program settings from main GUI"

        audio_settings = settings_list[0]
        character_settings = settings_list[1]
        prompt_settings = settings_list[2]
        other_settings = settings_list[3]

        if self.logging:
            print("\033[34m" + log_str + "\033[0m")

        # language_code that AI Model using ("pygmalion should communicate with  english")
        ai_model_language = prompt_settings["ai_model_language"]

        bot_reply = ""

        if text:
            # SEND USER MESSAGE TO DISCORD
            #########################################
            # TODO: test user discord message is working
            # TODO: refactor your name, your image

            your_name = character_settings["your_name"]
            your_image = other_settings["discord_your_avatar"]
            your_json = {"character_name": your_name, "character_image": your_image}

            #########################################
            # SEND USER MESSAGE TO DISCORD

            token_id = prompt_settings["translator_api_id"]
            token_secret = prompt_settings["translator_api_secret"]

            speech_lang = detect_language(text, token_id, token_secret)
            translated_speech = DoTranslate(text, speech_lang, ai_model_language, token_id, token_secret)

            self.send_discord(translated_speech, ai_model_language, [token_id, token_secret], your_json, other_settings,
                              by_user=True)

            if self.logging:
                # source_lang_name = languages.get(alpha2=speech_lang).name
                # print(f'{source_lang_name}: {eng_speech}')
                print(f'User: {translated_speech}')

            bot_reply = generate_reply(translated_speech, character_settings["character_name"],
                                       prompt_settings["max_prompt_token"], prompt_settings["max_reply_token"])
            # bot_trans_speech = DoTranslate(bot_reply,'en',target_lang=tts_language)

            if self.logging:
                print(f'Bot: {bot_reply}')

        else:
            print("\031[31m" + '[Generator.Generate] Error: text variable is None' + "\033[0m")
            return None  # failed

        if bot_reply == "":
            print("\031[31m" + '[Generator.Generate] Error: text value is blank' + "\033[0m")
            return None  # failed

        self.send_discord(bot_reply, ai_model_language, [token_id, token_secret], character_settings, other_settings)

        return bot_reply  # success

    def send_discord(self, message, message_language, trans_token_list: list, profile_settings, other_settings,
                     by_user=False):
        log_str = "[Generator.send_discord]: "
        if self.logging:
            print("\033[34m" + log_str + "\033[32m")

        discord_print_language = other_settings["discord_print_language"]
        discord_bot = other_settings["discord_bot"]
        discord_webhook = other_settings["discord_webhook"]

        token_id = trans_token_list[0]
        token_secret = trans_token_list[1]

        if discord_bot or discord_webhook:
            # Do translate to discord_print_langage, if it's not same as language_code
            if message_language != discord_print_language:
                discord_sentence = DoTranslate(message, message_language, discord_print_language, token_id,
                                               token_secret)
            else:
                discord_sentence = message

            if discord_bot:
                # Using Discord Bot
                SendDiscordMessage(discord_sentence, other_settings["discord_bot_id"],
                                   other_settings["discord_bot_channel_id"])
            if discord_webhook:
                webhook_url = other_settings["discord_webhook_url"]

                if by_user:
                    webhook_username = other_settings["discord_your_name"]
                    webhook_avatar = other_settings["discord_your_avatar"]
                else:
                    webhook_username = other_settings["discord_webhook_username"]
                    webhook_avatar = other_settings["discord_webhook_avatar"]

                # IF THERE NAME OR AVATAR ARE EMPTY, GET INFORMATION FROM "character_settings.txt"
                if webhook_username == "" or webhook_username is None:
                    webhook_username = profile_settings["character_name"]
                if webhook_avatar == "" or webhook_avatar is None:
                    webhook_avatar = profile_settings["character_image"]

                print("webhook_username: ", webhook_username)
                print("webhook_avatar: ", webhook_avatar)

                ExcuteDiscordWebhook(discord_sentence, webhook_url, webhook_username, webhook_avatar)  # Using Webhook

        if self.logging:
            print("\033[0m")

    @staticmethod
    def split_botcommand(text):
        bot_cmd = BotCommand()

        command, value = bot_cmd.check_command(text)
        print(command, value)
        return command, value


class GeneratorTTS:
    def __init__(self):
        super().__init__()
        self.logging = True
        self.final_result_path = ""
        self.audio_dir = ""
        self.sounda = None

    def speak_tts(self, text, settings_list: list = None):
        # Load Program Settings
        if settings_list is None or len(settings_list) == 0:
            log_str = "[Generator.speak]: No loaded settings exist! loading them now..."
            settings_list = SettingInfo.load_all_settings()

        else:
            log_str = "[Generator.speak]: Using loaded program settings from main GUI"

        audio_settings = settings_list[0]
        character_settings = settings_list[1]
        prompt_settings = settings_list[2]
        other_settings = settings_list[3]

        if self.logging:
            print("\033[34m" + log_str + "\033[0m")

        tts_only = other_settings["tts_only"]
        text_lang = None

        token_id = prompt_settings["translator_api_id"]
        token_secret = prompt_settings["translator_api_secret"]

        if tts_only:
            text_lang = detect_language(text, token_id, token_secret)
        else:
            text_lang = prompt_settings[
                "ai_model_language"]  # language_code that AI Model using ("pygmalion should communicate with  english")
        print("tts lang: ", text, text_lang)
        if text:
            self.speak_moegoe(text, text_lang, [token_id, token_secret], audio_settings)
        else:
            print("\031[31m" + '[GeneratorTTS.Generate] Error: text variable is None' + "\033[0m")
            return None  # failed

    def speak_moegoe(self, sentence, sentence_lang, trans_token_list: list, audio_settings):
        log_str = "[GeneratorTTS.speak_moegoe]: "
        if self.logging:
            print("\033[34m" + log_str + "\033[32m")

        # spk_id = audio_settings["spk_index"]
        tts_character = audio_settings["tts_character"]
        language_code = audio_settings["tts_language"]
        voice_speed = audio_settings["voice_speed"]
        if voice_speed == 0:
            voice_speed = 0.01  # Avoid [ZeroDivisionError: float division by zero]

        voice_volume = 2.0
        voice_id = audio_settings["tts_voice_id"]

        token_id = trans_token_list[0]
        token_secret = trans_token_list[1]

        bot_trans_speech = DoTranslate(sentence, sentence_lang, language_code, token_id,
                                       token_secret)  # Translate reply
        if language_code == 'ja':
            bot_trans_speech = english_to_katakana(bot_trans_speech)  # romaji to japanese
        elif language_code == 'ko':
            bot_trans_speech = bot_trans_speech  # TODO: eng to korean
            voice_volume = voice_volume * 0.5

        if self.logging:
            print("\033[0m")

        print("\033[34m" + f"[GeneratorTTS.run]: start speech process! [\033[32m{sentence}\033[34m]" + "\033[0m")

        self.final_result_path = self.new_audio_path()  # assign output directory to self.final_result_path before run this method!

        # synthesize voice as wav file
        speech_text(tts_character, bot_trans_speech, language_code, voice_id, voice_volume, voice_speed,
                    out_path=self.final_result_path)

        print(
            "\033[34m" + f"[GeneratorTTS.speak_moegoe]: Created TTS as Wav File! [\033[32m{sentence}\033[34m] [{self.final_result_path}]" + "\033[0m")

    def play_by_bot(self, device_name, volume, quite_mode=False):
        if not quite_mode:
            print("\033[34m" + f"Playing TTS Audio From Speaker: \033[32m{device_name}\033[0m")

        if device_name is None or device_name == "":
            print("Error: No device name specified!: ", f"[{device_name}]")
        else:
            if not quite_mode:
                print("Using Audio Device (Speaker): ", f"[{device_name}]")

        if pygame.mixer.get_init():
            pygame.mixer.quit()

        pygame.mixer.init(devicename=device_name)
        self.sounda = pygame.mixer.Sound(self.final_result_path)
        self.sounda.set_volume(volume * 0.5)  # [0.0 ~ 2.0] to [0.0 ~ 1.0]
        self.sounda.play()
        pygame.time.wait(int(self.sounda.get_length() * 1000))

        if not quite_mode:
            print("speech done!")
        self.sounda.stop()

    def change_volume(self, volume):
        mixer = pygame.mixer.get_init()
        if mixer and self.sounda:
            # print("changing pygame volume!", volume, self.sounda)
            self.sounda.set_volume(volume * 0.5)

    def new_audio_path(self):
        import os

        num = 0
        while True:
            file_name = f'tts_{num}.wav'
            file_path = os.path.join(self.audio_dir, file_name)
            if not os.path.exists(file_path):
                return file_path
            num += 1
