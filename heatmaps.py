import numpy as np
import streamlit as st
import pandas as pd
from user_heatmap import get_heatmap, get_starmap, get_heat_matrix, get_aspectmap, get_seibetsu, get_shozoku, get_nenrei, get_kyojuchi, get_hoshi, get_sentiment_bar
from freq_words_extract import get_freq_words, no_a, no_n, no_v
from janome.tokenizer import Tokenizer
import datetime
from datetime import datetime as dt


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


def heatmaps(file):
    file_review = file[file['Ambience#Decoration']!='-']
    st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 500px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 500px;
        margin-left: -500px;
    }
    </style>
    """,
    unsafe_allow_html=True,
    )

    logout_button = st.sidebar.button('log out')
    if logout_button:
        st.session_state['login'] = 0
    st.dataframe(file[['年齢', '性別', '職業', 'レビュー', 'time']])
    
    heat_matrix = get_heat_matrix(file)
    
    if 'file_review_' not in st.session_state:
        file_review = file[file['Ambience#Decoration']!='-']
        st.session_state['file_review_'] = file_review[['年齢', '性別', '職業', 'レビュー', '星評価', '居住地', 'time']]
        st.session_state['file_review_']['date'] = st.session_state['file_review_']['time']
        keys = []
        for i in st.session_state['file_review_']['レビュー']:
            keys.append(get_hinshi(i))
        CONTENT = ' '.join(keys)
        st.session_state['file_review_']['janome'] = keys
        
        st.session_state['CONTENT'] = CONTENT
    

    options = st.multiselect(
    '可視化する図を選んでください',
    ['客層ヒートマップ', '星評価ヒートマップ', '属性項目可視化マップ', '来客者性別情報円グラフ', '来客者職業情報円グラフ', '来客者年齢情報円グラフ', '来客者居住地情報円グラフ', '来客者星評価情報円グラフ', '項目別店舗評価'])

    options_side = st.sidebar.multiselect(
    '可視化する円グラフを選んでください',
    ['来客者性別情報円グラフ', '来客者職業情報円グラフ', '来客者年齢情報円グラフ', '来客者居住地情報円グラフ', '来客者星評価情報円グラフ', '頻出単語'])
    if '来客者性別情報円グラフ' in options_side:
        get_seibetsu(file, st.sidebar, True)
    
    if '来客者職業情報円グラフ' in options_side:
        get_shozoku(file, st.sidebar, True)
    
    if '来客者年齢情報円グラフ' in options_side:
        get_nenrei(file, st.sidebar, True)
    
    if '来客者居住地情報円グラフ' in options_side:
        get_kyojuchi(file, st.sidebar, True)
    
    if '来客者星評価情報円グラフ' in options_side:
        get_hoshi(file, st.sidebar, True)
    
    if '頻出単語' in options_side:
        num = st.sidebar.number_input('表示する件数', min_value=0, step=1)
        if num > 0:
            get_freq_words(st.session_state['CONTENT'], num, st.sidebar)
    options2 = options.copy()
    for i in options:
        if i in ['客層ヒートマップ', '星評価ヒートマップ', '属性項目可視化マップ', '項目別店舗評価']:
            options2.remove(i)

    left_column,right_column = st.columns(2)
    column_map = {}
    for i in range(len(options2)):
        if i % 2 == 0:

            column_map[options2[i]] = left_column
        else:

            column_map[options2[i]] = right_column

    if '客層ヒートマップ' in options:
        get_heatmap(file, heat_matrix)

    if '星評価ヒートマップ' in options:
        get_starmap(file, heat_matrix)

    if '属性項目可視化マップ' in options:
        get_aspectmap(file_review)

    if '来客者性別情報円グラフ' in options:
        get_seibetsu(file, st, False)
    
    if '来客者職業情報円グラフ' in options:
        get_shozoku(file, st, False)
    
    if '来客者年齢情報円グラフ' in options:
        get_nenrei(file, st, False)
    
    if '来客者居住地情報円グラフ' in options:
        get_kyojuchi(file, st, False)
    
    if '来客者星評価情報円グラフ' in options:
        get_hoshi(file, st, False)
    
    if '項目別店舗評価' in options:
        get_sentiment_bar(file_review)


    