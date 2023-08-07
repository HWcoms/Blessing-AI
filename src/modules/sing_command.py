import glob
import io
import os
import re
import subprocess as sp
from contextlib import suppress
from typing import Dict, Tuple, Optional, IO

import select

import yt_dlp
from youtube_search import YoutubeSearch
from urllib.parse import urlparse, parse_qs

# demucs
from rvc_modules.mdx import run_mdx

rvc_cache_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache', 'rvc')
save_dir = rvc_cache_dir
orig_song_path = os.path.join(rvc_cache_dir, 'original_song')
output_dir = os.path.join(rvc_cache_dir, 'mdx_output')
mdxnet_models_dir = os.path.join(rvc_cache_dir, 'mdx_models')

# CHECK AUDIO CACHE FOLDER
if not os.path.exists(save_dir):
    os.makedirs(save_dir)
    print("\033[34m" + f"[sing_command]: Created audio cache folder! \033[33m[{save_dir}]" + "\033[0m")


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


def do_sing(song_name):
    dl_url, video_id = search_audio(song_name)
    dl_audio = download_audio(dl_url, video_id)

    # demucs_audio(in_path=og_song, out_path=save_dir, mp3=True, int24=True)
    # sep_vocal = sep_dir + "og_vocal.wav"
    # sep_inst = sep_dir + "og_inst.wav"
    # return sep_vocal, sep_inst

    pitch = 12  # normalize og vocal -> get pitch that similar with inference
    # rvc_vocal = rvc_process(og_vocal, pitch)

    # result_rvc = merge_audio(rvc_vocal, og_inst, "final_rvc")

    # play_audio(result_rvc)
    # return result_rvc


def search_audio(song_name):
    search = YoutubeSearch(song_name, max_results=5).to_dict()
    top_vid = get_highest_view(search)
    dl_url = 'https://www.youtube.com' + top_vid['url_suffix']
    print("\033[34m" + f"[sing_command.search_audio]: \033[33mfound video on Youtube [{dl_url}]" + "\033[0m")

    video_id = get_youtube_video_id(dl_url)

    # print(f"[sing_command.search_audio]: downloaded Youtube video to audio in [{dl_audio}]")

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
                return parse_qs(query.query)['list'][0]
        if query.path == '/watch':
            return parse_qs(query.query)['v'][0]
        if query.path[:7] == '/watch/':
            return query.path.split('/')[1]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]

    # returns None for invalid YouTube url
    return None


def download_audio(link, out_dir_name):
    prefix_name = None

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

        orig_song_path = os.path.join(save_dir, out_dir_name)

        # CHECK FILE EXIST
        if check_file_exist(prefix_name, orig_song_path, "[Mp3 Found]"):
            return prefix_name

        if not os.path.exists(orig_song_path):
            os.makedirs(orig_song_path)
            print("\033[34m" + f"[sing_command.download_audio]: Created audio folder for yt-download! \033[33m[{orig_song_path}]" + "\033[0m")

    if not check_file_exist(download_name, orig_song_path, "[Wav Found]"):
        ydl.download([link])
        print("downloaded video! - ", prefix_name, "    ")

        os.renames(os.path.join(download_name), os.path.join(orig_song_path, download_name))

    return prefix_name


def check_file_exist(name, custom_dir, custom_log=""):
    file_path = os.path.join(custom_dir, name)

    if os.path.exists(file_path):
        print("\033[34m" f"[sing_command.check_file_exist]: \033[33m{custom_log} {name} - file is aleardy exist (skip process)" + "\033[0m")
        return True
    else:
        return False


