import gc
import glob
import json
import os
import re
from contextlib import suppress

import yt_dlp
from youtube_search import YoutubeSearch
from urllib.parse import urlparse, parse_qs

# demucs
from rvc_modules.mdx import run_mdx
from rvc_modules.download_rvc_models import download_required_models

# rvc
from rvc_modules.rvc import Config, load_hubert, get_vc, rvc_infer

# audio FX
from pedalboard import Pedalboard, Reverb, Compressor, HighpassFilter
from pedalboard.io import AudioFile
from pydub import AudioSegment

root_folder = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

rvc_required_dir = os.path.join(root_folder, 'src', 'Models', 'rvc_model')  # MDX, RVC Pretrained models
rvc_voice_dir = os.path.join(root_folder, 'src', 'Models', 'rvc_voice')  # Voice Models (pth, index)

rvc_cache_dir = os.path.join(root_folder, 'cache', 'rvc')
process_dir = os.path.join(rvc_cache_dir, "song_process")

# CHECK AUDIO CACHE FOLDER
if not os.path.exists(rvc_cache_dir):
    os.makedirs(rvc_cache_dir)
    print("\033[34m" + f"[sing_command]: Created audio cache folder! \033[33m[{rvc_cache_dir}]" + "\033[0m")


# region [COMMANDS]
############################################################################
def check_command(text):
    command_prefixes = ['!sing', '!draw', '!emote']
    command_prefix = None
    command_value = None

    text_parts = text.split()
    for i, part in enumerate(text_parts):
        if part in command_prefixes:
            command_prefix = part
            command_value = ' '.join(text_parts[i + 1:]).strip()
            break

    if command_prefix is None:
        print("\033[31m" + f"No command found in text: {text}" + "\033[0m")
        return command_prefix, command_value

    return command_prefix, command_value


def do_sing(char_name, song_name, pitch=0):  # normalize og vocal -> get pitch that similar with inference
    dl_url, video_id = search_audio(song_name)

    output_folder = os.path.join(process_dir, video_id)
    rvc_process_dict = check_rvc_process_exist(char_name, pitch, output_folder)

    vocals_path, instrumentals_path, backup_vocals_path, main_vocals_path, main_vocals_dereverb_path = None, None, None, None, None
    rvc_result_path, ai_vocals_mixed_path, final_cover_path = None, None, None
    # check if there's final prefix
    if 'final' in rvc_process_dict:
        # print("RVC result audio file name: ", rvc_process_dict['final'])
        final_cover_path = rvc_process_dict['final']
    else:
        if 'inst' not in rvc_process_dict:
            dl_audio = download_audio(dl_url, video_id)
            vocals_path, instrumentals_path = seperate_song(dl_audio, video_id, 'vocalninst')

        if ('main_vocal' not in rvc_process_dict) or ('backup_vocal' not in rvc_process_dict):
            # Check og vocals file
            if not vocals_path:
                if 'vocals' not in rvc_process_dict:
                    dl_audio = download_audio(dl_url, video_id)
                    rvc_process_dict['vocals'] = seperate_song(dl_audio, video_id, 'vocalninst')
                vocals_path = rvc_process_dict['vocals']

            backup_vocals_path, main_vocals_path = seperate_song(vocals_path, video_id, 'backup')

        if 'dereverb' not in rvc_process_dict:
            if not main_vocals_path:
                main_vocals_path = rvc_process_dict['main_vocal']
            main_vocals_dereverb_path = seperate_song(main_vocals_path, video_id, 'dereverb')

        if 'rvc' not in rvc_process_dict:
            if main_vocals_dereverb_path is None:
                main_vocals_dereverb_path = rvc_process_dict['dereverb']

            # rvc process
            rvc_result_path = voice_change(char_name, main_vocals_dereverb_path, output_folder, pitch)

        if 'fx' not in rvc_process_dict:
            if rvc_result_path is None:
                rvc_result_path = rvc_process_dict['rvc']

            ai_vocals_mixed_path = add_audio_fx(rvc_result_path,
                                                reverb_rm_size=0.15, reverb_wet=0.2,
                                                reverb_dry=0.8, reverb_damping=0.7)

    if backup_vocals_path is None:
        backup_vocals_path = rvc_process_dict['backup_vocal']
    if instrumentals_path is None:
        instrumentals_path = rvc_process_dict['inst']
    if ai_vocals_mixed_path is None:
        ai_vocals_mixed_path = rvc_process_dict['fx']

    audios_to_mix = [ai_vocals_mixed_path, backup_vocals_path, instrumentals_path]
    audio_mix_settings = [0, 0, 0]  # Main Vocal, Backup Vocal, Inst Volume

    # Fix final filename
    final_cover_prefix = instrumentals_path.replace("_Instrumental.wav", ".wav")
    final_cover_path = os.path.join(output_folder,
                                  f'{os.path.splitext(os.path.basename(final_cover_prefix))[0]} ({char_name} Ver).mp3')

    # Merge All Audios
    merge_audio(audios_to_mix, final_cover_path, audio_mix_settings)

    # if not keep_files:
    #     display_progress('[~] Removing intermediate audio files...', 0.95, is_webui, progress)
    #     intermediate_files = [vocals_path, main_vocals_path, ai_vocals_mixed_path]
    #     for file in intermediate_files:
    #         if file and os.path.exists(file):
    #             os.remove(file)

    print(final_cover_path)
    # play_audio(result_rvc)
    return final_cover_path


