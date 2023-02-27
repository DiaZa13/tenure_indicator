import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from PreprocessingData import get_agencies_balances, get_atm_balances, get_atm_transport, graphBalance, getData


# page configuration
st.set_page_config(page_title='Análisis de tenencia', page_icon='random', layout='wide')

header = st.container()
dataset = st.container()
graphs = st.empty()

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

    data = getData();

    col0, col1 = st.columns(2)

    with col0:
        uploaded_agency_file = st.file_uploader("Seleccione el balance diario de agencia")
        if uploaded_agency_file is not None:
            agency = get_agencies_balances(uploaded_agency_file)
            data = pd.concat([data, pd.DataFrame(agency)], ignore_index=True)

    with col1:
        uploaded_atm_file = st.file_uploader("Seleccione el balance de ATM's")
        if uploaded_atm_file is not None:
            atm_balances = get_atm_balances(uploaded_atm_file)
            atm_transport = get_atm_transport(uploaded_atm_file)
            data = pd.concat([data, pd.DataFrame(atm_balances)], ignore_index=True)
            data = pd.concat([data, pd.DataFrame(atm_transport)], ignore_index=True)

with graphs.container():                
    st.header('Estadísticas generales')

    fig = go.Figure()
    salas = data[data['type'] == 'Salas']
    agencies = data[data['type'] == 'Agencias']
    atm = data[data['type'] == 'ATM']
    transport = data[data['type'] == 'Transporte']
    total = data.groupby(by=['date'], as_index=False).sum(numeric_only=True)

    fig = graphBalance(salas, agencies, atm, transport, total)
    st.plotly_chart(fig, use_container_width=True);

    # Select box para gráfica mensual
    option_month = st.selectbox(
        'Análisis mensual',
        month.keys()
    )

    st.write('Usted seleccionó:', option_month)

    # Gráfica mensual
    data_month = get_month_graph(data, option_month)
    month_fig = px.bar(data_month, x='date', y='hnl', color='type')
    st.plotly_chart(month_fig, use_container_width=True)
