import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime as dt
from datetime import timedelta
import numpy as np

def make_date_column(start,end):

    # 日付条件の設定
    strdt = dt.strptime(start, '%Y-%m-%d')  # 開始日
    enddt = dt.strptime(end, '%Y-%m-%d')  # 終了日

    # 日付差の日数を算出（リストに最終日も含めたいので、＋１しています）
    days_num = (enddt - strdt).days + 1 
    # シンプルにforとappendを使用した場合
    datelist = []
    for i in range(days_num):
        datelist.append(strdt + timedelta(days=i))

    date2=[]

    # 確認用
    for d in datelist:
        date2.append(d.strftime("%Y-%m-%d"))
    date2=pd.DataFrame({'date':date2})
    
    return date2

def daterange(_start, _end):
    for n in range((_end - _start).days):
        yield _start + timedelta(n)

def make_term_data(df, term):
    df["date"] = pd.to_datetime(df["date"]) #datetime型にする
    df['date'] = df['date'].dt.strftime("%Y-%m-%d")
    dfa=df[['date','星評価']]
    dfa=dfa.groupby('date').mean()

    if len(dfa) != 0:
        start, end=dfa.index[0],dfa.index[-1]
    else:
        start, end=dfa.index[0],dfa.index[0]
    date=make_date_column(start,end)
    date['trash']=1
    date["date"] = pd.to_datetime(date["date"]) #datetime型にする
    date=date.groupby('date').mean()
    date=date.resample(term).sum()

    return date

def make_df_new(df, term):
    date=make_term_data(df, term)
    df["date"] = pd.to_datetime(df["date"]) #datetime型にする


    df_new=df[['date','星評価']]
    df_new=df_new.groupby('date').mean()
    df_new=df_new.resample(term).mean()
    df_new=pd.merge(date,df_new,on='date', how='outer').drop('trash',axis=1)
    
    
    for name in ['職業','性別']:
        dfb=df[['date',name]]
        dfb['num']=1
        dfb=dfb.groupby(['date',name]).sum()
        columns =df[name].unique().tolist()

        for belongs in columns:
            a=dfb.xs(belongs,level=name).rename(columns={'num':  belongs})
            b=a.resample(term).sum()
            df_new=pd.merge(df_new,b,on='date', how='outer')

    #何歳まで見る？
    n=int(100)
    name='年齢'
    dfs=df[['date',name]].sort_values(name)
    dfs['num']=1
    labels = [ '{0} – {1}'.format(i, i + 10) for i in range(0, n, 10) ]
    dfs[name]=pd.cut(dfs[name],np.arange(0, n+10, 10),labels=labels)
    dfs=dfs.groupby(['date',name]).sum()
    
  

    for belongs in labels:
        a=dfs.xs(belongs,level=name).rename(columns={'num':  belongs})
        b=a.resample(term).sum()
        df_new=pd.merge(df_new,b,on='date', how='outer')
    df_new=df_new.fillna(0).astype(float)



    
    
    return df_new

def make_df_nageposi(df,term):
    date=make_term_data(df, term)
    list=['date', 'Location#Transportation', 'Location#Downtown',
           'Location#Easy_to_find', 'Service#Queue', 'Service#Hospitality',
           'Service#Parking', 'Service#Timely', 'Price#Level',
           'Price#Cost_effective', 'Price#Discount', 'Ambience#Decoration',
           'Ambience#Noise', 'Ambience#Space', 'Ambience#Sanitary', 'Food#Portion',
           'Food#Taste', 'Food#Appearance', 'Food#Recommend']
    dfa=df[list]
    dfa=dfa.set_index('date')
    columns=dfa.columns
    for c in columns:
        for i in range(0,len(dfa)):
            if dfa[c][i]=='not_mentioned':
                dfa[c][i]=0
            elif dfa[c][i]=='positive':
                dfa[c][i]=1
            else:
                dfa[c][i]=-1
    dfa=dfa.reset_index()
    dfa["date"] = pd.to_datetime(dfa["date"]) #datetime型にする
    dfa=dfa.groupby('date').agg(['sum','count'])
    new=pd.DataFrame(index=dfa.index, columns=columns)
    for c in columns:
        for i in range(0,len(dfa)):
            if dfa[c]['count'][i]!=0:
    #             print(new[c][i])
                new[c][i]= dfa[c]['sum'][i]/dfa[c]['count'][i]
            else:
                new[c][i]=0

    new=new.resample(term).agg(['sum','count'])
    newdf=pd.DataFrame(index=new.index, columns=columns)
    for c in columns:
        for i in range(0,len(new)):
            if new[c]['count'][i]!=0:
                newdf[c][i]= new[c]['sum'][i]/new[c]['count'][i]
            else:
                newdf[c][i]=0
    newdf=pd.merge(date,newdf,on='date', how='outer').drop('trash',axis=1)

    aspects_japanese = ["立地#アクセスの良さ","立地#都心・繁華街にあるか","立地#見つけやすいか", "サービス#入店までの待ち時間", "サービス#接客", "サービス#駐車場の利便性", 
                    "サービス#料理の提供時間", "価格#水準", "価格#コストパフォーマンス", "価格#割引について", "雰囲気#装飾・雰囲気", "雰囲気#音楽・ノイズ", "雰囲気#店内・席の広さ",
                    "雰囲気#清潔感", "料理#分量", "料理#味", "料理#見た目", "料理#おすすめできるか"]
    list=['Location#Transportation', 'Location#Downtown',
           'Location#Easy_to_find', 'Service#Queue', 'Service#Hospitality',
           'Service#Parking', 'Service#Timely', 'Price#Level',
           'Price#Cost_effective', 'Price#Discount', 'Ambience#Decoration',
           'Ambience#Noise', 'Ambience#Space', 'Ambience#Sanitary', 'Food#Portion',
           'Food#Taste', 'Food#Appearance', 'Food#Recommend']
    for n in range(len(list)):
        newdf=newdf.rename(columns={list[n] :aspects_japanese[n]})

    return newdf

