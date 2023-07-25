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

# from modules.audio_to_device import play_voice
from discordbot import SendDiscordMessage, ExcuteDiscordWebhook

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
