import re
from bs4 import BeautifulSoup
import urllib.request as urllib

def extract_english_words(input_string):
     pattern = r'[a-zA-Z]+'
     english_words = re.findall(pattern, input_string)
     # print(english_words)
     return english_words

def replace_english_words(input_string, words_to_replace):
     for word in words_to_replace:
          replacement = english_to_katakana(word)
          # print(replacement)
          input_string = input_string.replace(word, replacement)
     return input_string

def replace_eng_jp_words(string):
     english_words = extract_english_words(string)
     if(english_words.count == 0):
          return string
     output_string = replace_english_words(string, english_words)
     
     return output_string

## Use this
def english_to_katakana(word):
     url = 'https://www.sljfaq.org/cgi/e2k_ja.cgi'
     url_q = url + '?word=' + word
     headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:47.0) Gecko/20100101 Firefox/47.0'}

     request = urllib.Request(url_q, headers=headers)
     html = urllib.urlopen(request)
     soup = BeautifulSoup(html, 'html.parser')
     katakana_string = soup.find_all(class_='katakana-string')[0].string.replace('\n', '')

     return katakana_string

#example
# input_string = "ここの water は na本当ni おいしいです**"
# print(replace_eng_jp_words(input_string))