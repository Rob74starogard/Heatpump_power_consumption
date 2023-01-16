import streamlit as st
import pandas as pd
import numpy as np
#import matplotlib.pyplot as plt
import altair as alt
import zipfile
from meteostat import Point, Daily
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff


def read_data(file):
    pomiary = zipfile.ZipFile(file+'.zip','r')
    file_measurements = pomiary.open(file+'.csv')
    data_usage = pd.read_csv(file_measurements, usecols = ["Date and time",
                                                          'Phase 1 Forward active Energy kWh',
                                                          'Phase 2 Forward active Energy kWh',
                                                          'Phase 3 Forward active Energy kWh'])
    #s=pd.to_datetime(data_usage['Date and time'])
    data_usage['Date and time']=pd.to_datetime(data_usage['Date and time'])
    data_usage=data_usage.groupby(pd.Grouper(key='Date and time', freq='D')).max()
    output = data_usage.copy()
    faza1 = output[ 'Phase 1 Forward active Energy kWh']
    faza2 = output[ 'Phase 2 Forward active Energy kWh']
    faza3 = output[ 'Phase 3 Forward active Energy kWh']
    output['suma']=faza1+faza2+faza3

    lista=output['suma'].to_numpy()
    count=output.shape[0]
    n=1
    while n < count:
        lista[count-n] = lista[count -n] - lista[count-n-1]
        n=n+1
    output['usage'] = lista
    output=output.dropna()
    output['suma']=faza1+faza2+faza3
    output = output.loc[(output['suma']>0)]
    output['time']=output.index
    return (output)

def dane_pogodowe(data):
    start=data.index[0]
    end=data.index[data.shape[0]-1]
    stacja_pogodowa = Point(54.2112, 18.3807, 70)
    data = Daily(stacja_pogodowa, start, end)
    data = data.fetch()
    return (data)

if __name__=='__main__':
    output = read_data('measurement_2752')
    dane_pog = dane_pogodowe(output)
    print(output)
    data2share=output.merge(dane_pog, how='inner', on='time')
    data2share.rename(columns = {'time':'Date'
                                ,'usage':'Power consumption[kWh]'}, inplace = True)
    
    #print(data2share)
    st.title('Heat pump power consumption as a function of environmental variables')
    with st.expander('About...'):
        st.markdown('''This application is a try to estimate power consumption of [Panasonic](https://www.aircon.panasonic.eu/PL_pl/model/wh-mxc12h6e5/) heat pump
        based on historical measurment data. [Feel to contact](mailto:rkucharski74@gmail.com)
        ''')
    #st.header('Show input dataframe')

    if st.button('Show input dataframe'):
        st.dataframe(data2share)
    

    data_nov=data2share.loc[(data2share['Date']>='2022-11-1')&(data2share['Date']<='2022-11-30')]
    data_dec=data2share.loc[(data2share['Date']>='2022-12-1')&(data2share['Date']<='2022-12-31')]
    data_jan=data2share.loc[(data2share['Date']>='2023-01-1')&(data2share['Date']<'2023-01-15')]
    

    rozmiar=25
    
    fig = px.scatter(
        data_nov,
        x="tmin",
        y="Power consumption[kWh]",
        size="Power consumption[kWh]",
        color="Power consumption[kWh]",
        title='Summary data power usage',
        labels={
                     "tmin": "Minimal temperature [deg C]"},
        size_max=rozmiar,
    )
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)

    fig = px.scatter(
        data_dec,
        x="tmin",
        y="Power consumption[kWh]",
        size="Power consumption[kWh]",
        color="Power consumption[kWh]",
         #hover_name="country",
        size_max=rozmiar,
        title="December data power usage",
        labels={"tmin": "Minimal temperature [deg C]"})
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)

    
    fig = px.scatter(
        data_jan,
        x="tmin",
        y="Power consumption[kWh]",
        size="Power consumption[kWh]",
        color="Power consumption[kWh]",
        title='January data power usage',
        size_max=rozmiar,
        labels={
                     "tmin": "Minimal temperature [deg C]"}
    )

    st.plotly_chart(fig, theme='streamlit', use_container_width=True)



    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
        name='Minimal 24h temperature',
        x=data_jan['Date'],
        y=data_jan['tmin'],
        #color=data_jan['tmin']
        ))
    
    fig.add_trace(
        go.Bar(
        name="Power consumption[kWh]",
        x=data_jan['Date'],
        y=data_jan["Power consumption[kWh]"]
        )
    )
    fig.update_layout(
    title="Power consumption in January 2023 as function of min temperature",
    xaxis_title="Date",
    #yaxis_title="Y Axis Title",
    legend_title="Data descripion",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"))
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
        name='Minimal 24h temperature',
        x=data2share['Date'],
        y=data2share['tmin'],
        #color=data_jan['tmin']
        ))
    
    fig.add_trace(
        go.Bar(
        name="Power consumption[kWh]",
        x=data2share['Date'],
        y=data2share["Power consumption[kWh]"]
        )
    )
    fig.update_layout(
    title="Power consumption in whole heating period as function of min 24h temperature",
    xaxis_title="Date",
    #yaxis_title="Y Axis Title",
    legend_title="Data descripion",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"))
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)