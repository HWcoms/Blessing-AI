import json
import urllib.request
from urllib.error import HTTPError

from iso639 import languages

import googletrans


# papago
trannslate_url = "https://openapi.naver.com/v1/papago/n2mt"
detect_url = "https://openapi.naver.com/v1/papago/detectLangs"


# If text language is ja -> no translate, but if other source_lang -> translate to ja
def DoTranslate(string, source_lang='ko', target_lang='ja', token_id="", token_secret=""):
    if source_lang == target_lang:
        return string

    # source_lang_name = languages.get(alpha2=source_lang).name
    # traget_lang_name = languages.get(alpha2=target_lang).name

    # Papago Translate
    encText = urllib.parse.quote(str(string))
    # print("인식언어: ",source_lang_name, "목표언어: ", traget_lang_name)

    request = urllib.request.Request(trannslate_url)
    request.add_header("X-Naver-Client-Id", token_id)
    request.add_header("X-Naver-Client-Secret", token_secret)

    data = "source=" + source_lang + "&target=" + target_lang + "&text=" + encText
    result = papago_translate(request, data)

    if result is None:
        result = google_translate(string, target_lang)

    return result


def papago_translate(request, data):
    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))
    except HTTPError as e:
        if e.code == 400:
            if e.headers['apigw-error'] == '084':
                print("unsupported Language: " + '\033[31m' + f"[{data}]" + '\033[0m')
                # return "I just said dumb things that my mic can't understand."
                # TODO: RETURN ERROR STRING AND GO TO READY MODE
        elif e.code == 401:
            print("Authorization failed.")
        elif e.code == 404:
            print("Wrong URL for API request.")
        elif e.code == 429:
            print("Rate Limit Exceeded.")

        print(f'파파고 API 접속 오류: {e}')

        # print(e.reason)
        # print(e.headers) #get apigw-error code

        # use google translate
        return None
        # return "I just said dumb things that my mic can't understand."
        # return "パパゴの APIが翻訳に失敗しました"
    except TimeoutError as e:
        print("Papago Timeout Error: ", e)
        return None

    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        result = response_body.decode('utf-8')
        des = json.loads(result)
        # print(des['message']['result']['translatedText'])

        str = des['message']['result']['translatedText']

        return str

    else:
        print("Error Code:" + rescode)


# when papago fails, Try Google Translate
def google_translate(text, target_lang):
    # translate
    print('구글 번역 시도중.')
    translator = googletrans.Translator()
    result = translator.translate(text, dest=target_lang)

    return result.text


def detect_language(string, token_id="", token_secret=""):
    # Papago detect_language
    encText = urllib.parse.quote(string)
    # print("인식언어: ",source_lang_name, "목표언어: ", traget_lang_name)

    request = urllib.request.Request(detect_url)
    request.add_header("X-Naver-Client-Id", token_id)
    request.add_header("X-Naver-Client-Secret", token_secret)

    data = "query=" + encText

    result = papago_detect_language(request, data)

    if result is None:
        result = google_detect_language(string)

    return result


def papago_detect_language(request, data):
    try:
        response = urllib.request.urlopen(request, data=data.encode("utf-8"))

    except HTTPError as e:
        if e.code == 400:
            if e.headers['apigw-error'] == '084':
                print("unsupported Language: " + '\033[31m' + f"[{data}]" + '\033[0m')
                return None
                # TODO: RETURN ERROR STRING AND GO TO READY MODE
        elif e.code == 401:
            print("Authorization failed.")
        elif e.code == 404:
            print("Wrong URL for API request.")
        elif e.code == 429:
            print("Rate Limit Exceeded.")

        print(f'파파고 API 접속 오류: {e}')

        # use google detect
        return None

    rescode = response.getcode()

    if rescode == 200:
        response_body = response.read()
        response_body = response_body.decode('utf-8')

        data = json.loads(response_body)
        lang_code = data['langCode']

        if lang_code == "unk":
            print("unsupported Language: " + '\033[31m' + f"[{data}]" + '\033[0m')
            return None

        return lang_code
    else:
        print("Error Code:" + rescode)
        return None


def google_detect_language(text):
    print('구글 언어 감지 시도중.')
    translator = googletrans.Translator()
    result = translator.translate(text, dest='en')

    return result.src


# testing translate
if __name__ == '__main__':
    print(DoTranslate("hello", 'en', 'ko'))
    # print(detect_language("hello"))
