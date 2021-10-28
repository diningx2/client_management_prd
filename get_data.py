import streamlit as st
import datetime
import pandas as pd
from stqdm import stqdm

def age(year, month, day):
    today = datetime.date.today()
    birthday = datetime.date(year, month, day)
    return (int(today.strftime("%Y%m%d")) - int(birthday.strftime("%Y%m%d"))) // 10000
aspects = ['Location#Transportation', 'Location#Downtown', 'Location#Easy_to_find',
       'Service#Queue', 'Service#Hospitality', 'Service#Parking',
       'Service#Timely', 'Price#Level', 'Price#Cost_effective',
       'Price#Discount', 'Ambience#Decoration', 'Ambience#Noise',
       'Ambience#Space', 'Ambience#Sanitary', 'Food#Portion', 'Food#Taste',
       'Food#Appearance', 'Food#Recommend']

def get_data(db, user_name, b_or_c):
    _ = db.collection(b_or_c).where('user_name', '==', user_name).get()
    for d in _:
        bId = d.id
        st.session_state['branchName'] = d.to_dict()['branchName']
        
    query = db.collection('QuestionnaireResult').where('bId', '==', bId).where('isProcessedByAI', '==', True)
    docs = query.get()

    data = []
    for doc in stqdm(docs):
        datum = {}
        review_data = doc.to_dict()
        
        user_data = db.collection('UserInfo').document(review_data['uId'])
        user_data = user_data.get().to_dict()
        
        if user_data is not None:
            datum['レビュー'] = review_data['response']['detail']
            datum['星評価'] = review_data['response']['star']
            datum['居住地'] = user_data["prefecture"]+user_data["municipality"]
            datum['職業'] = user_data["affiliation"]
            birthdata = user_data['birthday'].split('/')
            datum['年齢'] = age(int(birthdata[0]), int(birthdata[1]), int(birthdata[2]))
            datum['性別'] = user_data['gender']
            datum['time'] = review_data['time'].split('T')[0]

            for a in aspects:
                datum[a] = review_data[a]
            data.append(datum)
    return pd.DataFrame(data=data)


