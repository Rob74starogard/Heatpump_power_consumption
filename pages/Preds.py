import streamlit as st
import pandas as pd
import plotly.express as px
from sklearn.model_selection import train_test_split
import sklearn.metrics
import lightgbm as lgb
import matplotlib.pyplot as plt
import joblib

model = joblib.load("lgb_model.sav")

st.header("Estimation of potencial PV power to cover HP power consumption")
st.write(
    "Aim is to calculate average usage of electricity in past years based on trained model (LightGBM) to estimate power of future PV installation."
)


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


consumption = pd.DataFrame()
data = dane_pogodowe()

years = data["time"].dt.year
year = years.unique()
usage = []
yr = []
for i in year:
    data_tmp = data.loc[data["time"].dt.year == i]
    data_tmp2 = data_tmp.loc[
        (data_tmp["time"].dt.month >= 11) | (data_tmp["time"].dt.month < 4)
    ]
    sh = data_tmp2.shape[0]
    if sh >= 120:
        XX = data_tmp2[["tavg", "tmin", "tmax", "wdir", "wspd", "wpgt", "pres"]]
        result = model.predict(XX)
        value = round(result.sum(), 2)
        usage.append(value)
        yr.append(i)
consumption["yr"] = yr
consumption["usage"] = usage


fig = px.bar(
    consumption,
    x="yr",
    y="usage",
    color="usage",
    title="Predicted power consumption on past years",
    labels={"yr": "Year", "usage": "Power consumption [kWh]"},
)
st.plotly_chart(fig, use_container_width=True)


st.write(
    "Average consumtion is " + str(round(consumption["usage"].mean(), 2)) + "[kWh]."
)
st.write(
    "Based on literature and operational data from existing instalations one can assume that 1kW of PV instalation generates 900-980[kWh] per year."
)
st.write(
    "This gives approx. "
    + str(round(consumption["usage"].mean() / 940, 2))
    + "[kW] of PV instalation."
)
