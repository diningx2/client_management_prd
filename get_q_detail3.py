import streamlit as st
import pandas as pd
from freq_words_extract import get_freq_words_, no_a, no_n, no_v
from janome.tokenizer import Tokenizer
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from stqdm import stqdm
import codecs

review_columns = ['年齢', '性別', '職業', 'レビュー', 'janome', '星評価', '居住地', 'date']
def get_hinshi(text):
    t = Tokenizer()
    keys = []
    for token in t.tokenize(text):
        if token.part_of_speech.startswith('動詞'):
            if token.base_form not in no_v:
                keys.append(token.base_form)
        if token.part_of_speech.startswith('名詞'):
            if token.base_form not in no_n:
                keys.append(token.base_form)
        if token.part_of_speech.startswith('形容詞'):
            if token.base_form not in no_a:    
                keys.append(token.base_form)
    return ' '.join(keys)

def make_word_df(file, words):
    data = []
    for i in stqdm(range(len(file))):
        review_text = file.iloc[i, 3]
        #print(file.iloc[i, :])
        m = 0
        for word in words:
            if word in file.iloc[i, 4]:
                m += 1
            if m == len(words):
                datum = {}
                for c in range(8):
                    datum[review_columns[c]] = file.iloc[i, c]
                data.append(datum)
    return pd.DataFrame(data=data)

def make_gender_df(file, gender):
    data = []
    for i in range(len(file)):
        g = file.iloc[i, 1]
        if g in gender:
            datum = {}
            for j in range(8):
                datum[review_columns[j]] = file.iloc[i, j]
                
            data.append(datum)
    if len(data) == 0:
        return pd.DataFrame(data = data, columns=review_columns)
    else:
        return pd.DataFrame(data = data)

    return file[file['性別'] in gender]

def make_affiliation_df(file, affiliation):
    data = []
    for i in range(len(file)):
        g = file.iloc[i, 2]
        if g in affiliation:
            datum = {}
            for j in range(8):
                datum[review_columns[j]] = file.iloc[i, j]
            data.append(datum)
    if len(data) == 0:
        return pd.DataFrame(data = data, columns=review_columns)
    else:
        return pd.DataFrame(data = data)
def make_age_df(file, age_list):
    data = []
    age_list = [int(i.replace('代', '')) for i in age_list]
    for i in range(len(file)):
        g = file.iloc[i, 0]
        g = 10*int(g/10)
        if g in age_list:
            datum = {}
            for j in range(8):
                datum[review_columns[j]] = file.iloc[i, j]
            data.append(datum)
    if len(data) == 0:
        return pd.DataFrame(data = data, columns=review_columns)
    else:
        return pd.DataFrame(data = data)

def filter_df(file, gender, affiliation, age_list):
    file = make_gender_df(file, gender)
    file = make_affiliation_df(file, affiliation)
    file = make_age_df(file, age_list)
    return file

def daterange(_start, _end):
    for n in range((_end - _start).days):
        print(n)
        yield _start + timedelta(n)

