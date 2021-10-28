import numpy as np
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.graph_objects import Layout



aspects = ['Location#Transportation', 'Location#Downtown',
        'Location#Easy_to_find', 'Service#Queue', 'Service#Hospitality',
        'Service#Parking', 'Service#Timely', 'Price#Level',
        'Price#Cost_effective', 'Price#Discount', 'Ambience#Decoration',
        'Ambience#Noise', 'Ambience#Space', 'Ambience#Sanitary', 'Food#Portion',
        'Food#Taste', 'Food#Appearance', 'Food#Recommend']

aspects_japanese = ["立地#アクセスの良さ","立地#都心・繁華街にあるか","立地#見つけやすいか", "サービス#入店までの待ち時間", "サービス#接客", "サービス#駐車場の利便性", 
                    "サービス#料理の提供時間", "価格#水準", "価格#コストパフォーマンス", "価格#割引について", "雰囲気#装飾・雰囲気", "雰囲気#音楽・ノイズ", "雰囲気#店内・席の広さ",
                    "雰囲気#清潔感", "料理#分量", "料理#味", "料理#見た目", "料理#おすすめできるか"]

#data = {'10' : 0, '20' : 1, '30' : 2, '40' : 3, '50' : 4, '60' : 5, '会社員/団体職員' : 6, 'パート/アルバイト' : 7, '自営業/個人事業主' : 8, '主婦/主夫' : 9, '学生' : 10, '契約社員/派遣社員' : 11,
#    '会社役員/団体役員' : 12, '専門職(医師/弁護士/会計士/税理士等)' : 13, '退職された方' : 14, '公務員' : 15, '男性': 16, '女性' : 17}



def get_d(reviews):
    if 'data' not in st.session_state:
        ages = reviews['年齢'] / 10
        ages_list = []
        for age in ages:
            ages_list.append(10 * np.int(age))
        ages = np.sort(list(set(ages_list)))
        zokuseis = reviews['職業'].unique()
        seibetsus = reviews['性別'].unique()
        data = {}
        m = 0
        for age in ages:
            data[str(age)] = m
            m += 1 
        for age in zokuseis:
            data[age] = m
            m += 1 
        for age in seibetsus:
            data[age] = m
            m += 1 
        columns = []
        indexes = []
        for k in data.keys():
            columns.append(k)
            indexes.append(k)
        st.session_state['columns'] = columns
        st.session_state['indexes'] = indexes
        st.session_state['data'] = data
    return st.session_state['data']

def get_heat_matrix(reviews):
    if 'heat_matrix' not in st.session_state:
        data = get_d(reviews)
        heat_matrix = np.zeros((len(data), len(data)))
        for i in range(len(reviews)):
            age = reviews['年齢'][i]
            zokusei = reviews['職業'][i]
            seibetsu = reviews['性別'][i]

            age = str(10 * int(age / 10))
            heat_matrix[data[age], data[age]] += 1
            heat_matrix[data[age], data[zokusei]] += 1
            heat_matrix[data[age], data[seibetsu]] += 1

            heat_matrix[data[zokusei], data[zokusei]] += 1
            heat_matrix[data[zokusei], data[age]] += 1
            heat_matrix[data[zokusei], data[seibetsu]] += 1

            heat_matrix[data[seibetsu], data[seibetsu]] += 1
            heat_matrix[data[seibetsu], data[zokusei]] += 1
            heat_matrix[data[seibetsu], data[age]] += 1
        st.session_state['heat_matrix'] = heat_matrix
    return st.session_state['heat_matrix']
    
def get_heatmap(reviews, heat_matrix):
    
    df = pd.DataFrame(data=heat_matrix, columns=st.session_state['columns'], index=st.session_state['indexes'])
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=df, x=df.columns, y=df.index, colorscale='blues'))
    fig.update_layout(height=700, width=700, title='客層ヒートマップ')
    st.plotly_chart(fig, use_container_width=True)


def get_starmap(reviews, heat_matrix):
    if 's_m_5' not in st.session_state:
        data = get_d(reviews)
        s_m_5 = np.zeros((5, len(data)))
        for i in range(len(reviews)):
            age = reviews['年齢'][i]
            zokusei = reviews['職業'][i]
            seibetsu = reviews['性別'][i]
            age = str(10 * int(age / 10))
            star = int(reviews['星評価'][i] - 1)

            d_age = data[age]
            d_z = data[zokusei]
            d_s = data[seibetsu]

            age_len = heat_matrix[d_age, d_age]
            z_len = heat_matrix[d_z, d_z]
            s_len = heat_matrix[d_s, d_s]
            

            s_m_5[star, d_age] += 1
            s_m_5[star, d_z] += 1
            s_m_5[star, d_s] += 1
        st.session_state['s_m_5'] = s_m_5
    s_map = pd.DataFrame(st.session_state['s_m_5'], columns=st.session_state['columns'], index=[i + 1 for i in range(5)])
    for c in st.session_state['columns']:
        if np.sum(s_map[c]) != 0:
            s_map[c] = s_map[c] / np.sum(s_map[c])
    
    fig = go.Figure()
    fig.add_trace(go.Heatmap(z=s_map, x=s_map.columns, y=s_map.index, colorscale='blues'))
    fig.update_layout(height=400, width=700, title='星評価ヒートマップ')
    st.plotly_chart(fig, use_container_width=True)

