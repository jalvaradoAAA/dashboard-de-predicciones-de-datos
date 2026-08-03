import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Principales empresas del SP IPSA
IPSA_TICKERS = {
    'Banco de Chile': 'CHILE.SN',
    'SQM-B': 'SQM-B.SN',
    'Copec': 'COPEC.SN',
    'CMPC': 'CMPC.SN',
    'Enel Chile': 'ENELCHILE.SN',
    'BCI': 'BCI.SN',
    'Falabella': 'FALABELLA.SN'
}

def get_stock_data(ticker, period="2y"):
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    return df, stock.info

def get_dividends_info(ticker):
    stock = yf.Ticker(ticker)
    dividends = stock.dividends
    if not dividends.empty:
        # Calcular Dividend Yield anual aproximado
        last_price = stock.history(period="1d")['Close'].iloc[-1]
        annual_div = dividends.tail(4).sum()
        div_yield = (annual_div / last_price) * 100
        return dividends, div_yield
    return pd.Series(), 0.0