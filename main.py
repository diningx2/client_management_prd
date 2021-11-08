import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import pandas as pd
import streamlit as st
from heatmaps import heatmaps
from get_data import get_data
from time_series import time_series
from lottery_settings import lottery_settings
from get_q_detail import get_q_detail
from get_q_detail2 import get_q_detail2 
import os
import json
from stqdm import stqdm


if not firebase_admin._apps:

    
    # 初期済みでない場合は初期化処理を行う
    keys = {
    "type": os.environ.get('type'),
    "project_id": os.environ.get('project_id'),
    "private_key_id": os.environ.get('private_key_id'),
    "private_key": os.environ.get('private_key'),
    "client_email": os.environ.get('client_email'),
    "client_id": os.environ.get('client_id'),
    "auth_uri": os.environ.get('auth_uri'),
    "token_uri": os.environ.get('token_uri'),
    "auth_provider_x509_cert_url": os.environ.get('auth_provider_x509_cert_url'),
    "client_x509_cert_url": os.environ.get('client_x509_cert_url')
    }
    if os.environ.get('isDeployment') is None:
        from secret.secret import keys as KEYS
        keys = KEYS
    
    #print(type(keys))

    #json_open = open('keys.json', 'w')
    #json.dump(keys, json_open, indent=2)
    #json_open.close()
    #json_open = open('keys.json', 'r')
    #json_file = json.load(json_open)
    #print('=========================')
    #print(json_file)
    #print('=========================')
    cred = credentials.Certificate(keys)
    firebase_admin.initialize_app(cred)
    

if 'db' not in st.session_state:
    st.session_state['db'] = firestore.client()

if 'login' not in st.session_state:
    st.session_state['login'] = 0
st.header('店舗管理画面')
if st.session_state['login'] == 0:
    info_pass_list = {'店長' : 'BranchInfo', 'オーナー' : 'ClientInfo'}
    branch_or_client = st.radio('選択', ['店長', 'オーナー'])
    query = st.session_state['db'].collection(info_pass_list[branch_or_client])
    docs = query.get()
    login_pass_list = {}
    for d in stqdm(docs):
        doc = d.to_dict()
        login_pass_list[doc['user_name']] = doc['password']
    #st.write(login_pass_list)
    user_name = st.text_input('user name')
    password = st.text_input('password', type="password")
    login_button = st.button('login')

    if login_button:
        if user_name not in login_pass_list.keys():
            st.write('user nameが存在しません')
        else:
            correct_password = login_pass_list[user_name]
            if correct_password != password:
                st.write('pass wordが違います。')
            else:
                if len(st.session_state) != 0:
                    for k in st.session_state.keys():
                        if k != "db":
                            st.session_state.pop(k)
                st.session_state['login'] = 1
                st.session_state['user_name'] = user_name
                st.session_state['b_or_c'] = info_pass_list[branch_or_client]

if st.session_state['login'] == 1:
    if st.session_state['b_or_c'] == 'BranchInfo':
        if 'file' not in st.session_state:
            file = get_data(st.session_state['db'], st.session_state['user_name'], st.session_state['b_or_c'])
            st.session_state['file'] = file
        
        st.subheader(st.session_state['branchName'])
        option = st.selectbox('サービスを選択してください',('-', 'ヒートマップ・円グラフ', '時系列可視化', 'レビュー個別表示', '各種設定'))
        if option == 'ヒートマップ・円グラフ':

            if 'file' not in st.session_state:
                file = get_data(st.session_state['db'], st.session_state['user_name'], st.session_state['b_or_c'])
                st.session_state['file'] = file
            if len(st.session_state['file']) == 0:
                st.write('表示するアンケートがありません')
            else:
                heatmaps(st.session_state['file'])
        
        if option == '時系列可視化':
            if 'file' not in st.session_state:
                file = get_data(st.session_state['db'], st.session_state['user_name'], st.session_state['b_or_c'])
                st.session_state['file'] = file
            if len(st.session_state['file']) == 0:
                st.write('表示するアンケートがありません')
            else:
                time_series(st.session_state['file'])
        
        if option == 'レビュー個別表示':
            if 'file' not in st.session_state:
                file = get_data(st.session_state['db'], st.session_state['user_name'], st.session_state['b_or_c'])
                st.session_state['file'] = file

            if len(st.session_state['file']) == 0:
                st.write('表示するアンケートがありません')
            else:
                get_q_detail(st.session_state['file'])

        if option == '各種設定':
            lottery_settings(st.session_state['db'], st.session_state['user_name'], st.session_state['b_or_c'])



    
    else:
        st.write('実装中')
        logout = st.button('logout')


        if logout:
            st.session_state['login'] = 0

            





            

