import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from ta.momentum import RSIIndicator
from ta.trend import SMAIndicator
from modules.data_fetcher import IPSA_TICKERS, get_stock_data, get_dividends_info

st.set_page_config(page_title="Dashboard IPSA Predictor", layout="wide")

st.title("📈 Dashboard de Predicción y Estrategia - S&P IPSA Chile")
st.markdown("Visualización de puntos críticos de compra/venta y retornos por dividendos.")

# Selector de Empresa
selected_company = st.sidebar.selectbox("Seleccione Empresa del IPSA:", list(IPSA_TICKERS.keys()))
ticker = IPSA_TICKERS[selected_company]

# Cargar Datos
df, info = get_stock_data(ticker)
dividends, div_yield = get_dividends_info(ticker)

# Calcular Indicadores Técnicos
rsi_op = RSIIndicator(close=df['Close'], window=14)
df['RSI'] = rsi_op.rsi()

sma_fast = SMAIndicator(close=df['Close'], window=20)
df['SMA_20'] = sma_fast.sma_indicator()

sma_slow = SMAIndicator(close=df['Close'], window=50)
df['SMA_50'] = sma_slow.sma_indicator()

# Lógica de Puntos Críticos (Señales)
latest_price = df['Close'].iloc[-1]
latest_rsi = df['RSI'].iloc[-1]

signal = "NEUTRAL ⚪"
color = "gray"

if latest_rsi < 35 and df['SMA_20'].iloc[-1] > df['SMA_50'].iloc[-1]:
    signal = "COMPRA CRÍTICA (Oportunidad de Entrada) 🟢"
    color = "green"
elif latest_rsi > 70 or df['SMA_20'].iloc[-1] < df['SMA_50'].iloc[-1]:
    signal = "VENTA / TOMA DE GANANCIAS 🔴"
    color = "red"

# KPIs Superiores
col1, col2, col3, col4 = st.columns(4)
col1.metric("Último Precio CLP", f"${latest_price:,.2f}")
col2.metric("RSI (14 días)", f"{latest_rsi:.1f}")
col3.metric("Div. Yield Est.", f"{div_yield:.2f}%")
col4.metric("Objetivo Anual", "5.00%")

st.subheader(f"Estado Actual de Señal: :{color}[{signal}]")

# Gráfico de Precios e Indicadores
fig = go.Figure()
fig.add_trace(go.Scatter(x=df.index, y=df['Close'], mode='lines', name='Precio Cierre'))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], mode='lines', name='SMA 20 (Rápida)'))
fig.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], mode='lines', name='SMA 50 (Lenta)'))

fig.update_layout(title=f"Evolución de Precio - {selected_company}", xaxis_title="Fecha", yaxis_title="Precio (CLP)")
st.plotly_chart(fig, use_container_width=True)

# Sección de Dividendos y Riesgo
st.markdown("---")
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📋 Historial de Dividendos")
    st.write("Información obtenida en línea con los registros de la [Bolsa de Santiago](https://www.bolsadesantiago.com/detalle_indice/SP%20IPSA).")
    if not dividends.empty:
        st.dataframe(dividends.tail(10), use_container_width=True)
    else:
        st.info("No se registraron dividendos recientes para este instrumento.")

with col_right:
    st.subheader("🛡️ Regla de Gestión de Riesgo (50/50)")
    st.markdown("""
    - **Distribución de Cartera sugerida:** 50% Acciones IPSA / 50% Renta Fija (UF / Depósitos).
    - **Stop Loss Asignado:** -5% desde el punto de compra.
    - **Retorno Esperado:** Con un Dividend Yield medio del 3%-5% más apreciación de capital, alcanzar el **5% anual** es factible manteniendo un perfil conservador/moderado.
    """)