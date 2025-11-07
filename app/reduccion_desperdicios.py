import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# --------------------------------------------------------------
# ⚙️ CONFIGURACIÓN GENERAL
# --------------------------------------------------------------
st.set_page_config(
    page_title="Reducción de Desperdicio de Productos",
    page_icon="🧃",
    layout="wide",
)

# --------------------------------------------------------------
# 🎨 CONFIGURACIÓN VISUAL PERSONALIZADA
# --------------------------------------------------------------

# Fondo blanco, texto negro y títulos en color institucional
st.markdown("""
    <style>
        /* Fondo general */
        .stApp {
            background-color: #434545;
            color: #ffffff;
        }

        /* Encabezados principales */
        h1, h2, h3 {
            color: #1f1d1d; /* negro adaptado */
            font-weight: 700;
        }

        /* Tablas */
        .stDataFrame, .dataframe {
            background-color: #1f1d1d;
            color: #1f1d1d;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] {
            background-color: #b4bdb3;
            color: #343d31;
        }

       /* KPI base */
        div[data-testid="metric-container"] {
            border-radius: 14px;
            padding: 12px;
            color: white;
            font-weight: bold;
            text-align: center;
        }
        
        /* Primera métrica (ventas) */
        div[data-testid="metric-container"]:nth-child(1) {
            background-color: #0072B2; /* Azul */
        }
        
        /* Segunda métrica (valor total) */
        div[data-testid="metric-container"]:nth-child(2) {
            background-color: #009E73; /* Verde */
        }
        
        /* Tercera métrica (descartes) */
        div[data-testid="metric-container"]:nth-child(3) {
            background-color: #D55E00; /* Naranja/rojo */
        }
        
        /* Cuarta métrica (merma) */
        div[data-testid="metric-container"]:nth-child(4) {
            background-color: #E69F00; /* Amarillo */
        }
        
        /* Quinta métrica (donaciones) */
        div[data-testid="metric-container"]:nth-child(5) {
            background-color: #56B4E9; /* Celeste */
        }



        /* Texto de botones y encabezados */
        .stButton>button {
            color: #000000;
            background-color: #0072B2;
            border-radius: 8px;
            border: none;
        }
        .stButton>button:hover {
            background-color: #005f91;
        }

        /* Links y markdown */
        a {
            color: #1f1d1d !important;
            text-decoration: none;
        }

        /* Ajustes para gráficos de Plotly/Altair */
        .js-plotly-plot, .vega-embed {
            background-color: #FFFFFF !important;
        }
    </style>
""", unsafe_allow_html=True)


# --------------------------------------------------------------
# 🧩 TÍTULO Y DESCRIPCIÓN
# --------------------------------------------------------------
st.markdown('<p class="big-font">🧃 Sistema de Reducción de Desperdicio de Productos</p>', unsafe_allow_html=True)
st.write("""
Proyecto académico desarrollado en el marco de la **Tecnicatura en Ciencia de Datos e Inteligencia Artificial**.
Este dashboard permite analizar **ventas, inventario, desperdicio y donaciones**, contribuyendo a la eficiencia operativa y la responsabilidad social.
""")

# --------------------------------------------------------------
# 📂 CARGA DE DATOS
# --------------------------------------------------------------
@st.cache_data
def load_data():
    try:
        ventas = pd.read_csv("data/ventas.csv", parse_dates=["fecha"])
        inventario = pd.read_csv("data/inventario.csv", parse_dates=["fecha_vencimiento"])
        descarte = pd.read_csv("data/descarte.csv", parse_dates=["fecha"])
        proveedores = pd.read_csv("data/proveedores.csv")
        comedores = pd.read_csv("data/comedores.csv", parse_dates=["ultimo_envio"])
        return ventas, inventario, descarte, proveedores, comedores
    except Exception as e:
        st.error(f"⚠️ Error al cargar los archivos CSV: {e}")
        st.stop()

ventas, inventario, descarte, proveedores, comedores = load_data()

# --------------------------------------------------------------
# 🔍 FILTROS LATERALES
# --------------------------------------------------------------
st.sidebar.header("📊 Filtros de análisis")
sucursal = st.sidebar.selectbox("Sucursal", ["Todas"] + sorted(ventas["sucursal"].unique()))
categoria = st.sidebar.selectbox("Categoría", ["Todas"] + sorted(ventas["categoria"].unique()))
dias_venc = st.sidebar.slider("Productos próximos a vencer (días)", 1, 10, 3)

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
# 🧮 CÁLCULO DE INDICADORES
# --------------------------------------------------------------
total_ventas = ventas["cantidad"].sum()
total_descartes = descarte["cantidad"].sum()
valor_ventas = (ventas["cantidad"] * ventas["precio_unitario"]).sum()
valor_descartes = np.random.uniform(0.7, 1.0) * total_descartes * 500  # valor estimado de pérdida
porcentaje_merma = (total_descartes / total_ventas * 100) if total_ventas > 0 else 0

# Fecha de vencimiento
inventario["fecha_vencimiento"] = pd.to_datetime(inventario["fecha_vencimiento"], errors="coerce")
inventario["dias_para_vencer"] = (inventario["fecha_vencimiento"] - pd.Timestamp.now().normalize()).dt.days
prox_vencer = inventario[inventario["dias_para_vencer"] <= dias_venc]

# Productos perecederos vs no perecederos (estimado)
perecederos = inventario[inventario["categoria"].str.contains("lácteos|frutas|verduras|carne|pan", case=False)]
no_perecederos = inventario.drop(perecederos.index)

tasa_donacion = (comedores["cantidad_donaciones"].sum() / total_descartes * 100) if total_descartes > 0 else 0

