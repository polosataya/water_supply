# streamlit run Холодная_вода.py
import streamlit as st
import pandas as pd
#import numpy as np
#from datetime import datetime, timedelta
import seaborn as sns
import matplotlib.pyplot as plt


st.set_page_config(
    page_title="Прогнозирование технологических ситуаций",
    page_icon="🛁", layout="wide",
    initial_sidebar_state="expanded",
    menu_items={'Get Help': None,'Report a bug': None,'About': None})

hide_streamlit_style = """<style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style>"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

############################################################################
# config
############################################################################

cold_path = "data/Посуточная ведомость водосчетчика ХВС ИТП.xlsx"
hot_path = "data/Посуточная ведомость ОДПУ ГВС.xlsx"
cold_sheet = "Водосчетчик ИТП ХВС"
hot_sheet = "ОДПУ ГВС"
cold_cols = ["Дата", "Время суток, ч", "Потребление накопленным итогом, м3", "Потребление за период, м3"]
hot_cols =  ["Дата", "Время суток, ч", "Подача, м3", "Обратка, м3", "Потребление за период, м3", "Т1 гвс, оС", "Т2 гвс, оС"]
new_col=['День недели']

############################################################################
# работа с файлами
############################################################################

@st.cache_data
def load_file(file_path, sheet_name, col_names):
    '''Загрузка файла'''
    data = pd.read_excel(file_path, sheet_name=sheet_name, engine='openpyxl')
    data['Дата']=pd.to_datetime(data['Дата'], format='%d.%m.%Y')
    data['Время суток, ч']=data['Время суток, ч'].str.split('-').str.get(1).astype(int)
    data['День недели'] = data['Дата'].dt.weekday + 1
    return data[col_names+new_col]

def display_heatmap(title, data, figsize=(12,6)):
    '''Теплокарта потребления воды по дням недели и часам'''
    out = data.groupby(['День недели', 'Время суток, ч'])['Потребление за период, м3'].sum().unstack()
    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(out, cmap="crest", ax=ax)
    plt.title(title)
    plt.ylabel('День недели')
    plt.xlabel('Час')
    st.pyplot(fig)
    #st.write(fig)

def display_linechart(title, data, figsize=(12,6)):
    '''Суммарное за день потребление'''
    out = data.groupby(['Дата'])['Потребление за период, м3'].agg({'min', 'max'}).reset_index()
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(out['Дата'], out['min'], label='Минимальное потребление в час')
    ax.plot(out['Дата'], out['max'], label='Максимальное потребление в час')
    ax.legend()
    plt.title(title)
    plt.ylabel('Потребление')
    plt.xlabel('Дата')
    st.pyplot(fig)

def display_all(title, data_1, data_2, figsize=(12,6)):
    ''' Сравнение поребления горячей и холодной воды по дням'''
    out_1 = data_1.groupby(['Дата'])['Потребление за период, м3'].agg({'sum', 'max'}).reset_index()
    out_2 = data_2.groupby(['Дата'])['Потребление за период, м3'].agg({'sum', 'max'}).reset_index()
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(out_1['Дата'], out_1['sum'], label='Потребление за день холодной воды')
    ax.plot(out_2['Дата'], out_2['max'], label='Потребление за день горячей воды')
    ax.legend()
    plt.title(title)
    plt.ylabel('Потребление')
    plt.xlabel('Дата')
    st.pyplot(fig)

############################################################################
# вывод результатов
############################################################################

data_cold = load_file(cold_path, cold_sheet, cold_cols)
data_hot = load_file(hot_path, hot_sheet, hot_cols)


display_heatmap('Потребление холодной воды', data_cold, figsize=(12,6))

display_linechart('Потребление холодной воды за день', data_cold, figsize=(12,6))

display_all('Потребление воды за день', data_cold, data_hot, figsize=(12,6))