############################################################################
# endregion [COMMANDS]

# region [Youtube DL]
############################################################################
def search_audio(song_name, top_view=False):
    search = YoutubeSearch(song_name, max_results=5).to_dict()

    if top_view:
        # Get highest viewed video from list
        top_vid = get_highest_view(search)
    else:
        # Get first video from list
        top_vid = search[0]
    dl_url = 'https://www.youtube.com' + top_vid['url_suffix']
    print("\033[34m" + f"[sing_command.search_audio]: \033[33mfound video on Youtube [{dl_url}]" + "\033[0m")

    video_id = get_youtube_video_id(dl_url)

    # print(f"[sing_command.search_audio]: downloaded YouTube video to audio in [{dl_audio}]")

    return dl_url, video_id
    # return None


def get_highest_view(video_list):
    if len(video_list) == 0:
        return None
    top_video = video_list[0]

    for video in video_list:
        top_view = get_view_count_from_str(top_video['views'])
        cur_view = get_view_count_from_str(video['views'])

        if top_view < cur_view:
            top_video = video
    return top_video


def get_view_count_from_str(view_str):
    numbers = re.findall(r'\d+', view_str)
    num_list = [int(number) for number in numbers]

    merged_string = ''.join(str(number) for number in num_list)
    merged_number = int(merged_string)
    return merged_number


