import streamlit as st
import pandas as pd
from freq_words_extract import get_freq_words_, no_a, no_n, no_v
from janome.tokenizer import Tokenizer
import numpy as np
from datetime import datetime as dt
from datetime import timedelta, datetime
from stqdm import stqdm
import codecs

review_columns = ['年齢', '性別', '職業', 'レビュー', 'janome', '星評価', '居住地', 'date']

def get_hinshi(text):
    extract_list = ['名詞', '動詞', '形容詞', '形容動詞']
    t = Tokenizer()
    base_text = [i.base_form for i in t.tokenize(text)]
    hinshi_text = [i.part_of_speech.split(',')[0] for i in t.tokenize(text)]
    new_token_list = [base_text[i] for i in range(len(base_text)) if hinshi_text[i] in extract_list]
    return ' '.join(new_token_list)

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
        yield _start + timedelta(n)

def get_datetime(str_):
    return datetime.strptime(str_[:7]+'-01', '%Y-%m-%d')

def get_datetime_list_s(start_, end_):
    start_datetime = get_datetime(start_)
    end_datetime = get_datetime(end_)
    if start_datetime.year == end_datetime.year:
        datetime_list = [str(start_datetime.year) + '年' + str(i) + '月1日' for i in range(start_datetime.month, end_datetime.month+1)]
    else:
        datetime_list = []
        for i in range(start_datetime.month, 13):
            datetime_list.append(str(start_datetime.year) + '年' + str(i) + '月1日')
        for i in range(start_datetime.year+1, end_datetime.year):
            for j in range(1, 13):
                datetime_list.append(str(i) + '年' + str(j) + '月1日')
        for i in range(1, end_datetime.month+1):
            datetime_list.append(str(end_datetime.year) + '年' + str(i) + '月1日')
    
    return datetime_list

def get_str_(datetime_option):
    year_str = datetime_option.split('年')[0]
    month = datetime_option.split('年')[1].split('月')[0]
    return datetime(int(year_str), int(month), 1, 0, 0)

def get_datetime_list_e(start_, end_):
    start_datetime = get_datetime(start_)
    end_datetime = get_datetime(end_)
    if start_datetime.year == end_datetime.year:
        datetime_list = [str(start_datetime.year) + '年' + str(i) + '月末' for i in range(start_datetime.month, end_datetime.month+1)]
    else:
        datetime_list = []
        for i in range(start_datetime.month, 13):
            datetime_list.append(str(start_datetime.year) + '年' + str(i) + '月末')
        for i in range(start_datetime.year+1, end_datetime.year):
            for j in range(1, 13):
                datetime_list.append(str(i) + '年' + str(j) + '月1日')
        for i in range(1, end_datetime.month+1):
            datetime_list.append(str(end_datetime.year) + '年' + str(i) + '月末')
    
    return datetime_list


pd.get_option("display.max_columns")
def get_q_detail2(file):
    #st.write(st.session_state['file'])
    if 'file_review' not in st.session_state:
        file_review_columns = ['年齢', '性別', '職業', 'レビュー', '星評価', '居住地', 'time']
        file_review_data = file[file['Ambience#Decoration']!='-']
        data = []
        keys = []
        for i in stqdm(range(len(file_review_data))):   
            frd_i = file_review_data.iloc[i, :] 
            datum = {}
            for c in file_review_columns:
                if i in [0, 1,2,3]:
                    print(c)
                if c != 'time':
                    datum[c] = frd_i[c]
                if c == 'レビュー':
                    key = get_hinshi(datum[c])
                    datum['janome'] = key
                    keys.append(key)
                if c == 'time':
                    #date : str
                    #time : datetime
                    datum['date'] = frd_i[c]
                    print(datum['date'])
                    print(datum['date'])
                    print(datum['date'])
                    print(datum['date'])
                    datum['time'] = [datetime.strptime(i, '%Y-%m-%d') for i in datum['date']]
            data.append(datum)
        st.session_state['file_review'] = pd.DataFrame(data=data)
        CONTENT = ' '.join(keys)
        st.session_state['file_review']['janome'] = keys
        st.session_state['CONTENT'] = CONTENT

    st.dataframe(st.session_state['file_review'])


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
        #何日まで？？
        st.session_state['file_review'] = st.session_state['file_review'][review_columns]
        #st.dataframe(st.session_state['file_review'])
        start_ = st.session_state['file_review']['date'].min()
        end_ = st.session_state['file_review']['date'].max()
        start_datetime_option = get_datetime_list_s(start_, end_)
        end_datetime_option = get_datetime_list_e(start_, end_)


        default_gender = st.session_state['file_review']['性別'].unique()
        default_affiliation = st.session_state['file_review']['職業'].unique()
        default_age = [str(i*10)+'代' for i in range(15)]

        gender = st.sidebar.multiselect('性別による絞り込み', options=default_gender, default=default_gender)
        affiliation = st.sidebar.multiselect('職業による絞り込み', options=default_affiliation, default=default_affiliation)
        age_list = st.sidebar.multiselect('年代による絞り込み', options=default_age, default=default_age)
        show_df = filter_df(st.session_state['file_review'][review_columns], gender, affiliation, age_list)
        
        start = st.sidebar.selectbox('開始', options=start_datetime_option)
        end = st.sidebar.selectbox('終了', options=end_datetime_option)
        start_sp = get_str_(start)
        end_sp = get_str_(end)

        if start_sp > end_sp:
            start_sp, end_sp = end_sp, start_sp
        elif start == end:
            end_sp = start_sp + timedelta(weeks=5)
        #show_df['date'] = pd.to_datetime(show_df['date'])
        
        show_df = show_df[show_df['time'] >= start_sp]
        show_df = show_df[show_df['time'] <= end_sp]

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