def get_aspectmap(reviews):
    if 'aspect_df' not in st.session_state:
        reviews2 = pd.DataFrame()
        age_list = []
        seibetsu_list = []
        zokusei_list = []
        
        for z in reviews['職業']:
            zokusei_list.append(z)
        for s in reviews['性別']:
            seibetsu_list.append(s)
        for age in reviews['年齢']:
            age_list.append(int(age / 10) * 10)

        
        reviews2['年齢'] = age_list
        reviews2['性別'] = seibetsu_list
        reviews2['職業'] = zokusei_list 
        for asp in aspects:
            asp_list = []
            for s in reviews[asp]:
                asp_list.append(s)
            reviews2[asp] = asp_list
        
        #for i in range(len(reviews)):
        #    reviews2['年齢'][i] = int(reviews2['年齢'][i] / 10) * 10
        data = get_d(reviews)
        #data2 = {'10' : 0, '20' : 1, '30' : 2, '40' : 3, '50' : 4, '60' : 5, '会社員/団体職員' : 6, 'パート/アルバイト' : 7, '自営業/個人事業主' : 8, '主婦/主夫' : 9, '学生' : 10, '契約社員/派遣社員' : 11,
        #       '会社役員/団体役員' : 12, '専門職(医師/弁護士/会計士/税理士等)' : 13, '退職された方' : 14, '公務員' : 15, '男性': 16, '女性' : 17}
        data2 = {}
        m = 0
        for k in data.keys():
            data2[k] = m
    

        n = 0
        for k in data2.keys():
            d = {}
            d['emb'] = n
            for a in aspects:
                d[a] = {'positive' : 0, 'negative' : 0}
            data2[k] = d
            n += 1

        for v in reviews2['年齢'].unique():

            v_df = reviews2[reviews2['年齢'] == v]
            for a in aspects:
                data2[str(v)][a]['positive'] = len(v_df[v_df[a]=='positive'])
                data2[str(v)][a]['negative'] = len(v_df[v_df[a]=='negative'])

        for v in reviews2['性別'].unique():

            v_df = reviews2[reviews2['性別'] == v]
            for a in aspects:
                data2[str(v)][a]['positive'] = len(v_df[v_df[a]=='positive'])
                data2[str(v)][a]['negative'] = len(v_df[v_df[a]=='negative'])

        for v in reviews2['職業'].unique():

            v_df = reviews2[reviews2['職業'] == v]
            for a in aspects:
                data2[str(v)][a]['positive'] = len(v_df[v_df[a]=='positive'])
                data2[str(v)][a]['negative'] = len(v_df[v_df[a]=='negative'])


        a_m = np.zeros((len(aspects), len(data)))
        a_m_sub = np.zeros((len(aspects), len(data)))

        for i in range(len(reviews2)):
            age = reviews2['年齢'][i]
            zokusei = reviews2['職業'][i]
            seibetsu = reviews2['性別'][i]
            age = str(10 * int(age / 10))

            d_a = data2[age]['emb']
            d_z = data2[zokusei]['emb']
            d_s = data2[seibetsu]['emb']

            for a in range(len(aspects)):
                s = reviews2[aspects[a]][i]
                if s == 'positive':
                    a_m[a, d_a] += 1 / (data2[age][aspects[a]]['positive'] + data2[age][aspects[a]]['negative'] + 1)
                    a_m[a, d_s] += 1 / (data2[seibetsu][aspects[a]]['positive'] + data2[seibetsu][aspects[a]]['negative'] + 1)
                    a_m[a, d_z] += 1 / (data2[zokusei][aspects[a]]['positive'] + data2[zokusei][aspects[a]]['negative'] + 1)

                    a_m_sub[a, d_a] += 1 
                    a_m_sub[a, d_s] += 1 
                    a_m_sub[a, d_z] += 1 
                if s == 'negative':

                    a_m_sub[a, d_a] += 1 
                    a_m_sub[a, d_s] += 1 
                    a_m_sub[a, d_z] += 1 

        a_m2 = a_m * 2 - 1
        for i in range(len(aspects)):
            for j in range(len(data)):
                if a_m_sub[i][j] == 0:
                    a_m2[i][j] = None
        
        aspect_df = pd.DataFrame(data=a_m2, columns=st.session_state['columns'], index=aspects_japanese)
        st.session_state['aspect_df'] = aspect_df

    layout = Layout(plot_bgcolor='rgba(0,0,0,0)')
    fig = go.Figure(layout=layout)
    fig.add_trace(go.Heatmap(z=st.session_state['aspect_df'], x=st.session_state['aspect_df'].columns, y=st.session_state['aspect_df'].index, colorscale='blues'))
    fig.update_layout(height=700, width=700, title='属性項目可視化マップ')
    st.plotly_chart(fig, use_container_width=True)

