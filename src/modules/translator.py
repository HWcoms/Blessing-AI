from iso639 import languages
import urllib.request
import json

from os import getenv
from dotenv import load_dotenv
load_dotenv()
import googletrans

PAPAGO_AUTH_ID = getenv('PAPAGO_AUTH_ID')
PAPAGO_AUTH_SECRET = getenv('PAPAGO_AUTH_SECRET')

#papago
client_id = PAPAGO_AUTH_ID      # 개발자센터에서 발급받은 Client ID 값
client_secret = PAPAGO_AUTH_SECRET      # 개발자센터에서 발급받은 Client Secret 값
url = "https://openapi.naver.com/v1/papago/n2mt"

#If text language is ja -> no translate, but if other source_lang -> translate to ja
def DoTranslate(string, source_lang = 'ko', target_lang = 'ja'):
     if(source_lang == target_lang):
        return string
       
     source_lang_name = languages.get(alpha2=source_lang).name
     traget_lang_name = languages.get(alpha2=target_lang).name
     
     #Papago Translate       
     encText = urllib.parse.quote(string)    
     # print("인식언어: ",source_lang_name, "목표언어: ", traget_lang_name)
     
     request = urllib.request.Request(url)
     request.add_header("X-Naver-Client-Id",client_id)
     request.add_header("X-Naver-Client-Secret",client_secret)
     
     data = "source="+source_lang+"&target="+target_lang+"&text=" + encText
     result = papago_translate(request, data)
          
     return result
        

def papago_translate(request, data):
     try:
          response = urllib.request.urlopen(request, data=data.encode("utf-8"))
     except Exception as e:
          print(f'파파고 API 접속 오류: {e}, 구글번역 시도중.')
          
          #use google translate
          return google_translate(data)
          # return "パパゴの APIが翻訳に失敗しました"
               
     rescode = response.getcode()
     
     if(rescode==200):
          response_body = response.read()
          result = response_body.decode('utf-8')
          des = json.loads(result)
          #print(des['message']['result']['translatedText'])
          
          str = des['message']['result']['translatedText']
          
          return str
     
     else:
          print("Error Code:" + rescode)   
          
#when papago fails, Try google translate
def google_translate(data):
     source, target, text = extract_query_string(data)
     text = urllib.parse.unquote(text) 
     ##translate
     translator = googletrans.Translator()
     result = translator.translate(text, dest=target)
     
     return result.text

#Get infos from query
def extract_query_string(query_string):
     variables = query_string.split('&')
     variable_dict = {}

     for variable in variables:
          key, value = variable.split('=')
          variable_dict[key] = value

     source = variable_dict.get('source')
     target = variable_dict.get('target')
     text = variable_dict.get('text')

     return source, target, text