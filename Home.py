import streamlit as st
import pandas as pd
import numpy as np
import zipfile
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff


def read_data(file):
    pomiary = zipfile.ZipFile(file + ".zip", "r")
    file_measurements = pomiary.open(file + ".csv")
    data_usage = pd.read_csv(
        file_measurements,
        usecols=[
            "Date and time",
            "Phase 1 Forward active Energy kWh",
            "Phase 2 Forward active Energy kWh",
            "Phase 3 Forward active Energy kWh",
        ],
    )

    data_usage["Date and time"] = pd.to_datetime(data_usage["Date and time"])
    data_usage = data_usage.groupby(pd.Grouper(key="Date and time", freq="D")).max()
    output = data_usage.copy()
    faza1 = output["Phase 1 Forward active Energy kWh"]
    faza2 = output["Phase 2 Forward active Energy kWh"]
    faza3 = output["Phase 3 Forward active Energy kWh"]
    output["suma"] = faza1 + faza2 + faza3

    lista = output["suma"].to_numpy()
    count = output.shape[0]
    n = 1
    while n < count:
        lista[count - n] = lista[count - n] - lista[count - n - 1]
        n = n + 1
    output["usage"] = lista
    output = output.dropna()
    output["suma"] = faza1 + faza2 + faza3
    output = output.loc[(output["suma"] > 0)]
    output["time"] = output.index
    return output


def dane_pogodowe():
    url = "https://bulk.meteostat.net/v2/daily/12150.csv.gz"
    data = pd.read_csv(url, compression="gzip", header=0, sep=",")
    names = [
        "time",
        "tavg",
        "tmin",
        "tmax",
        "prcp",
        "snow",
        "wdir",
        "wspd",
        "wpgt",
        "pres",
        "tsun",
    ]
    data_out = pd.DataFrame()
    for i in range(11):
        data_out[names[i]] = data.iloc[:, i]

    data_out["time"] = pd.to_datetime(data_out["time"])
    return data_out


def draw_2trace(title_sum, name1, x1, y1, name2, x2, y2):
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name=name1,
            x=x1,
            y=y1,
        )
    )

    fig.add_trace(go.Bar(name=name2, x=x2, y=y2))
    fig.update_layout(
        title=title_sum,
        xaxis_title="Date",
        legend_title="Data descripion",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )
    return fig


if __name__ == "__main__":
    rozmiar = 25
    output = read_data("measurement_2752")
    dane_pog = dane_pogodowe()
    data2share = output.merge(dane_pog, how="inner", on="time")
    data2share["usage"] = data2share["usage"].round(1)
    data2share.rename(
        columns={"time": "Date", "usage": "Power consumption[kWh]"}, inplace=True
    )
    data2share["Date"] = pd.to_datetime(data2share["Date"])

    st.set_page_config(layout="wide")

    st.title("Heat pump power consumption as a function of environmental variables")
    with st.expander("About..."):
        st.markdown(
            """This application is a try to estimate power consumption of [Panasonic](https://www.aircon.panasonic.eu/PL_pl/model/wh-mxc12h6e5/) heat pump
        based on historical measurment data. Application also contains forecast of last 16yrs.  [Feel free to contact](mailto:rkucharski74@gmail.com)
        """
        )

    st.write(
        """This applications was made to estimate power consumption of heat pump Panasonic Aquarea T-CAP 12kW.
                Main target is predict average power consumption in past 16 yrs to calculate with highest presision power of the photovoltaic \n system needed to reduce significantlly costs of house and water heating.
             """
    )
    st.write(
        """Data used: 
     Power consumption values readed via Suppla by Zamel energy counter and 
      weather data for heat pump localization (past&present)."""
    )

    first = data2share.iloc[:1, 5].dt.strftime("%d-%m-%y")
    last = data2share.iloc[-1:, 5].dt.strftime("%d-%m-%y")

    st.sidebar.header(str(first.values)[2:10] + "--> " + str(last.values)[2:10])
    all_history = st.sidebar.checkbox(
        "Power consumption and aver. 24h \n temperature by day "
    )
    all_power = st.sidebar.checkbox("Summary of power usage per month")
    temp_usage = st.sidebar.checkbox("Temperature vs usage")

    data_oct = data2share.loc[(data2share["Date"].dt.month == 10)]
    data_nov = data2share.loc[(data2share["Date"].dt.month == 11)]
    data_dec = data2share.loc[(data2share["Date"].dt.month == 12)]
    data_jan = data2share.loc[(data2share["Date"].dt.month == 1)]
    data_feb = data2share.loc[(data2share["Date"].dt.month == 2)]

    fig = draw_2trace(
        "Power consumption in whole period as function of average 24h temperature",
        "Temperature [degC], average 24h",
        data2share["Date"],
        data2share["tavg"],
        "Power consumption[kWh]",
        data2share["Date"],
        data2share["Power consumption[kWh]"],
    )

    fig3 = px.scatter(
        data2share,
        x="tmin",
        y="Power consumption[kWh]",
        size="Power consumption[kWh]",
        color="Power consumption[kWh]",
        title="Summary data power usage",
        labels={"tmin": "Minimal temperature [deg C]"},
        size_max=rozmiar,
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name="Minimal 24h temperature",
            x=data_jan["Date"],
            y=data_jan["tmin"],
        )
    )

    fig.add_trace(
        go.Bar(
            name="Power consumption[kWh]",
            x=data_jan["Date"],
            y=data_jan["Power consumption[kWh]"],
        )
    )
    fig.update_layout(
        title="Power consumption in January 2023 as function of min temperature",
        xaxis_title="Date",
        legend_title="Data descripion",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            name="Minimal 24h temperature [degC]",
            x=data2share["Date"],
            y=data2share["tmin"],
        )
    )

    fig.add_trace(
        go.Bar(
            name="Power consumption[kWh]",
            x=data2share["Date"],
            y=data2share["Power consumption[kWh]"],
        )
    )
    fig.update_layout(
        title="Power consumption in whole heating period as function of min 24h temperature",
        xaxis_title="Date",
        legend_title="Data descripion",
        font=dict(family="Courier New, monospace", size=18, color="RebeccaPurple"),
    )

    labels = ["October", "November", "December", "January", "February"]
    values = [
        data_oct["Power consumption[kWh]"].sum(),
        data_nov["Power consumption[kWh]"].sum(),
        data_dec["Power consumption[kWh]"].sum(),
        data_jan["Power consumption[kWh]"].sum(),
        data_feb["Power consumption[kWh]"].sum(),
    ]
    summary = sum(values)
    fig_power = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.35)])
    fig_power.update_layout(
        title="Power consumption per month. Summary usage : "
        + str(round(summary, 2))
        + "[kWh]."
    )

    if all_history:
        st.plotly_chart(fig, theme="streamlit", use_container_width=True)
    if all_power:
        st.plotly_chart(fig_power, theme="streamlit", use_container_width=True)
    if temp_usage:
        st.plotly_chart(fig3, theme="streamlit", use_container_width=True)
