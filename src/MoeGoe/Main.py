import os
import re
import sys
from pathlib import Path
import glob

from scipy.io.wavfile import write
from torch import no_grad, LongTensor

import sys
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'modules'))

if __name__ != "__main__":
    from . import commons
    from . import utils
    from .mel_processing import spectrogram_torch
    from .models import SynthesizerTrn
    from .text import text_to_sequence, _clean_text
    from manage_folder import tts_char_dir
else:
    import commons
    import utils
    from mel_processing import spectrogram_torch
    # from models import SynthesizerTrn
    # from text import text_to_sequence, _clean_text
    from manage_folder import tts_char_dir

# import logging
# logging.getLogger('numba').setLevel(logging.WARNING)

language_marks = {
    "Japanese": "",
    "日本語": "[JA]",
    "简体中文": "[ZH]",
    "English": "[EN]",
    "한국어": "[KO]",
    "Mix": "",
}

language = "日本語"

out_file_path = "models\demo.wav"


# Pre-define variables
# hps_ms = None
# n_speakers = None
# n_symbols = None
# speakers = None
# use_f0 = None
# emotion_embedding = None
# net_g_ms = None


def ex_print(text, escape=False):
    if escape:
        print(text.encode('unicode_escape').decode())
    else:
        print(text)


def get_text(text, hps, cleaned=False):
    if cleaned:
        text_norm = text_to_sequence(text, hps.symbols, [])
    else:
        text_norm = text_to_sequence(text, hps.symbols, hps.data.text_cleaners)
    if hps.data.add_blank:
        text_norm = commons.intersperse(text_norm, 0)
    text_norm = LongTensor(text_norm)
    return text_norm


def ask_if_continue():
    while True:
        answer = input('Continue? (y/n): ')
        if answer == 'y':
            break
        elif answer == 'n':
            sys.exit(0)


def print_speakers(speakers, escape=False):
    if len(speakers) > 100:
        return
    print('ID\tSpeaker')
    for id, name in enumerate(speakers):
        ex_print(str(id) + '\t' + name, escape)


def get_speaker_id(message):
    speaker_id = input(message)
    try:
        speaker_id = int(speaker_id)
    except:
        print(str(speaker_id) + ' is not a valid ID!')
        sys.exit(1)
    return speaker_id


def get_label_value(text, label, default, warning_name='value'):
    value = re.search(rf'\[{label}=(.+?)\]', text)
    if value:
        try:
            text = re.sub(rf'\[{label}=(.+?)\]', '', text, 1)
            value = float(value.group(1))
        except:
            print(f'Invalid {warning_name}!')
            sys.exit(1)
    else:
        value = default
    return value, text


def get_label(text, label):
    if f'[{label}]' in text:
        return True, text.replace(f'[{label}]', '')
    else:
        return False, text


"""
def voice_conversion():
    audio_path = input('Path of an audio file to convert:\n')
    print_speakers(speakers)
    audio = utils.load_audio_to_torch(
        audio_path, hps_ms.data.sampling_rate)

    originnal_id = get_speaker_id('Original speaker ID: ')
    target_id = get_speaker_id('Target speaker ID: ')
    out_path = input('Path to save: ')

    y = audio.unsqueeze(0)

    spec = spectrogram_torch(y, hps_ms.data.filter_length,
                             hps_ms.data.sampling_rate, hps_ms.data.hop_length, hps_ms.data.win_length,
                             center=False)
    spec_lengths = LongTensor([spec.size(-1)])
    sid_src = LongTensor([originnal_id])

    with no_grad():
        sid_tgt = LongTensor([target_id])
        audio = net_g_ms.voice_conversion(spec, spec_lengths, sid_src=sid_src, sid_tgt=sid_tgt)[
            0][0, 0].data.cpu().float().numpy()
    return audio, out_path
"""


def speech_text(character_name, msg, lang, spk_id, audio_volume, voice_speed, out_path=out_file_path):
    # Load model path
    hps_ms, n_speakers, n_symbols, speakers, use_f0, emotion_embedding, net_g_ms = load_model(character_name)
    # print(hps_ms['data']['text_cleaners'][0])
    # TODO: auto language_mark if text_cleaners is for multiple language
    if lang == 'ja':
        msg = language_marks[language] + msg + language_marks[language]
    elif lang == 'ko' and hps_ms['data']['text_cleaners'][0] != 'korean_cleaners':
        msg = language_marks["한국어"] + msg + language_marks["한국어"]

    if n_symbols != 0:
        if not emotion_embedding:
            while True:
                text = msg

                if text == '[ADVANCED]':
                    text = input('Raw text:')
                    print('Cleaned text is:')
                    ex_print(_clean_text(
                        text, hps_ms.data.text_cleaners), escape)
                    continue

                # length_scale, text = get_label_value(
                #     text, 'LENGTH', 1, 'length scale')
                # noise_scale, text = get_label_value(
                #     text, 'NOISE', 0.667, 'noise scale')
                # noise_scale_w, text = get_label_value(
                #     text, 'NOISEW', 0.8, 'deviation of noise')
                cleaned, text = get_label(text, 'CLEANED')

                length_scale = 1.0 / voice_speed
                noise_scale = 0.667
                noise_scale_w = 0.8
                # cleaned
                stn_tst = get_text(text, hps_ms, cleaned=cleaned)

                # print_speakers(speakers[0], escape)
                # speaker_id = get_speaker_id('Speaker ID: ')
                speaker_id = spk_id

                with no_grad():
                    x_tst = stn_tst.unsqueeze(0)
                    x_tst_lengths = LongTensor([stn_tst.size(0)])
                    sid = LongTensor([speaker_id])
                    audio = net_g_ms.infer(x_tst, x_tst_lengths, sid=sid, noise_scale=noise_scale,
                                           noise_scale_w=noise_scale_w, length_scale=length_scale)[0][
                        0, 0].data.cpu().float().numpy()

                audio = audio_volume * audio
                write(out_path, hps_ms.data.sampling_rate, audio)
                # print('Successfully saved!')
                # ask_if_continue()
                return


