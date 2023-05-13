import requests


          params_encoded = urlencode({'text': sentence, 'speaker': voice_Dyna_id})
    r = requests.post(f'{BASE_URL}/audio_query?{params_encoded}')