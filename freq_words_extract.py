import collections
import streamlit as st


no_v = ['する', 'いる', '思う', 'くれる', 'ある', 'くる', 'なる', '来る', 'できる', 'れる', '']
no_n = ['の', 'そう', 'さん', 'よい', 'これ', 'あれ', 'それ', 'どれ', '方', 'ん', 'よう', '']
no_a = ['']




def get_freq_words(CONTENT, num, col):
    content_list = [i for i in CONTENT.split(' ') if i != '']
    
    c = collections.Counter(content_list)
    most_c = c.most_common()[:num]
    expander = col.expander('頻出単語(件数)')
    for i in range(len(most_c)):
        expander.write(most_c[i][0]+'('+str(most_c[i][1])+')')

def get_freq_words_(CONTENT, num):
    content_list = [i for i in CONTENT.split(' ') if i != '']
    c = collections.Counter(content_list)
    most_c = c.most_common()[:num]
    return [most_c[i][0]+'('+str(most_c[i][1])+')' for i in range(len(most_c))]