def get_youtube_video_id(url, ignore_playlist=True):
    """
    Examples:
    http://youtu.be/SA2iWivDJiE
    http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    http://www.youtube.com/embed/SA2iWivDJiE
    http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        if query.path[1:] == 'watch':
            return query.query[2:]
        return query.path[1:]

    if query.hostname in {'www.youtube.com', 'youtube.com', 'music.youtube.com'}:
        if not ignore_playlist:
            # use case: get playlist id not current video in playlist
            with suppress(KeyError):
                return parse_qs(query.query)['list'][0]  # noqa
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]  # noqa
        if query.path[:7] == '/watch/':
            return query.path.split('/')[1]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]

    # returns None for invalid YouTube url
    return None


def download_audio(link, out_dir_name):
    prefix_name = None  # noqa

    if not out_dir_name:
        raise RuntimeError("out_path is None!")

    ydl_opts = {
        'format': 'bestaudio',
        'outtmpl': '%(title)s.%(ext)s',
        'nocheckcertificate': True,
        'ignoreerrors': True,
        'no_warnings': True,
        'quiet': True,
        'extractaudio': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl_info = ydl.extract_info(link, download=False)
        download_name = ydl.prepare_filename(ydl_info)

        # print(download_name)

        prefix_name, ext = os.path.splitext(download_name)
        # print(ext)
        if ".mp3" in ext:
            prefix_name = download_name
        else:
            prefix_name += ".mp3"

        video_id_dir = os.path.join(process_dir, out_dir_name)

        # CHECK FILE EXIST
        if check_file_exist(prefix_name, video_id_dir, "[Mp3 Found]"):
            return prefix_name

        if not os.path.exists(video_id_dir):
            os.makedirs(video_id_dir)
            print(
                "\033[34m" + f"[sing_command.download_audio]: Created audio folder for yt-download! \033[33m[{video_id_dir}]" + "\033[0m")

    if not check_file_exist(download_name, video_id_dir, "[Wav Found]"):
        ydl.download([link])
        print("downloaded video! - ", prefix_name, "    ")

        os.renames(os.path.join(download_name), os.path.join(video_id_dir, download_name))

    return download_name


############################################################################
# endregion [Youtube DL]


# region [UTILS]
############################################################################
def check_file_exist(name, custom_dir, custom_log=""):
    file_path = os.path.join(custom_dir, name)

    if os.path.exists(file_path):
        print(
            "\033[34m" f"[sing_command.check_file_exist]: \033[33m{custom_log} {name} - file is aleardy exist (skip process)" + "\033[0m")
        return True
    else:
        return False


def check_rvc_process_exist(char_name, pitch, work_dir, custom_log=""):
    result_dict = {}

    # Check Final (merged)
    prefix = "Ver*).mp3"
    for filename in glob.glob(os.path.join(work_dir, f'*{char_name}*{prefix}*')):
        print(f"Final Cover Music is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found Final Result
        result_dict['final'] = filename
        break

    # Check FX process
    prefix = "_mixed.wav"
    for filename in glob.glob(os.path.join(work_dir, f'*_{char_name}_p*{pitch}_i*{prefix}*')):
        print(f"Audio FX Result is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found Final Result
        result_dict['fx'] = filename
        break

    # Check RVC process
    prefix = ".wav"
    for filename in glob.glob(os.path.join(work_dir, f'*_{char_name}_p*{pitch}_i*{prefix}*')):
        print(f"RVC Result is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found Final Result
        result_dict['rvc'] = filename
        break

    # Check DeReverb
    prefix = "_DeReverb.wav"
    for filename in glob.glob(os.path.join(work_dir, f'*{prefix}*')):
        print(custom_log + f"DeReverb Result is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found DeReverb Result
        result_dict['dereverb'] = filename
        break

    # Check Main_Vocal, Backup_Vocal
    prefix = "_Vocals_Main.wav"
    for filename in glob.glob(os.path.join(work_dir, f'*{prefix}*')):
        print(custom_log + f"Main Vocal Result is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found _Vocals_Main Result
        result_dict['main_vocal'] = filename
        break
    prefix = "_Vocals_Backup.wav"
    for filename in glob.glob(os.path.join(work_dir, f'*{prefix}*')):
        print(custom_log + f"Backup Vocal Result is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found _Vocals_Backup Result
        result_dict['backup_vocal'] = filename
        break
    # Check Vocal, Inst
    prefix = "_Instrumental.wav"
    for filename in glob.glob(os.path.join(work_dir, f'*{prefix}*')):
        print(custom_log + f"Instrumental Result is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found _Instrumental Result
        result_dict['inst'] = filename
        break
    prefix = "_Vocals.wav"
    for filename in glob.glob(os.path.join(work_dir, f'*{prefix}*')):
        print(custom_log + f"Vocals Result is Aleardy exist!: [\033[33m{filename}\033[0m]")
        # Found _Vocals Result
        result_dict['vocals'] = filename
        break

    return result_dict


############################################################################
# endregion [UTILS]

# region [RVC]
############################################################################
def get_rvc_model(voice_model):
    rvc_model_filename, rvc_index_filename = None, None
    model_dir = os.path.join(rvc_voice_dir, voice_model)
    for file in os.listdir(model_dir):
        ext = os.path.splitext(file)[1]
        if ext == '.pth':
            rvc_model_filename = file
        if ext == '.index':
            rvc_index_filename = file

    if rvc_model_filename is None:
        error_msg = f'No model file exists in {model_dir}.'
        raise ValueError(error_msg)

    return os.path.join(model_dir, rvc_model_filename), os.path.join(model_dir,
                                                                     rvc_index_filename) if rvc_index_filename else ''


def voice_change(voice_model, vocals_path, output_path, pitch_change,
                 index_rate=0.5):  # Control how much of the AI's accent to leave in the vocals. 0 <= INDEX_RATE <= 1.
    rvc_model_path, rvc_index_path = get_rvc_model(voice_model)
    device = 'cuda:0'
    config = Config(device, True)
    # print(config)
    hubert_model = load_hubert(device, config.is_half, os.path.join(rvc_required_dir, 'hubert_base.pt'))
    cpt, version, net_g, tgt_sr, vc = get_vc(device, config.is_half, config, rvc_model_path)

    # print(output_path)
    # convert main vocals
    ai_vocals_filename = vocals_path.replace("_Vocals_Main_DeReverb.wav", ".wav")  # _Vocals_Main_DeReverb.wav -> .wav
    ai_vocals_path = os.path.join(output_path,
                                  f'{os.path.splitext(os.path.basename(ai_vocals_filename))[0]}_{voice_model}_p{pitch_change}_i{index_rate}.wav')

    rvc_infer(rvc_index_path, index_rate, vocals_path, ai_vocals_path, pitch_change, cpt, version, net_g, tgt_sr, vc,
              hubert_model)
    del hubert_model, cpt
    gc.collect()

    print("\033[34m[sing_command.voice_change]: \033[32mRVC Vocal Process Done!\033[0m")

    return ai_vocals_path


############################################################################
# endregion [RVC]

# region [SoundFX]
############################################################################
def seperate_song(in_file, song_id, mode,
                  keep_orig=True):  # mode=["vocalninst", "backup", "dereverb"] # keep_org -> keep input files
    song_input = os.path.join(process_dir, song_id, in_file)  # og song file
    song_output_dir = os.path.join(process_dir, song_id)  # out file dir

    with open(os.path.join(rvc_required_dir, 'model_data.json')) as infile:
        mdx_model_params = json.load(infile)

    str_tmp = "\033[34m" + "[sing_command.seperate_song]: \033[33m"
    str_end = "\033[0m"
    if mode == 'vocalninst':
        # Put original_audio as song_input argument
        # [~] Separating Vocals from Instrumental...

        print(str_tmp + "Separating Vocals from Instrumental..." + str_end)
        vocals_path, instrumentals_path = run_mdx(mdx_model_params, song_output_dir,
                                                  os.path.join(rvc_required_dir, 'UVR-MDX-NET-Voc_FT.onnx'),
                                                  song_input, denoise=True, keep_orig=keep_orig)

        return vocals_path, instrumentals_path

    elif mode == 'backup':
        # Put vocals_path as song_input argument
        # [~] Separating Main Vocals from Backup Vocals...
        print(str_tmp + "Separating Main Vocals from Backup Vocals..." + str_end)

        backup_vocals_path, main_vocals_path = run_mdx(mdx_model_params, song_output_dir,
                                                       os.path.join(rvc_required_dir, 'UVR_MDXNET_KARA_2.onnx'),
                                                       in_file, suffix='Backup', invert_suffix='Main', denoise=True)
        return backup_vocals_path, main_vocals_path

    elif mode == 'dereverb':
        # Put main_vocals_path as song_input argument
        # [~] Applying DeReverb to Vocals...
        print(str_tmp + "Applying DeReverb to Vocals..." + str_end)

        _, main_vocals_dereverb_path = run_mdx(mdx_model_params, song_output_dir,
                                               os.path.join(rvc_required_dir, 'Reverb_HQ_By_FoxJoy.onnx'),
                                               in_file, invert_suffix='DeReverb', exclude_main=True, denoise=True)
        return main_vocals_dereverb_path
    else:
        raise ValueError(f"Argument mode is invalid: {mode}")


def add_audio_fx(audio_path, reverb_rm_size, reverb_wet, reverb_dry, reverb_damping):
    output_path = f'{os.path.splitext(audio_path)[0]}_mixed.wav'

    # Initialize audio effects plugins
    board = Pedalboard(
        [
            HighpassFilter(),
            Compressor(ratio=4, threshold_db=-15),
            Reverb(room_size=reverb_rm_size, dry_level=reverb_dry, wet_level=reverb_wet, damping=reverb_damping)
        ]
    )

    with AudioFile(audio_path) as f:
        with AudioFile(output_path, 'w', f.samplerate, f.num_channels) as o:
            # Read one second of audio at a time, until the file is empty:
            while f.tell() < f.frames:
                chunk = f.read(int(f.samplerate))
                effected = board(chunk, f.samplerate, reset=False)
                o.write(effected)

    print("\033[34m[sing_command.add_audio_fx]: \033[32mAdd Reverb Process Done!\033[0m")
    return output_path


def merge_audio(in_audio: list, out_dir, volume_settings: list):
    main_vocal_audio = AudioSegment.from_wav(in_audio[0]) - 4 + volume_settings[0]
    backup_vocal_audio = AudioSegment.from_wav(in_audio[1]) - 6 + volume_settings[1]
    instrumental_audio = AudioSegment.from_wav(in_audio[2]) - 7 + volume_settings[2]

    main_vocal_audio.overlay(backup_vocal_audio).overlay(instrumental_audio).export(out_dir, format='mp3')

    print("\033[34m[sing_command.merge_audio]: \033[32mFinal Merge Process Done!\033[0m")


############################################################################
# endregion [SoundFX]

def find_all(dir_path, ext):
    file_list = []
    for filename in glob.glob(os.path.join(dir_path, f'*.{ext}')):
        file_list.append(filename)

    return file_list


if __name__ == '__main__':
    download_required_models()
    v_model = "nahida-jp"

    command, value = check_command("!sing 비둘기 크라잉넛")
    if command == '!sing':
        do_sing(v_model, value, 12)
        # search_audio(value)
        # download_audio("https://youtu.be/Yd8kUoB72xU", "test")
    elif command == '!draw':
        # do_draw(value)
        pass
    elif command == '!emote':
        # do_emote(value)
        pass
    else:
        print("prompt: ", value)