# --------------------------------------------------------------
# ⚡ ALERTAS AUTOMÁTICAS
# --------------------------------------------------------------
if porcentaje_merma > 20:
    st.error("🚨 Nivel de merma elevado: revisar gestión de stock.")
elif len(prox_vencer) > 50:
    st.warning("⚠️ Muchos productos próximos a vencer.")
else:
    st.success("✅ Nivel de desperdicio controlado.")

# --------------------------------------------------------------
# 💡 INDICADORES CLAVE (KPIs)
# --------------------------------------------------------------
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("🛒 Ventas Totales", f"{total_ventas:,}")
col2.metric("💰 Valor Total de Ventas", f"${valor_ventas:,.0f}")
col3.metric("🗑️ Productos Descartados", f"{total_descartes:,}")
col4.metric("📉 % de Merma", f"{porcentaje_merma:.2f}%")
col5.metric("🍽️ Tasa de Donación", f"{tasa_donacion:.1f}%")
st.markdown("---")

# --------------------------------------------------------------
# 📊 SECCIONES PRINCIPALES
# --------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Ventas y Rotación", "📦 Inventario y Vencimientos",
    "🗑️ Desperdicio y Merma", "🍽️ Donaciones", "📘 Conclusiones"
])

# --------------------------------------------------------------
# TAB 1: VENTAS Y ROTACIÓN
# --------------------------------------------------------------
with tab1:
    st.subheader("📈 Evolución de Ventas")

    ventas_diarias = ventas.groupby("fecha")["cantidad"].sum().reset_index()
    st.line_chart(ventas_diarias, x="fecha", y="cantidad")

    st.subheader("🏷️ Ventas por Categoría")
    ventas_cat = ventas.groupby("categoria")["cantidad"].sum().sort_values(ascending=False)
    st.bar_chart(ventas_cat)

    st.subheader("📍 Ventas por Sucursal")
    ventas_suc = ventas.groupby("sucursal")["cantidad"].sum()
    st.bar_chart(ventas_suc)

# --------------------------------------------------------------
# TAB 2: INVENTARIO Y VENCIMIENTOS
# --------------------------------------------------------------
with tab2:
    st.subheader("📦 Productos próximos a vencer")
    st.dataframe(prox_vencer[["producto","categoria","sucursal","stock","fecha_vencimiento","dias_para_vencer"]])

    fig, ax = plt.subplots(figsize=(6,4))
    plt.pie([len(perecederos), len(no_perecederos)], labels=["Perecederos","No perecederos"], autopct='%1.1f%%')
    ax.set_title("Distribución de productos por tipo")
    st.pyplot(fig)

# --------------------------------------------------------------
# TAB 3: DESPERDICIO Y MERMA
# --------------------------------------------------------------
with tab3:
    st.subheader("🗑️ Descarte por sucursal")
    merma = descarte.groupby("sucursal")["cantidad"].sum().reset_index()
    fig, ax = plt.subplots(figsize=(7,4))
    sns.barplot(data=merma, x="sucursal", y="cantidad", palette="Reds", ax=ax)
    ax.set_title("Cantidad de productos descartados por sucursal")
    st.pyplot(fig)

    st.subheader("🔥 Heatmap: Desperdicio por categoría y sucursal")
    pivot = descarte.pivot_table(values='cantidad', index='categoria', columns='sucursal', aggfunc='sum', fill_value=0)
    fig, ax = plt.subplots(figsize=(7,4))
    sns.heatmap(pivot, cmap="YlOrRd", annot=True, fmt=".0f")
    st.pyplot(fig)

    st.subheader("🥇 Top 10 productos más descartados")
    top = descarte.groupby("producto")["cantidad"].sum().sort_values(ascending=False).head(10)
    st.bar_chart(top)

# --------------------------------------------------------------
# TAB 4: DONACIONES
# --------------------------------------------------------------
with tab4:
    st.subheader("🍽️ Registro de Comedores Comunitarios")

    if comedores.empty:
        st.info("ℹ️ No hay registros de comedores disponibles.")
    else:
        # 📋 Mostrar tabla de comedores
        st.dataframe(comedores[["nombre","direccion","zona","cantidad_donaciones","ultimo_envio"]])

        # 🌍 Mapa con coordenadas dinámicas generadas automáticamente
        st.markdown("### 🌍 Ubicación aproximada de comedores")
        base_lat, base_lon = -27.7833, -64.2667
        coords = pd.DataFrame({
            'nombre': comedores["nombre"],
            'lat': [base_lat + np.random.uniform(-0.01, 0.01) for _ in range(len(comedores))],
            'lon': [base_lon + np.random.uniform(-0.01, 0.01) for _ in range(len(comedores))]
        })
        st.map(coords, zoom=12)

        # 📤 Botón para descargar el CSV
        st.markdown("### 📤 Descarga de datos")
        st.download_button(
            "📥 Descargar registro de donaciones",
            comedores.to_csv(index=False).encode('utf-8'),
            "comedores.csv",
            "text/csv"
        )
# --------------------------------------------------------------
# TAB 5: CONCLUSIONES
# --------------------------------------------------------------
with tab5:
    st.subheader("📘 Conclusiones Generales")
    st.markdown("""
    - **Optimización de stock:** permite detectar productos próximos a vencer y reducir pérdidas.  
    - **Análisis de desempeño:** compara sucursales y categorías para priorizar acciones.  
    - **Responsabilidad social:** las donaciones contribuyen al impacto positivo en la comunidad.  
    - **Futuro:** integrar modelos predictivos de demanda y recomendaciones automatizadas.  
    """)
