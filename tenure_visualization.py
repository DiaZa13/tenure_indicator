import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PreprocessingData import get_agencies_balances, get_atm_balances, get_atm_transport


# page configuration
st.set_page_config(page_title='Análisis de tenencia', page_icon='random', layout='wide')

header = st.container()
dataset = st.container()
graphs = st.container()

padding_top = 2.5

st.markdown(f'''
            <style>
                .css-k1ih3n {{
                    padding-top: {padding_top}rem;
                }}
            </style>
            ''', unsafe_allow_html=True,
    )

with header:

    st.title('Analizador de la Tenencia')

with dataset:
    st.header("Tenencia por día ")
    # description
    st.markdown(
        'Para actualizar las gráficas de tenencia deberá de subir los archivos de balances diarios')

    data = pd.read_feather('tenure.feather')

    col0, col1 = st.columns(2)

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

 
    fig = go.Figure()
    salas = data[data['type'] == 'Salas']
    agencias = data[data['type'] == 'Agencias']
    automatic = data[data['type'] == 'ATM']
    transport = data[data['type'] == 'Transporte']
    fig.add_trace(go.Bar(x=salas['date'], y=salas['hnl'], name='Salas'))
    fig.add_trace(go.Bar(x=agencias['date'], y=agencias['hnl'], name='Agencias'))
    fig.add_trace(go.Bar(x=automatic['date'], y=automatic['hnl'], name='ATM'))
    fig.add_trace(go.Bar(x=transport['date'], y=transport['hnl'], name='Transporte'))

    group_data = data.groupby(by=['date'], as_index=False).sum(numeric_only=True)
    fig.add_scatter(x = group_data['date'], y=group_data['hnl'], mode="markers", opacity=0,
                    marker={'symbol': 'square'},
                    line={'color':'black'},
                    name='Total')
    fig.update_layout(barmode='relative', title_text='Saldos totales por día')
    st.plotly_chart(fig, use_container_width=True);