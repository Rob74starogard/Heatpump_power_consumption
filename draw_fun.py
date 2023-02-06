import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
from main import dane_pogodowe
from main import read_data
def draw_2trace (title_sum,name1,x1,y1,name2,x2,y2):
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
            name=name1,
            x=x1,
            y=y1,
            ))
        
        fig.add_trace(
            go.Bar(
            name=name2,
            x=x2,
            y=y2
            )
        )
        fig.update_layout(
        title=title_sum,
        xaxis_title="Date",
        legend_title="Data descripion",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"))
        return fig

if __name__=='__main__':
    dane = dane_pogodowe()
    dane2 = read_data('measurement_2752')
    data2share=dane2.merge(dane, how='inner', on='time')
    data2share['usage'] = data2share['usage'].round(1)
    data2share.rename(columns = {'time':'Date'
                                ,'usage':'Power consumption[kWh]'}, inplace = True)

    
    
    fig = draw_2trace ("Power consumption in whole heating period as function of min 24h temperature",
                        'Minimal 24h temperature [degC]'
                        ,data2share['Date'],
                        data2share['tmin'],
                        "Power consumption[kWh]",
                        data2share['Date'],
                        data2share["Power consumption[kWh]"])
    fig2 = draw_2trace ("Power consumption in whole heating period as function of min 24h temperature",'Minimal 24h temperature [degC]',data2share['Date'],data2share['tavg'],"Power consumption[kWh]",data2share['Date'],data2share["Power consumption[kWh]"])        
    st.write('All')
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)
    st.plotly_chart(fig2, theme='streamlit', use_container_width=True)

    labels = ['October','November','December','January','February']
    values = [4500, 2500, 1053, 500,90]

    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
    #fig.show()
    st.plotly_chart(fig, theme='streamlit', use_container_width=True)