# def make_plot(df_all):

#     fig = go.Figure()
#     fig.add_trace(go.Scatter(y=df_all['女性'],x=df_all.index, name='女'))
#     fig.add_trace(go.Scatter(y=df_all['男性'],x=df_all.index ,name='男性'))
#     fig.show()
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(y=df_all['星評価'],x=df_all.index, name='配列の名前'))
#     fig.update_layout(legend_title_text='タイトル')
#     fig.show()
#     fig = go.Figure()
#     for name in df['所属'].unique().tolist():
#         fig.add_trace(go.Scatter(y=df_all[name],x=df_all.index, name=name))
#     fig.show()
#     fig = go.Figure()
#     labels = [ '{0} – {1}'.format(i, i + 10) for i in range(0, 100, 10) ]
#     for name in labels:
#         fig.add_trace(go.Scatter(y=df_all[name],x=df_all.index, name=name))
#     fig.show()


def time_series(df1):
    df1 = df1.rename(columns={'time': 'date'}) 
    df1["date"] = pd.to_datetime(df1["date"])

    logout_button = st.sidebar.button('log out')
    if logout_button:
        st.session_state['login'] = 0
    
    st.write('各種時系列')

    start_ = df1['date'].min()
    end_ = df1['date'].max()
    date_range = np.sort(list(set([dt.strptime(str(i.year)+'-'+str(i.month)+'-'+'01', '%Y-%m-%d') for i in list(daterange(start_, end_))])))
    date_option = [str(i)[:7].replace('-','/') for i in date_range]
    date_option = [i+'/01' for i in date_option]
    
    right, left = st.columns(2)
    start = right.selectbox('開始', options=date_option)
    end = left.selectbox('終了', options=date_option)
    
    start_sp = start.split('/')
    end_sp = end.split('/')

    start = dt.strptime(str(start_sp[0])+'-'+str(start_sp[1])+'-'+'01', '%Y-%m-%d')
    end = dt.strptime(str(end_sp[0])+'-'+str(end_sp[1])+'-'+'01', '%Y-%m-%d')
    if start > end:
        start, end = end, start
    elif start == end:
        end = start + timedelta(weeks=5)
 

    df1 = df1[df1['date'] >= start]
    df1 = df1[df1['date']<= end]
    

    term = st.selectbox('期間選択', options=['1日', '1週間', '1ヶ月'])
    if term == '1日':
        df_all = make_df_new(df1, 'D')
        df_np= make_df_nageposi(df1,'D')
    elif term == '1週間':
        df_all = make_df_new(df1, 'W')
        df_np = make_df_nageposi(df1, 'W')
    else:
        df_all = make_df_new(df1, 'M')
        df_np = make_df_nageposi(df1, 'M')
    not_star = [i for i in df_all.columns if i!='星評価']
    


    #df_all['星評価'] = df_all['星評価'] / df_all[not_star].sum(axis=1)


    names = st.multiselect('星評価、職業、年齢',df_all.columns)
    fig = go.Figure()
    for name in names:
        fig.add_trace(go.Scatter(y=df_all[name],x=df_all.index, name=name))
    fig.update_layout(width=900, height=400)
    if term == '1日':
        fig.update_xaxes(dtick=7 * 86400000.0)
    elif term == '1週間':
        fig.update_xaxes(dtick=14 * 86400000.0)
    else:
        fig.update_xaxes(dtick='M1')
    
    st.plotly_chart(fig, use_container_width=True)

    

 
    
    names = st.multiselect('アンケートにおける『ポジティブな回答の割合』を1から-1の間で表しています。1に近づくほどポジティブな回答が多いです。',df_np.columns)

    fig2= go.Figure()
    for name in names:
        fig2.add_trace(go.Scatter(y=df_np[name],x=df_np.index, name=name))
    fig2.update_layout(width=900, height=400)
    if term == '1日':
        fig2.update_xaxes(dtick=7 * 86400000.0)
    elif term == '1週間':
        fig2.update_xaxes(dtick=14 * 86400000.0)
    else:
        fig2.update_xaxes(dtick='M1')
    
    st.plotly_chart(fig2, use_container_width=True)


    

