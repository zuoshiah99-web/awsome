import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="00679B 監控中心", page_icon="📈", layout="wide")

# --- 資料抓取邏輯 ---

def fetch_yuanta():
    """來源 1：元大官網 (最準確，但雲端易被擋)"""
    url = "https://www.yuantaetfs.com/api/StkNav"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers, timeout=5)
        data = res.json()
        target = next((item for item in data if item["stk_code"] == "00679B"), None)
        if target:
            return {
                'price': float(target['trade_price']),
                'nav': float(target['nav']),
                'diff': float(target['diff_rate']),
                'source': '元大投信官網'
            }
    except: return None

def fetch_anue():
    """來源 2：鉅亨網 (對雲端友善，含折溢價)"""
    # 鉅亨網 00679B 接口
    url = "https://api.cnyes.com/media/api/v1/quote/etf/00679B"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()['data']
        # 假設資料結構，通常含 netValue(淨值) 與簡化折溢價
        return {
            'price': float(data['quote']['close']),
            'nav': float(data['netValue']),
            'diff': float(data['navChangePercent']), # 這裡通常代表折溢價率
            'source': '鉅亨網 Anue'
        }
    except: return None

def fetch_yahoo():
    """來源 3：Yahoo Finance (保底方案，僅市價)"""
    try:
        ticker = yf.Ticker("00679B.TWO")
        price = ticker.fast_info['last_price']
        return {
            'price': round(price, 2),
            'nav': "N/A",
            'diff': "N/A",
            'source': 'Yahoo Finance (僅市價)'
        }
    except: return None

# --- 執行抓取 ---
# 優先順序：元大 > 鉅亨 > Yahoo
result = fetch_yuanta()
if not result:
    result = fetch_anue()
if not result:
    result = fetch_yahoo()

# --- 介面呈現 ---
st.title("🛡️ 00679B 元大美債20年監控儀表板")
st.caption(f"數據更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if result:
    # 如果不是元大，顯示目前的備援來源
    if result['source'] != '元大投信官網':
        st.info(f"💡 目前切換至備援模式：數據來自 {result['source']}")

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("即時市價", f"${result['price']}")
    with col2:
        st.metric("預估淨值", f"${result['nav']}")
    with col3:
        diff = result['diff']
        if isinstance(diff, float):
            color = "inverse" if diff > 1 else "normal"
            st.metric("折溢價率", f"{diff}%", delta=f"{diff}%", delta_color=color)
        else:
            st.metric("折溢價率", "暫無資料")

    # 警示邏輯
    st.divider()
    if isinstance(diff, float):
        if diff > 1.0:
            st.error(f"🚨 溢價過高 ({diff}%)！目前買入風險較大。")
        elif diff < -0.5:
            st.success(f"💎 正在折價 ({diff}%)！適合分批進場。")
        else:
            st.info("⚖️ 折溢價處於合理區間。")

    # 圖表
    st.subheader("📊 走勢對照 (1個月)")
    history = yf.Ticker("00679B.TWO").history(period="1mo")
    st.line_chart(history['Close'])

else:
    st.error("所有數據源均失效，請確認網路或稍後再試。")

if st.button('🔄 立即重新整理'):
    st.rerun()
