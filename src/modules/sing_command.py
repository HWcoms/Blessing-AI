import glob
import io
import os
import subprocess as sp
from typing import Dict, Tuple, Optional, IO

import select

import pytube
from pytube.cli import on_progress

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
    og_vocal, og_inst = search_audio(song_name)
    pitch = 12  # normalize og vocal -> get pitch that similar with inference
    # rvc_vocal = rvc_process(og_vocal, pitch)

    # result_rvc = merge_audio(rvc_vocal, og_inst, "final_rvc")

    # play_audio(result_rvc)
    # return result_rvc


def search_audio(song_name):
    dl_audio = None  # dl

    sep_dir = demucs_audio(dl_audio)

    sep_vocal = sep_dir + "og_vocal.wav"
    sep_inst = sep_dir + "og_inst.wav"

    return sep_vocal, sep_inst


path = os.path.join(os.path.dirname(__file__), 'video_data')
video_file_size = 0


def generate_infos():
    infos = []
    with open("./speaker_links.txt", 'r', encoding='utf-8') as f:
        lines = f.readlines()
    for line in lines:
        line = line.replace("\n", "").replace(" ", "")
        if line == "":
            continue
        speaker, link = line.split("|")
        filename = speaker + "_" + str(random.randint(0, 1000000))
        infos.append({"link": link, "filename": filename})
    return infos


def download_video():
    infos = generate_infos()

    for info in infos:
        link = info['link']
        filename = info['filename']

        yt = pytube.YouTube(link, on_progress_callback=on_progress)
        video = yt.streams.get_lowest_resolution()
        video_file_size = video.filesize
        result_name = video.default_filename
        result_name = result_name.replace(" ", "_")

        if check_file_exist(result_name):
            continue

        video.download('./video_data')

        # pytube.YouTube(link).streams.first().download()

        output_video_name = video.default_filename
        output_prefix_name = result_name

        os.renames(os.path.join(path, output_video_name), os.path.join(path, output_prefix_name))

        temp_file_path = os.path.join(os.path.dirname(__file__), video.title + '.3gpp')
        if (os.path.exists(temp_file_path)):
            os.remove(temp_file_path)

        print("downloaded video! - ", result_name, "    ")


def demucs_audio(in_path=None, out_path=None, model="htdemucs", mp3=False, float32=False, int24=False,
                 two_stems=None):  # ex) two_stems = "vocals"
    cmd = ["python3", "-m", "demucs.separate", "-o", str(out_path), "-n", model]
    ext = "wav"
    if mp3:
        mp3_rate = 320
        cmd += ["--mp3", f"--mp3-bitrate={mp3_rate}"]
        ext = "mp3"
    if float32:
        cmd += ["--float32"]
    if int24:
        cmd += ["--int24"]
    if two_stems is not None:
        cmd += [f"--two-stems={two_stems}"]
    files = find_all(in_path, ext)
    if not files:
        print(f"No valid audio files in {in_path}")
        return
    print("Going to separate the files:")
    print('\n'.join(files))
    print("With command: ", " ".join(cmd))
    p = sp.Popen(cmd + files, stdout=sp.PIPE, stderr=sp.PIPE)
    copy_process_streams(p)
    p.wait()
    if p.returncode != 0:
        print("Command failed, something went wrong.")
    else:
        return out_path  # success


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
    command, value = check_command("!sing song_name")

    print(value)
    if command == '!sing':
        do_sing(value)
    elif command == '!draw':
        # do_draw(value)
        pass
    elif command == '!emote':
        # do_emote(value)
        pass
