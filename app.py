from pathlib import Path

import pandas as pd
import streamlit as st


ARCHIVO_DATOS = Path(__file__).parent / "citibike-tripdata.csv"

st.set_page_config(page_title="Bicicletas en la Ciudad", page_icon="🚲", layout="wide")


@st.cache_data
def cargar_datos(n=500):
    return pd.read_csv(ARCHIVO_DATOS, nrows=n, low_memory=False)


def preparar_datos(df):
    df = df.copy()
    columnas = {
        "started_at": ("started_at", "starttime", "start_time"),
        "started_lat": ("started_lat", "start_lat", "start_station_latitude"),
        "started_lng": ("started_lng", "start_lng", "start_station_longitude"),
    }
    for destino, opciones in columnas.items():
        if destino not in df.columns:
            origen = next((col for col in opciones if col in df.columns), None)
            if origen:
                df.rename(columns={origen: destino}, inplace=True)
    df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
    df["hora"] = df["started_at"].dt.hour
    return df


st.title("Bicicletas en la Ciudad")

with st.sidebar:
    mostrar_datos = st.checkbox("Raw datos", value=True)
    mostrar_grafica = st.checkbox("Recorridos por hora", value=False)
    hora = st.slider("Horario", min_value=0, max_value=23, value=17)

try:
    viajes = preparar_datos(cargar_datos())
except Exception as error:
    st.error("No se pudieron cargar los datos de Citi Bike.")
    st.caption(str(error))
    st.stop()

if mostrar_datos:
    st.subheader("Raw")
    st.dataframe(viajes, use_container_width=True, hide_index=True)

if mostrar_grafica:
    st.subheader("Recorridos por hora")
    conteo = viajes.groupby("hora").size().reindex(range(24), fill_value=0)
    grafica = pd.DataFrame({"Recorridos": conteo.values}, index=[f"{h:02d}:00" for h in range(24)])
    st.bar_chart(grafica, color="#0e7490")

st.subheader(f"Mapa · {hora}:00")
if {"started_lat", "started_lng", "hora"}.issubset(viajes.columns):
    puntos = viajes.loc[viajes["hora"] == hora, ["started_lat", "started_lng"]].copy()
    puntos.columns = ["lat", "lon"]
    puntos["lat"] = pd.to_numeric(puntos["lat"], errors="coerce")
    puntos["lon"] = pd.to_numeric(puntos["lon"], errors="coerce")
    puntos = puntos.dropna(subset=["lat", "lon"])
    if not puntos.empty:
        st.map(puntos, latitude="lat", longitude="lon", color="#0e7490")

st.caption("Angelica Martinez Hernandez · Mariel Cruz Hernandez")