def load_model(character_name):
    model_folder = tts_char_dir

    voice_folder = None
    model_file = None
    config_file = None

    hps_load = None
    n_speakers_load = None
    n_symbols_load = None
    speakers_load = None
    use_f0_load = None
    emotion_embedding_load = None
    net_g_ms_load = None

    # find all character voice model paths
    for fname in os.listdir(model_folder):
        path = os.path.join(model_folder, fname)
        if os.path.isdir(path):
            # print(fname)
            if character_name.lower() in fname.lower():
                voice_folder = path
                print(f"found character voice: {fname}")

    if voice_folder:
        # Find *.pth, *.JSON files
        model_file = os.path.join(voice_folder, "*.pth")
        config_file = os.path.join(voice_folder, "*.json")

        model_file = glob.glob(model_file)[0]
        config_file = glob.glob(config_file)[0]

        print(f"moegoe model file: {model_file}")
        print(f"moegoe config file: {config_file}")

        # print("tts model loaded: ", model_file)

        hps_load = utils.get_hparams_from_file(config_file)
        n_speakers_load = hps_load.data.n_speakers if 'n_speakers' in hps_load.data.keys() else 0
        n_symbols_load = len(hps_load.symbols) if 'symbols' in hps_load.keys() else 0
        speakers_load = hps_load.speakers if 'speakers' in hps_load.keys() else ['0']
        use_f0_load = hps_load.data.use_f0 if 'use_f0' in hps_load.data.keys() else False
        emotion_embedding_load = hps_load.data.emotion_embedding if 'emotion_embedding' in hps_load.data.keys() else False

        net_g_ms_load = SynthesizerTrn(
            n_symbols_load,
            hps_load.data.filter_length // 2 + 1,
            hps_load.train.segment_size // hps_load.data.hop_length,
            n_speakers=n_speakers_load,
            emotion_embedding=emotion_embedding_load,
            **hps_load.model)
        _ = net_g_ms_load.eval()
        utils.load_checkpoint(model_file, net_g_ms_load)

    else:
        print("Error: Could not found tts folder")

    return hps_load, n_speakers_load, n_symbols_load, speakers_load, use_f0_load, emotion_embedding_load, net_g_ms_load


if __name__ == 'MoeGoe.Main':
    print()
    print("moe goe loaded by other")
    print()

    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

    # code_path = os.path.dirname(os.path.realpath(__file__))
    out_file_path = Path(__file__).resolve().parent.parent / r'audio\tts.wav'

    #
    # hps_ms = utils.get_hparams_from_file(config)
    # n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    # n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
    # speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
    # use_f0 = hps_ms.data.use_f0 if 'use_f0' in hps_ms.data.keys() else False
    # emotion_embedding = hps_ms.data.emotion_embedding if 'emotion_embedding' in hps_ms.data.keys() else False
    #
    # net_g_ms = SynthesizerTrn(
    #     n_symbols,
    #     hps_ms.data.filter_length // 2 + 1,
    #     hps_ms.train.segment_size // hps_ms.data.hop_length,
    #     n_speakers=n_speakers,
    #     emotion_embedding=emotion_embedding,
    #     **hps_ms.model)
    # _ = net_g_ms.eval()
    # utils.load_checkpoint(model, net_g_ms)

if __name__ == '__main__':
    if '--escape' in sys.argv:
        escape = True
    else:
        escape = False

    print("this is __main__")

    # print(load_model("Kamisato Ayaka"))   # test loading pth, json

    # hps_ms = utils.get_hparams_from_file(config)
    # n_speakers = hps_ms.data.n_speakers if 'n_speakers' in hps_ms.data.keys() else 0
    # n_symbols = len(hps_ms.symbols) if 'symbols' in hps_ms.keys() else 0
    # speakers = hps_ms.speakers if 'speakers' in hps_ms.keys() else ['0']
    # use_f0 = hps_ms.data.use_f0 if 'use_f0' in hps_ms.data.keys() else False
    # emotion_embedding = hps_ms.data.emotion_embedding if 'emotion_embedding' in hps_ms.data.keys() else False
    #
    # net_g_ms = SynthesizerTrn(
    #     n_symbols,
    #     hps_ms.data.filter_length // 2 + 1,
    #     hps_ms.train.segment_size // hps_ms.data.hop_length,
    #     n_speakers=n_speakers,
    #     emotion_embedding=emotion_embedding,
    #     **hps_ms.model)
    # _ = net_g_ms.eval()
    # utils.load_checkpoint(model, net_g_ms)

    # speech_text("ショッピングなど多数のサービスを展開。")