def get_seibetsu(reviews, col, leg):

    seibetsu_label = reviews['性別'].unique()
    seibetsu = []
    for s in seibetsu_label:
        seibetsu.append(len(reviews[reviews['性別']==s]))
    fig = go.Figure(go.Pie(
        sort=True,
        direction ='clockwise', 
        values = seibetsu,
        labels = seibetsu_label,
        texttemplate = "%{label}: %{value:s}人 <br>(%{percent})",
        textposition = "inside"))
    fig.update_layout(title='性別可視化円グラフ')
    if leg:
        fig.update_layout(showlegend=False)
    col.plotly_chart(fig, use_container_width=True)

def get_shozoku(reviews, col, leg):
    
    shozoku_label = reviews['職業'].unique()
    shozoku = []
    for s in shozoku_label:
        shozoku.append(len(reviews[reviews['職業']==s]))
    fig = go.Figure(go.Pie(
        sort=True,
        direction ='clockwise', 
        values = shozoku,
        labels = shozoku_label,
        texttemplate = "%{label}: %{value:s}人 <br>(%{percent})",
        textposition = "inside"))
    fig.update_layout(title='職業可視化円グラフ')
    if leg:
        fig.update_layout(showlegend=False)
    col.plotly_chart(fig, use_container_width=True)

def get_nenrei(reviews, col, leg):

    reviews2 = reviews.copy()
    for i in range(len(reviews)):
        reviews2['年齢'][i] = int(reviews2['年齢'][i] / 10) * 10
    age_label = reviews2['年齢'].unique()
    age = []
    for s in age_label:
        age.append(len(reviews2[reviews2['年齢']==s]))
    
    age_label_str = []
    for i in range(len(age_label)):
        age_label_str.append(np.str(age_label[i])+'代')
    
    fig = go.Figure(go.Pie(
        sort=True,
        direction ='clockwise', 
        values = age,
        labels = age_label_str,
        texttemplate = "%{label}: %{value:,s}人 <br>(%{percent})",
        textposition = "inside"))
    fig.update_layout(title='年齢可視化円グラフ')
    if leg:
        fig.update_layout(showlegend=False)
    col.plotly_chart(fig, use_container_width=True)


def get_kyojuchi(reviews, col, leg):

    shozoku_label = reviews['居住地'].unique()
    shozoku = []
    for s in shozoku_label:
        shozoku.append(len(reviews[reviews['居住地']==s]))
    
    fig = go.Figure(go.Pie(
        sort=True,
        direction ='clockwise', 
        values = shozoku,
        labels = shozoku_label,
        texttemplate = "%{label}: %{value:s}人 <br>(%{percent})",
        textposition = "inside"))
    fig.update_layout(title='居住地可視化円グラフ')
    if leg:
        fig.update_layout(showlegend=False)
    col.plotly_chart(fig, use_container_width=True)

def get_hoshi(reviews, col, leg):

    shozoku_label = reviews['星評価'].unique()
    shozoku = []
    for s in shozoku_label:
        shozoku.append(len(reviews[reviews['星評価']==s]))
    shozoku_label_str = []
    for i in range(len(shozoku_label)):
        shozoku_label_str.append('⭐️'+np.str(shozoku_label[i]))

 
    fig = go.Figure(go.Pie(
        sort=True,
        direction ='clockwise', 
        values = shozoku,
        labels = shozoku_label_str,
        texttemplate = "%{label}: %{value:s}人 <br>(%{percent})",
        textposition = "inside"))
    fig.update_layout(title='星評価可視化円グラフ')
    if leg:
        fig.update_layout(showlegend=False)
    col.plotly_chart(fig, use_container_width=True)

def get_sentiment_bar(reviews):

    sentiment_rate = []
    for a in aspects:
        n_len = len(reviews[reviews[a] == "negative"]) + 1
        p_len = len(reviews[reviews[a] == "positive"]) + 1
        sentiment_rate.append((200*p_len/(p_len+n_len))-100)
    #df = pd.DataFrame(sentiment_rate, index=aspects_japanese)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=sentiment_rate,
                     y=aspects_japanese,
                     #marker_color='#87cefa',
                     textfont={'color': '#87cefa'},
                     name='項目別店舗評価'),
    )
    fig.update_traces(textposition='outside',
                     orientation='h')
    fig.update_layout(title='項目別店舗評価',
                  legend=dict(orientation='h',
                              xanchor='right',
                              x=1,
                              yanchor='bottom',
                              y=1.05),
                  width=800, 
                  height=600,
                  )

    st.plotly_chart(fig, use_container_width=True)