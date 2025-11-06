import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime

# --------------------------------------------------------------
# 🏁 CONFIGURACIÓN INICIAL
# --------------------------------------------------------------
st.set_page_config(
    page_title="Reducción de Desperdicio de Productos",
    layout="wide",
    page_icon="🧃"
)

st.title("🧃 Sistema de Reducción de Desperdicio de Productos en Supermercados")
st.markdown("""
Este dashboard forma parte del proyecto académico de **Gestión de Proyectos de Servicios Profesionales**.
Su objetivo es **analizar datos de ventas, inventario, descartes, proveedores y donaciones** para optimizar la gestión de productos y reducir el desperdicio en supermercados.
""")

# --------------------------------------------------------------
# 📂 CARGA DE DATOS
# --------------------------------------------------------------
@st.cache_data
def load_data():
    ventas = pd.read_csv("data/ventas.csv", parse_dates=["fecha"])
    inventario = pd.read_csv("data/inventario.csv", parse_dates=["fecha_vencimiento"])
    descarte = pd.read_csv("data/descarte.csv", parse_dates=["fecha"])
    proveedores = pd.read_csv("data/proveedores.csv")
    comedores = pd.read_csv("data/comedores.csv", parse_dates=["ultimo_envio"])
    return ventas, inventario, descarte, proveedores, comedores

ventas, inventario, descarte, proveedores, comedores = load_data()

# --------------------------------------------------------------
# 🔍 FILTROS LATERALES
# --------------------------------------------------------------
st.sidebar.header("📊 Filtros")
sucursal = st.sidebar.selectbox("Seleccionar sucursal:", ["Todas"] + sorted(ventas["sucursal"].unique().tolist()))
categoria = st.sidebar.selectbox("Seleccionar categoría:", ["Todas"] + sorted(ventas["categoria"].unique().tolist()))
dias_venc = st.sidebar.slider("Filtrar productos próximos a vencer (días)", 1, 10, 3)

# Aplicar filtros
if sucursal != "Todas":
    ventas = ventas[ventas["sucursal"] == sucursal]
    inventario = inventario[inventario["sucursal"] == sucursal]
    descarte = descarte[descarte["sucursal"] == sucursal]

if categoria != "Todas":
    ventas = ventas[ventas["categoria"] == categoria]
    inventario = inventario[inventario["categoria"] == categoria]
    descarte = descarte[descarte["producto"].isin(ventas["producto"].unique())]

# --------------------------------------------------------------
# 🧮 KPIs
# --------------------------------------------------------------
total_ventas = ventas["cantidad"].sum()
total_descartes = descarte["cantidad"].sum()
porcentaje_merma = (total_descartes / total_ventas * 100) if total_ventas > 0 else 0
productos_vencer = inventario.copy()
productos_vencer["fecha_vencimiento"] = pd.to_datetime(productos_vencer["fecha_vencimiento"], errors="coerce")
hoy = pd.Timestamp.now().normalize()
productos_vencer["dias_para_vencer"] = (productos_vencer["fecha_vencimiento"] - hoy).dt.days
prox_vencer = productos_vencer[productos_vencer["dias_para_vencer"] <= dias_venc]

col1, col2, col3, col4 = st.columns(4)
col1.metric("🛒 Ventas Totales", f"{total_ventas:,}")
col2.metric("🗑️ Productos Descartados", f"{total_descartes:,}")
col3.metric("📉 % de Merma", f"{porcentaje_merma:.2f}%")
col4.metric("⏳ Próximos a Vencer", len(prox_vencer))

st.markdown("---")

# --------------------------------------------------------------
# 📈 GRÁFICOS PRINCIPALES
# --------------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Desperdicio", "📦 Inventario", "💰 Ventas", "🍽️ Donaciones"])

with tab1:
    st.subheader("📊 Descarte por Sucursal")
    merma = descarte.groupby("sucursal")["cantidad"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(7,4))
    sns.barplot(data=merma, x="sucursal", y="cantidad", palette="coolwarm", ax=ax)
    ax.set_title("Cantidad de productos descartados por sucursal")
    st.pyplot(fig)

    st.subheader("🥇 Top 10 productos con mayor descarte")
    top = descarte.groupby("producto")["cantidad"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top)

with tab2:
    st.subheader("📦 Productos próximos a vencer")
    st.dataframe(prox_vencer[["producto","categoria","sucursal","stock","fecha_vencimiento","dias_para_vencer"]])

with tab3:
    st.subheader("💰 Ventas por categoría")
    ventas_cat = ventas.groupby("categoria")["cantidad"].sum().sort_values(ascending=False)
    st.bar_chart(ventas_cat)

    st.subheader("📅 Ventas diarias")
    ventas_diarias = ventas.groupby("fecha")["cantidad"].sum()
    st.line_chart(ventas_diarias)

with tab4:
    st.subheader("🍽️ Registro de comedores comunitarios")
    st.dataframe(comedores)
    st.map(
        pd.DataFrame({
            'lat': [-27.7833, -27.7835, -27.7810],
            'lon': [-64.2667, -64.2700, -64.2500],
            'nombre': comedores["nombre"]
        }),
        zoom=12
    )

# --------------------------------------------------------------
# 🧾 CONCLUSIÓN
# --------------------------------------------------------------
st.markdown("""
---
### 🎯 Conclusiones
Este prototipo demuestra cómo el uso de **datos y visualización analítica** puede apoyar la toma de decisiones en supermercados para:
- Detectar productos próximos a vencerse.
- Reducir el desperdicio mediante ofertas o donaciones.
- Analizar las diferencias de comportamiento entre sucursales.
- Promover la responsabilidad social mediante la colaboración con comedores locales.

💡 **Próximos pasos:** incorporar un modelo predictivo de demanda y un sistema de alertas automatizado.
""")