pd.get_option("display.max_columns")
def get_q_detail(file):
    #st.write(st.session_state['file'])
    if 'file_review' not in st.session_state:
        file_review = file[file['Ambience#Decoration']!='-']
        st.session_state['file_review'] = file_review[['年齢', '性別', '職業', 'レビュー']]
        keys = []
        for i in st.session_state['file_review']['レビュー']:
            keys.append(get_hinshi(i))
        CONTENT = ' '.join(keys)
        st.session_state['file_review']['janome'] = keys
        for c in ['星評価', '居住地']:
            st.session_state['file_review'][c] = file_review[c]
        
        st.session_state['file_review']['date'] = pd.to_datetime(file_review['time'])
        
        st.session_state['CONTENT'] = CONTENT

    #st.dataframe(st.session_state['file_review'])
    if 'CONTENT' not in st.session_state:
        keys = []
        for i in st.session_state['file_review']['レビュー']:
            keys.append(get_hinshi(i))
        CONTENT = ' '.join(keys)
        st.session_state['file_review']['janome'] = keys
        
        st.session_state['CONTENT'] = CONTENT


    logout_button = st.sidebar.button('log out')
    if logout_button:
        st.session_state['login'] = 0


    

    show_all = st.sidebar.radio('レビューの絞り込み', options=['しない', 'する'])
    if show_all == 'しない':
        show_df = st.session_state['file_review'][['年齢', '性別', '職業', 'レビュー', '星評価', '居住地', 'date']]
        show_df['index'] = [i+1 for i in range(len(show_df))]
        show_df = show_df.set_index('index')

        # スペースに置き換えてみる。
        codecs.register_error('error_handler', lambda e: ('', e.end))
        csv = show_df.to_csv().encode('shift_jis', errors='error_handler') 
        st.download_button(
            "csv ダウンロード",
            csv,
            "レビューデータ.csv"
            )
        st.table(show_df)
    else:
        st.session_state['file_review'] = st.session_state['file_review'][review_columns]
        #st.dataframe(st.session_state['file_review'])
        start_ = st.session_state['file_review']['date'].min()
        end_ = st.session_state['file_review']['date'].max()

        start__ = dt.strptime(start_, '%Y-%m-%d') 
        end__ = dt.strptime(end_, '%Y-%m-%d') 
        
        date_range = np.sort(list(set([dt.strptime(str(i.year)+'-'+str(i.month)+'-'+'01', '%Y-%m-%d') for i in list(daterange(start__, end__))])))
        date_option = [str(i)[:7].replace('-','/') for i in date_range]
        date_option = [i+'/01' for i in date_option]
     

        default_gender = st.session_state['file_review']['性別'].unique()
        default_affiliation = st.session_state['file_review']['職業'].unique()
        default_age = [str(i*10)+'代' for i in range(15)]

        gender = st.sidebar.multiselect('性別による絞り込み', options=default_gender, default=default_gender)
        affiliation = st.sidebar.multiselect('職業による絞り込み', options=default_affiliation, default=default_affiliation)
        age_list = st.sidebar.multiselect('年代による絞り込み', options=default_age, default=default_age)
        show_df = filter_df(st.session_state['file_review'][review_columns], gender, affiliation, age_list)
        
        start = st.sidebar.selectbox('開始', options=date_option)
        end = st.sidebar.selectbox('終了', options=date_option)
        start_sp = start.split('/')
        end_sp = end.split('/')

        start = dt.strptime(str(start_sp[0])+'-'+str(start_sp[1])+'-'+'01', '%Y-%m-%d')
        end = dt.strptime(str(end_sp[0])+'-'+str(end_sp[1])+'-'+'01', '%Y-%m-%d')

        print(type(start))
        print(type(show_df['date'][0]))
        if start > end:
            start, end = end, start
        elif start == end:
            end = start + timedelta(weeks=5)
        #show_df['date'] = pd.to_datetime(show_df['date'])
        print(type(show_df['date'][0]))
        print(type(start))
        show_df = show_df[show_df['date'] >= start]
        show_df = show_df[show_df['date'] <= end]



        word_select = st.sidebar.checkbox('頻出単語による絞り込みを行う')
        if word_select:
            num = st.sidebar.number_input('頻出単語の表示する件数（多い順）', min_value=0, step=1)
            options = get_freq_words_(st.session_state['CONTENT'], num)
            selected_words = st.sidebar.multiselect('頻出単語による絞り込み', options=options)
            selected_words = [i.split('(')[0] for i in selected_words]
            show_df = make_word_df(show_df, selected_words)
        if len(show_df) == 0:
            show_df = pd.DataFrame(data=[], columns=review_columns)
        show_df = show_df.rename(columns={'属性': '職業'})
        show_df['index'] = [i+1 for i in range(len(show_df))]
        show_df = show_df.set_index('index')
        show_df=show_df[['年齢', '性別', '職業', 'レビュー', '星評価', '居住地', 'date']]
        # スペースに置き換えてみる。
        codecs.register_error('error_handler', lambda e: ('', e.end))
        csv = show_df.to_csv().encode('shift_jis', errors='error_handler') 
        st.download_button(
            "csv Download",
            csv,
            "user_data.csv"
            )
        st.table(show_df)
        st.sidebar.write('レビュー表示件数：' + str(len(show_df)), ' 件')
    #st.table(st.session_state['file_review'][['年齢', '性別', '職業', 'レビュー']])