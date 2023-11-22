import speech_recognition as sr


def is_silence(audio_data, threshold=0.01):
    # Assuming audio_data is a byte sequence representing PCM audio data

    # Convert byte sequence to a list of integers (assuming 16-bit little-endian encoding)
    samples = [int.from_bytes(audio_data[i:i + 2], byteorder='little', signed=True) for i in
               range(0, len(audio_data), 2)]

    # Check if all samples are below the threshold
    silent = all(abs(sample) < threshold for sample in samples)

    return silent


def is_wav_human_voice(audio_data, energy_threshold=300):
    recognizer = sr.Recognizer()
    aud_file = sr.AudioFile(audio_data)
    recognizer.energy_threshold = energy_threshold

    # dynamic energy compensation lowers the energy threshold to a point where SpeechRecognizer never stops recording.
    recognizer.dynamic_energy_threshold = False

    with aud_file as source:
        recorded = recognizer.listen(source)
        rec2 = recognizer.record(source)

    rec = rec2.get_raw_data()

    raw_data = recorded.get_raw_data()
    # print(raw_data)

    has_sound = not is_silence(raw_data)
    # print('has word spoken?:', not has_sound)
    return has_sound


def is_human_voice(frames, sample_rate, sample_width=2):
    recognizer = sr.Recognizer()
    aud_file = sr.AudioData(frames, sample_rate, sample_width)

    # dynamic energy compensation lowers the energy threshold to a point where SpeechRecognizer never stops recording.
    recognizer.dynamic_energy_threshold = False

    with aud_file as source:
        recorded = recognizer.listen(source)

    raw_data = recorded.get_raw_data()

    has_sound = is_silence(raw_data)
    # print('has word spoken?:', not has_sound)
    return not has_sound


if __name__ == "__main__":
    import os

    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    cache_dir = os.path.join(root_dir, 'cache', 'user_mic')
    file_path = os.path.join(cache_dir, 'mic_0_main.wav')

    result = is_wav_human_voice(file_path)

    if result:
        print("The file contains human voice.")
    else:
        print("The file may contain noise or non-speech audio.")
