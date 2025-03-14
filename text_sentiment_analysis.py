import pandas as pd
df=pd.read_excel('/content/drive/MyDrive/Test/20211030 Test Assignment/Input.xlsx')
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from bs4 import BeautifulSoup
import os
import numpy as np
import re
import nltk
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('cmudict')
import string

for i in range(len(df)):
  link=df.loc[i][1]
  try:
    page_connect = urlopen(link)    
    soup = BeautifulSoup(page_connect, "html.parser")
    head=soup.find('h1')
    body=soup.find('body')
    head = head.get_text().replace("\n"," ")
    head = re.sub('\s+', ' ', head)
    text = body.get_text().replace("\n"," ")
    text = re.sub('\s+', ' ', text)
    foot="Blackcoffer Insights"
    start=text.find(head)
    text=text[start:]
    if foot not in text:
      foot='TAGS'
      if foot not in text:
        foot='Previous article'
    end=text.find(foot)
    text=text[:end]
    personal_pronouns = ["I", "we", "my", "ours", "us"]
    pro_count = 0
    for word in text:
      if word == "US":
          continue
      elif word in personal_pronouns:
          pro_count += 1
    with open('/content/drive/MyDrive/Test/20211030 Test Assignment/StopWords/StopWords_GenericLong.txt', 'r') as file:
      file_contents = file.read().upper()
    with open('/content/drive/MyDrive/Test/20211030 Test Assignment/StopWords/StopWords_GenericLong.txt', 'w') as file:
      file.write(file_contents)
    stop_list=[]
    for files in os.listdir('/content/drive/MyDrive/Test/20211030 Test Assignment/StopWords'):
      if 'Currencies' in files:
        filename='/content/drive/MyDrive/Test/20211030 Test Assignment/StopWords/StopWords_Currencies.txt'
        import chardet
        with open(filename, 'rb') as file:
            raw_data = file.read(1024)
        result = chardet.detect(raw_data)
        encoding = result['encoding']
        with open(filename, 'r', encoding=encoding) as file:
            file_contents = file.read()
      else:  
        filename='/content/drive/MyDrive/Test/20211030 Test Assignment/StopWords/'+files
        with open(filename, 'r') as file:
          file_contents = file.read()
      pattern = r'\b[A-Z]+\b'
      uppercase_words = re.findall(pattern, file_contents)
      for word in uppercase_words:
        stop_list.append(word)
        text = re.sub(r'\b' + re.escape(word) + r'\b', '', text)
    text_list=nltk.word_tokenize(text)
    word_list=re.findall(r'\b\w+\b',text)
    num_words=len(word_list)

    f = open("/content/drive/MyDrive/Test/20211030 Test Assignment/MasterDictionary/positive-words.txt", "r")
    data=f.read()
    pos = data.split("\n")
    f.close()
    f = open('/content/drive/MyDrive/Test/20211030 Test Assignment/MasterDictionary/negative-words.txt', encoding = "ISO-8859-1") 
    data=f.read()
    neg = data.split("\n")
    f.close()
    pos_score=0
    neg_score=0
    for word in text_list:
      if word.lower() in pos:
        if pos not in stop_list:
          pos_score+=1
      elif word.lower() in neg:
        if neg not in stop_list:
          neg_score+=1
    polarity=(pos_score-neg_score)/((pos_score+neg_score)+0.000001)
    subj=(pos_score+neg_score)/(num_words+0.000001)
    sentence_list=nltk.sent_tokenize(text)
    num_sentences=len(sentence_list)
    avg_sen_len=num_words/num_sentences
    def is_complex(word):
      pos_tag = nltk.pos_tag([word])[0][1]
      complex_pos_tags = ['JJ', 'JJR', 'JJS', 'RB', 'RBR', 'RBS']
      return pos_tag in complex_pos_tags
    num_complex_words = 0
    for word in text_list:
        if is_complex(word):
            num_complex_words += 1
    per_complex_words=100 * (num_complex_words / num_words)
    fog_index = 0.4 * (avg_sen_len + per_complex_words)
    d = nltk.corpus.cmudict.dict()
    suffixes = ['es', 'ed']
    text = [word if not any(word.endswith(suffix) for suffix in suffixes) else word[:-2] for word in text.split()]
    syl_counts=[]
    for word in text:
      count = 0
      for phonemes in d.get(word.lower(), [[]]):
        count += len([p for p in phonemes if p[-1].isdigit()])
      syl_counts.append(count)
    num_letters=0
    for word in text:
      for letter in word:
        num_letters+=1
    avg_word_len=num_letters/num_words
    avg_words_per_sen=num_words/num_sentences
    syl_per_word=np.average(syl_counts)

    dict={'POSITIVE SCORE':pos_score,
    'NEGATIVE SCORE':neg_score,
    'POLARITY SCORE':polarity,
    'SUBJECTIVITY SCORE':subj,
    'AVG SENTENCE LENGTH':avg_sen_len,
    'PERCENTAGE OF COMPLEX WORDS':per_complex_words,
    'FOG INDEX':fog_index,
    'AVG NUMBER OF WORDS PER SENTENCE':avg_words_per_sen,
    'COMPLEX WORD COUNT':num_complex_words,
    'WORD COUNT':num_words,
    'SYLLABLE PER WORD':syl_per_word,
    'PERSONAL PRONOUNS':pro_count,
    'AVG WORD LENGTH':avg_word_len}
    for k in range(len(list(dict.keys()))):
      df.loc[i, list(dict.keys())[k]]=list(dict.values())[k]
    df.to_excel('Output Data Structure.xlsx')
  except (URLError, HTTPError):
    continue