def all_in_one(song_id):
    keep_orig = True
    song_output_dir = os.path.join(output_dir, song_id)

    mdx_model_params = None

    # [~] Separating Vocals from Instrumental...
    vocals_path, instrumentals_path = run_mdx(mdx_model_params, song_output_dir,
                                              os.path.join(mdxnet_models_dir, 'UVR-MDX-NET-Voc_FT.onnx'),
                                              orig_song_path, denoise=True, keep_orig=keep_orig)

    # [~] Separating Main Vocals from Backup Vocals...
    backup_vocals_path, main_vocals_path = run_mdx(mdx_model_params, song_output_dir,
                                                   os.path.join(mdxnet_models_dir, 'UVR_MDXNET_KARA_2.onnx'),
                                                   vocals_path, suffix='Backup', invert_suffix='Main', denoise=True)

    # [~] Applying DeReverb to Vocals...
    _, main_vocals_dereverb_path = run_mdx(mdx_model_params, song_output_dir,
                                           os.path.join(mdxnet_models_dir, 'Reverb_HQ_By_FoxJoy.onnx'),
                                           main_vocals_path, invert_suffix='DeReverb', exclude_main=True, denoise=True)

    return orig_song_path, vocals_path, instrumentals_path, main_vocals_path, backup_vocals_path, main_vocals_dereverb_path


def demucs_audio(in_path=None, out_path=None, model="htdemucs", mp3=False, float32=False, int24=False,
                 two_stems="vocals"):  # ex) two_stems = "vocals"
    cmd = ["python3", "-m", "demucs.separate", "-o", str(out_path), "-n", model]
    ext = "wav"
    if mp3:
        mp3_rate = 320
        cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
        ext = "mp3"
    if float32:
        cmd += [" --float32"]
    if int24:
        cmd += [" --int24"]
    if two_stems is not None:
        cmd += [f" --two-stems={two_stems}"]

    in_full_path = os.path.join(save_dir, in_path)

    if not os.path.exists(in_full_path):
        print(f"No valid audio files in {in_full_path}")
        return

    print("Going to separate the files:")
    print(f"{cmd} {in_full_path}")

    import demucs.separate
    demucs.separate.main(cmd)
    # os.system(f"{cmd} {in_full_path}")
    os.system(f"demucs --two-stems=vocals {in_full_path}")
    # p = sp.Popen(cmd + in_full_path, stdout=sp.PIPE, stderr=sp.PIPE)
    # copy_process_streams(p)
    # p.wait()
    # if p.returncode != 0:
    #     print("Command failed, something went wrong.")
    # else:
    #     return out_path  # success


def find_all(dir_path, ext):
    file_list = []
    for filename in glob.glob(os.path.join(dir_path, f'*.{ext}')):
        file_list.append(filename)

    return file_list


def copy_process_streams(process: sp.Popen):
    def raw(stream: Optional[IO[bytes]]) -> IO[bytes]:
        assert stream is not None
        if isinstance(stream, io.BufferedIOBase):
            stream = stream.raw
        return stream

    p_stdout, p_stderr = raw(process.stdout), raw(process.stderr)
    stream_by_fd: Dict[int, Tuple[IO[bytes], io.StringIO, IO[str]]] = {  # noqa
        p_stdout.fileno(): (p_stdout, sys.stdout),  # noqa
        p_stderr.fileno(): (p_stderr, sys.stderr),  # noqa
    }  # noqa
    fds = list(stream_by_fd.keys())

    while fds:
        # `select` syscall will wait until one of the file descriptors has content.
        ready, _, _ = select.select(fds, [], [])
        for fd in ready:
            p_stream, std = stream_by_fd[fd]  # noqa
            raw_buf = p_stream.read(2 ** 16)
            if not raw_buf:
                fds.remove(fd)
                continue
            buf = raw_buf.decode()
            std.write(buf)
            std.flush()


def rvc_process(audio, pitch):
    result = "test"
    return result


def add_sound_fx(audio, reverb=True, echo=False):
    result = audio
    if reverb:
        # Add Reverb
        result = audio
    if echo:
        # Add Echo
        result = audio

    return result


def merge_audio(vocal, inst, out_name):
    from pydub import AudioSegment  # noqa

    sound1 = AudioSegment.from_mp3(vocal)
    sound2 = AudioSegment.from_mp3(inst)

    # mix sound2 with sound1
    output = sound1.overlay(sound2)

    # save the result
    result = out_name

    output.export(f"{out_name}.mp3", format="mp3")

    return result


if __name__ == '__main__':
    command, value = check_command("!sing kemono friends opening")
    if command == '!sing':
        value = "TVアニメ「ぼっち・ざ・ろっく！」オープニング映像/「青春コンプレックス」#結束バンド"
        do_sing(value)
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
