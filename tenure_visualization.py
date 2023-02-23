# Basado en: https://github.com/tdenzl/BuLiAn/blob/main/BuLiAn.py

import streamlit as st
import pandas as pd
import plotly.express as px
from PreprocessingData import get_agencies_balances, get_atm_balances, get_atm_transport


# page configuration
st.set_page_config(page_title='Análisis de tenencia', page_icon='random', layout='wide')

header = st.container()
dataset = st.container()
graphs = st.container()

col0, col1 = st.columns(2)

with header:
    st.title('Analizador de la Tenencia')

with dataset:
    st.header("Tenencia por día ")
    # description
    st.markdown(
        'Para actualizar las gráficas de tenencia deberá de subir los archivos de balances diarios')

    data = pd.read_feather('tenure.feather')

    with col0:
        uploaded_agency_file = st.file_uploader("Seleccione el balance diario de agencia")
        if uploaded_agency_file is not None:
            agency = get_agencies_balances(uploaded_agency_file)
            data = data.append(agency, ignore_index=True)

    with col1:
        uploaded_atm_file = st.file_uploader("Seleccione el balance de ATM's")
        if uploaded_atm_file is not None:
            atm_balances = get_atm_balances(uploaded_atm_file)
            atm_transport = get_atm_transport(uploaded_atm_file)
            data = data.append(atm_balances, ignore_index=True)
            data = data.append(atm_transport, ignore_index=True)

with graphs:                
    st.header('Estadísticas generales')

    st.plotly_chart(px.bar(data, x='date', y='hnl', color='type'), use_container_width=True)
