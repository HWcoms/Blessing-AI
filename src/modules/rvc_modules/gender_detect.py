from inaSpeechSegmenter import Segmenter
from inaSpeechSegmenter.export_funcs import seg2csv
import pandas as pd

# Load the model
seg = Segmenter()

# Choose any mp3 file online
# media = 'https://github.com/ina-foss/inaSpeechSegmenter/raw/master/media/musanmix.mp3'
media = r'C:\Users\HWcoms\Blessing-AI\cache\rvc\song_process\avAfAZ6d-Rg\EZ DO DANCE (THUNDER STORM ver.) 더빙_Vocals.wav'


def seperate_audio_infos(media_path):
    # Run the segmentation
    seg_list = seg(media_path)

    return seg_list


def compare_gender(segment_list):
    if len(segment_list) < 1:
        raise ValueError("list is empty")

    female_duration = 0
    male_duration = 0
    top_seg = None

    for _seg in segment_list:
        if _seg[0] == 'female':
            female_duration += _seg[2] - _seg[1]
        elif _seg[0] == 'male':
            male_duration += _seg[2] - _seg[1]
    if female_duration > male_duration:
        top_seg = 'female'
    else:
        top_seg = 'male'

    if top_seg:
        print("\033[34m" + f"[gender_detect.comparegender]: Gender Classified \033[33m[{top_seg}]" + "\033[0m")

    return top_seg


def pitch_by_gender(og_gender_type: str, ai_gender_type: str, defer_value):
    pitch = 0.0
    if og_gender_type == ai_gender_type:
        pitch = 0.0
    else:
        if og_gender_type == 'female':  # ai_gender -> male
            pitch -= defer_value
        elif og_gender_type == 'male':  # ai_gender -> female
            pitch += defer_value

    pitch = round(float(pitch), 1)
    return pitch


# All in one method
def get_pitch_with_audio(audio_file, ai_gender_type: str, defer_value=12.0):  # ai_gender_type -> ["female", "male"]
    segmented_infos = seperate_audio_infos(audio_file)
    og_gender_type = compare_gender(segmented_infos)

    return pitch_by_gender(og_gender_type, ai_gender_type, defer_value)


if __name__ == "__main__":
    print(get_pitch_with_audio(media, "female"))

    # seg_infos = seperate_audio_infos(media)
    # og_gen_type = compare_gender(seg_infos)
    #
    # ai_gen_type = 'female'
    # print(pitch_by_gender(og_gen_type, ai_gen_type))
