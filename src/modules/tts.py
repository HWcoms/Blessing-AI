from .thorsten import speak_de
from .voicevox import speak_jp
from .voicevox import speak_ko


# Text-to-Speech, feel free to add your own function or add more languages
def speak(sentence, language_code):
    # Japanese
    if language_code == 'ja':
        speak_jp(sentence)

    # French
    elif language_code == 'ko':
        # Write your own function to play your TTS audio
        speak_ko(sentence)

    # Chinese
    elif language_code == 'zh':
        pass

    # French
    elif language_code == 'fr':
        pass

    # Spanish
    elif language_code == 'es':
        pass

    # Russian
    elif language_code == 'ru':
        pass

    # German
    elif language_code == 'de':
        speak_de(sentence)
