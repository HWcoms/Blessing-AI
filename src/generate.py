# LanguageModel
from LangAIComm import generate_reply

# Load Voice Settings
from setting_info import SettingInfo


class Generator:
    def __init__(self):
        self.logging = True

    def generate(self, text, settings_list: list = None):
        from modules.translator import DoTranslate, detect_language
        log_str = ""
        # Load Program Settings
        tts_settings, character_settings, other_settings = None, None, None

        if settings_list is None or len(settings_list) == 0:
            log_str = "[VoiceTranslator.Generate]: No loaded settings exist! loading them now..."
            settings_list = SettingInfo.load_all_settings()

        else:
            log_str = "[VoiceTranslator.Generate]: Using loaded program settings from main GUI"

        tts_settings = settings_list[0]
        character_settings = settings_list[1]
        other_settings = settings_list[2]

        if self.logging:
            print(log_str)

        # language_code that AI Model using ("pygmalion should communicate with  english")
        ai_model_language = other_settings["ai_model_language"]

        bot_reply = ""

        if text:
            speech_lang = detect_language(text)
            translated_speech = DoTranslate(text, speech_lang, ai_model_language)

            if self.logging:
                # source_lang_name = languages.get(alpha2=speech_lang).name
                # print(f'{source_lang_name}: {eng_speech}')
                print(f'User: {translated_speech}')

            bot_reply = generate_reply(translated_speech, character_settings["character_name"])
            # bot_trans_speech = DoTranslate(bot_reply,'en',target_lang=tts_language)

            if self.logging:
                print(f'Bot: {bot_reply}')
        else:
            print('[VoiceTranslator.Generate] Error: text variable is None')
            return None  # failed

        if bot_reply == "":
            print('[VoiceTranslator.Generate] Error: text value is blank')
            return None  # failed

        # speak(bot_reply, tts_settings, other_settings)
        return bot_reply  # success
