from io import StringIO
import os
import pathlib
import pandas as pd
import csv
import plotly.graph_objects as go
import streamlit as st
# Functions definitions to access the useful data

SALAS = ['CBA', 'CHT', 'ROA', 'SGA', 'TGU', 'SPS']


def getData() -> pd.DataFrame:
    return pd.read_feather('tenure.feather')


def graphBalance(salas, agencies, atm, transport, total):

    figure = go.Figure()
    figure.add_trace(go.Bar(x=salas['date'], y=salas['hnl'], name='Salas', marker={'color':'midnightblue'}))
    figure.add_trace(go.Bar(x=agencies['date'], y=agencies['hnl'], name='Agencias', marker={'color':'yellowgreen'}))
    figure.add_trace(go.Bar(x=atm['date'], y=atm['hnl'], name='ATM', marker={'color':'orange'}))
    figure.add_trace(go.Bar(x=transport['date'], y=transport['hnl'], name='Transporte', marker={'color':'deepskyblue'}))

    figure.add_scatter(x = total['date'], y=total['hnl'], mode="markers", opacity=0.8,
                    # marker={'symbol': 'square'},
                    line={'color':'tan'},
                    name='Total')

    figure.update_layout(barmode='relative', title_text='Saldos totales por día')
    return figure


# read an preprocess the necessary data from the agency balance
def get_agencies_balances(agency_file):

    salas_hnl, salas_usd, salas_eur = 0, 0, 0
    agencies_hnl, agencies_usd, agencies_eur = 0, 0, 0
    # file_name = agency_file.split('_')

    balance = {
        'date':[],
        'type':[],
        'hnl':[],
    }   
    parent_path = pathlib.Path(__file__).parent.parent.resolve()           
    save_path = os.path.join(parent_path, "data")
    complete_name = os.path.join(save_path, agency_file.name)

    file = StringIO(agency_file.getvalue().decode("utf-8"))
    reader = csv.reader(file, delimiter=';')
    for row in reader:
        # this eliminates the first row
        if len(row) > 1:
            if row[0] == 'FECHA':
                balance.get('date').append(row[1])
                balance.get('date').append(row[1])
            elif row[0].isdigit():
                name = row[1].split()
                if name[len(name) - 1] in SALAS:
                    salas_hnl += float(row[2])
                    salas_usd += float(row[3])
                    salas_eur += float(row[4])
                else:
                    agencies_hnl += float(row[2])
                    agencies_usd += float(row[3])
                    agencies_eur += float(row[4])
                    
    balance.get('type').append('Salas')
    balance.get('type').append('Agencias')
    balance.get('hnl').append(salas_hnl)
    balance.get('hnl').append(agencies_hnl)

    file.close()

    return balance

# def get_atm_balances(atm_file):

#     atm = {
#         'date':[],
#         'type':[],
#         'hnl': [],
#     }

#     balance = {
#         'date':[],
#         'type':[],
#         'hnl':[],
#     } 
#     file = StringIO(atm_file.getvalue().decode("utf-8"))
#     reader = csv.reader(file, delimiter= ',')
#     next(reader)
#     for row in reader: 
#         date = row[2].split(" ")
#         if(len(date)>1):
#             if date[1] == '5:00': 
#                 atm.get('date').append(date[0])
#                 atm.get('type').append('ATM')
                
#                 if '-' in row[3]:
#                     atm.get('hnl').append(float('0'))  
#                 else: 
#                     atm.get('hnl').append(float(row[3]))
                    
#     file.close()
#     df_atm = pd.DataFrame(atm)
#     group_atm = df_atm.groupby('date', as_index= False).sum()

#     balance.get('date').extend(group_atm.date.tolist())
#     balance.get('type').extend( list('ATM' for x in range (len(group_atm.date))))
#     balance.get('hnl').extend(group_atm.hnl.tolist())

#     return balance

def get_atm_balances(atm_file):

    atm = {
        'date':[],
        'type':[],
        'hnl': [],
    }

    balance = {
        'date':[],
        'type':[],
        'hnl':[],
    } 
    file = StringIO(atm_file.getvalue().decode("utf-8"))
    reader = csv.reader(file, delimiter= ',')
    for row in reader: 
        date = row[2].split(" ")
        if(len(date)>1):
            if date[1] == '05:00:00': 
                atm.get('date').append(date[0])
                atm.get('type').append('ATM')
                
                if '-' in row[3]:
                    atm.get('hnl').append(float('0'))  
                else: 
                    atm.get('hnl').append(float(row[3]))
                    
    file.close()
    df_atm = pd.DataFrame(atm)
    group_atm = df_atm.groupby('date', as_index= False).sum()

    balance.get('date').extend(group_atm.date.tolist())
    balance.get('type').extend( list('ATM' for x in range (len(group_atm.date))))
    balance.get('hnl').extend(group_atm.hnl.tolist())

    return balance
                    
# Validación de los atm que tienen valores negativos a ciertas horas
def get_atm_transport(atm_file):

    atm_transport = {
        'date':[],
        'type':[],
        'hnl': [],
    }

    balance = {
        'date':[],
        'type':[],
        'hnl':[],
    } 

    actual = ['', '', '', '']

    file = StringIO(atm_file.getvalue().decode("utf-8"))
    reader = csv.reader(file, delimiter= ',')
    for row in reader:
        #skip first row
        if len(row) > 3:
            # check if it is the same atm
            if actual[1] == row[1]:
                # check if next value is greater than the actual
                if row[3] > actual[3]:
                    atm_transport.get('date').append(actual[2].split()[0])
                    atm_transport.get('type').append('Atm')
                    if float(row[3]) > 0:
                        atm_transport.get('hnl').append(float(actual[3]))
                    else:
                        atm_transport.get('hnl').append(0.0)
                        
        # creates the actual value for future comparisson
        actual = row
    
    df_atm_transport = pd.DataFrame(atm_transport)
    df_atm_transport = df_atm_transport.groupby(by=['date'], as_index=False).sum(numeric_only=True)
    balance.get('date').extend(df_atm_transport.date.tolist())
    balance.get('type').extend( list('Transporte' for x in range (len(df_atm_transport.date))))
    balance.get('hnl').extend(df_atm_transport.hnl.tolist())

    return balance