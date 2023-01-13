import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt
import zipfile
from meteostat import Point, Daily

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
    #print(data2share)
    st.title('Heat pump power consumption as a function of environmental variables')
    with st.expander('About...'):
        st.markdown('''This application is a try to estimate power consumption of [Panasonic](https://www.aircon.panasonic.eu/PL_pl/model/wh-mxc12h6e5/) heat pump
        based on historical measurment data. [Feel to contact](mailto:rkucharski74@gmail.com)
        ''')
    #st.header('Show input dataframe')

    if st.button('Show input dataframe'):
        st.dataframe(data2share)
    
    c = alt.Chart(data2share).mark_circle().encode(x='tmin', y='usage', size='usage', color='usage', tooltip=['time', 'usage']).properties(
    title='Summary data')
    st.write(c)
    data_nov=data2share.loc[(data2share['time']>='2022-11-1')&(data2share['time']<='2022-11-30')]
    d = alt.Chart(data_nov).mark_circle().encode(x='tmin', y='usage', size='usage', color='usage', tooltip=['time', 'usage']).properties(
    title='November data')
    st.write(d)
        
        
