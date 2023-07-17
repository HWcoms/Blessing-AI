# LanguageModel
from LangAIComm import generate_reply

# Load Program Settings
from setting_info import SettingInfo
import json

from pathlib import Path

# Speak MoeGoe
from modules.translator import DoTranslate
from modules.convert_roma_ja import english_to_katakana
from MoeGoe.Main import speech_text
from threading import Thread
# from modules.audio_to_device import play_voice
from discordbot import SendDiscordMessage, ExcuteDiscordWebhook

tts_wav_path = Path(__file__).resolve().parent / r'audio\tts.wav'


class Generator:
    def __init__(self):
        self.logging = True
        self.tts_wav_path = tts_wav_path

    def generate(self, text, settings_list: list = None):
        from modules.translator import DoTranslate, detect_language
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

            speech_lang = detect_language(text)
            translated_speech = DoTranslate(text, speech_lang, ai_model_language)

            self.send_discord(translated_speech, ai_model_language, your_json, other_settings, by_user=True)

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

        self.send_discord(bot_reply, ai_model_language, character_settings, other_settings)

        return bot_reply  # success

    def send_discord(self, message, message_language, profile_settings, other_settings, by_user=False):
        log_str = "[Generator.send_discord]: "
        if self.logging:
            print("\033[34m" + log_str + "\033[32m")

        discord_print_language = other_settings["discord_print_language"]
        discord_bot = other_settings["discord_bot"]
        discord_webhook = other_settings["discord_webhook"]

        if discord_bot or discord_webhook:
            # Do translate to discord_print_langage, if it's not same as language_code
            if message_language != discord_print_language:
                discord_sentence = DoTranslate(message, message_language, discord_print_language)
            else:
                discord_sentence = message

            if discord_bot:
                # Using Discord Bot
                SendDiscordMessage(discord_sentence, other_settings["discord_bot_id"], other_settings["discord_bot_channel_id"])
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

    def speak_tts(self, text, settings_list: list = None):
        # print("speak")

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

        if text:
            self.speak_moegoe(text, character_settings, audio_settings, prompt_settings)
        else:
            print("\031[31m" + '[Generator.Generate] Error: text variable is None' + "\033[0m")
            return None  # failed

    def speak_moegoe(self, sentence, character_settings, audio_settings, prompt_settings):
        log_str = "[Generator.speak_moegoe]: "
        if self.logging:
            print("\033[34m" + log_str + "\033[32m")

        spk_id = audio_settings["spk_index"]
        language_code = audio_settings["tts_language"]
        voice_volume = audio_settings["voice_volume"]
        voice_id = audio_settings["voice_id"]
        ai_model_language = prompt_settings[
            "ai_model_language"]  # language_code that AI Model using ("pygmalion should communicate with  english")

        bot_trans_speech = DoTranslate(sentence, ai_model_language, language_code)  # Translate reply
        if language_code == 'ja':
            bot_trans_speech = english_to_katakana(bot_trans_speech)  # romaji to japanese
        elif language_code == 'ko':
            bot_trans_speech = bot_trans_speech  # TODO: eng to korean
            voice_volume = voice_volume * 0.5

        # synthesize voice as wav file
        speech_text(audio_settings["tts_character_name"], bot_trans_speech, language_code, voice_id, voice_volume)

        if self.logging:
            print("\033[0m")

        # play voice to app mic input and speakers/headphones
        threads = [Thread(target=self.play_voice, args=[spk_id])]
        # threads = [Thread(target=play_voice, args=[APP_INPUT_ID]), Thread(target=play_voice, args=[SPEAKERS_INPUT_ID])]

        [t.start() for t in threads]
        [t.join() for t in threads]

    def play_voice(self, device_id):
        import sounddevice as sd
        import soundfile as sf

        s_q = sd.query_devices()
        device_name = f"""{s_q[device_id]["name"]}"""
        data, fs = sf.read(self.tts_wav_path, dtype='float32')
        print("\033[34m" + f"Playing TTS Audio From Speaker: \033[32m{device_name}\033[0m")

        sd.play(data, fs, device=device_id)
        sd.wait()
