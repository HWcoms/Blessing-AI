import glob
import io
import os
import re
import subprocess as sp
from typing import Dict, Tuple, Optional, IO

import select

import yt_dlp
from youtube_search import YoutubeSearch

save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'cache', 'rvc')

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
        return None

    return command_prefix, command_value


def do_sing(song_name):
    og_song = search_audio(song_name)

    demucs_audio(in_path=og_song, out_path=save_dir, mp3=True)
    pitch = 12  # normalize og vocal -> get pitch that similar with inference
    # rvc_vocal = rvc_process(og_vocal, pitch)

    # result_rvc = merge_audio(rvc_vocal, og_inst, "final_rvc")

    # play_audio(result_rvc)
    # return result_rvc


def search_audio(song_name):
    search = YoutubeSearch(song_name, max_results=5).to_dict()
    top_vid = get_highest_view(search)
    dl_url = 'https://www.youtube.com' + top_vid['url_suffix']
    print(dl_url)
    dl_audio = download_audio(dl_url, top_vid['title'])
    print(dl_audio)

    return dl_audio
    #
    # sep_vocal = sep_dir + "og_vocal.wav"
    # sep_inst = sep_dir + "og_inst.wav"

    # return sep_vocal, sep_inst


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


def download_audio(link, filename=None):
    prefix_name = None

    ydl_opts = None
    if filename:
        ydl_opts = {
            'quiet': True,
            'outtmpl': f'{save_dir}/{filename}.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
    else:
        dl_opts = {
            'quiet': True,
            'outtmpl': f'{save_dir}/%(title)s.%(ext)s',
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl_info = ydl.extract_info(link, download=False)
        yt_title = ydl_info['title']

        if filename:
            prefix_name = filename
        else:
            prefix_name = yt_title

        if ".mp3" in prefix_name:
            prefix_name = prefix_name
        else:
            prefix_name += ".mp3"

        # CHECK FILE EXIST
        if filename is None:
            prefix_name = prefix_name.replace(" ", "_")

        if check_file_exist(prefix_name):
            return prefix_name

        ydl.download([link])

    os.renames(os.path.join(save_dir, yt_title + ".mp3"), os.path.join(save_dir, prefix_name))

    print("downloaded video! - ", prefix_name, "    ")
    return prefix_name


def check_file_exist(name):
    file_path = os.path.join(save_dir, name)
    if os.path.exists(file_path):
        print(name, " - file is aleardy exist (skip download)")
        return True
    else:
        return False


def demucs_audio(in_path=None, out_path=None, model="htdemucs", mp3=False, float32=False, int24=False,
                 two_stems=None):  # ex) two_stems = "vocals"
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
        do_sing(value)
        # search_audio(value)
        # download_audio("https://youtu.be/53iAl0Cgc1A", "bocchi")
    elif command == '!draw':
        # do_draw(value)
        pass
    elif command == '!emote':
        # do_emote(value)
        pass
