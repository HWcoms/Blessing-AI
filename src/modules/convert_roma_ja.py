import re
from bs4 import BeautifulSoup
import urllib.request as urllib
# import requests

from concurrent.futures import ThreadPoolExecutor
import lxml
import cchardet

from datetime import datetime

def extract_english_words(input_string):
     pattern = r'[a-zA-Z]+'
     english_words = re.findall(pattern, input_string)
     # print(english_words)
     return english_words

def replace_english_words(input_string, words_to_replace, katakana_words):
     for (word,kata) in zip(words_to_replace, katakana_words):
          # print(replacement)
          input_string = input_string.replace(word, kata)
     return input_string

def english_to_katakana(string):
     #english_words -> original english words
     english_words = extract_english_words(string)
     # results -> katakana words
     results = get_katakana_words_parallel(english_words)
     
     output_string = replace_english_words(string, english_words, results)
     return output_string

def get_katakana_words_parallel(words):
     results = []
     
     executor = ThreadPoolExecutor(max_workers=100)
     for result in executor.map(get_katakana_words, words):
          results.append(result)
     
     return results
     

def get_katakana_words(word):
     url = f"https://www.sljfaq.org/cgi/e2k_ja.cgi?word={word}"
     headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 OPR/98.0.0.0 (Edition GX-CN)'}
     request = urllib.Request(url, headers=headers)
     html = urllib.urlopen(request)
     soup = BeautifulSoup(html, 'lxml')
     # katakana_string = soup.find_all(class_='katakana-string')[0].string.replace('\n', '') #unuse
     katakana_string = soup.select('.katakana-string')[0].string.replace('\n', '')
     return katakana_string

# #example
# input_string = "ここの water は na本当ni おいしいです**"

# now = datetime.now()
# print(english_to_katakana(input_string))
# sec = datetime.now()
# print("time: ",(sec-now).total_seconds())

