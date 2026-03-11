import streamlit as st
import requests
import pandas as pd
import yfinance as yf
from datetime import datetime

# --- 網頁設定 ---
st.set_page_config(page_title="00679B 監控中心", page_icon="📈", layout="wide")

# --- CSS 樣式優化 ---
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- 資料抓取函式 ---
def fetch_yuanta_data():
    """從元大官網抓取即時淨值與折溢價"""
    url = "https://www.yuantaetfs.com/api/StkNav"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.yuantaetfs.com/product/detail/00679B/BasicInformation'
    }
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        target = next((item for item in data if item["stk_code"] == "00679B"), None)
        return target, "Official API"
    except Exception:
        return None, "Error"

def fetch_yfinance_fallback():
    """備援方案：從 Yahoo Finance 抓取股價"""
    try:
        ticker = yf.Ticker("00679B.TWO")
        info = ticker.fast_info
        return {
            'trade_price': round(info['last_price'], 2),
            'stk_name': '元大美債20年 (備援資料)',
            'nav': '-',
            'diff_rate': '-'
        }, "Yahoo Finance"
    except Exception:
        return None, "Error"

# --- 主畫面 ---
st.title("🛡️ 00679B 元大美債20年監控儀表板")
st.caption(f"數據更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (每分鐘手動刷新一次)")

# 嘗試抓取資料
data, source = fetch_yuanta_data()
if not data:
    data, source = fetch_yfinance_fallback()

if data:
    # 顯示數據來源警告（如果是備援模式）
    if source == "Yahoo Finance":
        st.warning("⚠️ 目前無法連線至元大官網，已切換至 Yahoo Finance 備援模式（僅顯示市價）。")

    # 第一排：關鍵數據指標
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("即時市價", f"{data['trade_price']}")
    
    with col2:
        st.metric("預估淨值", f"{data['nav']}")
    
    with col3:
        # 折溢價處理
        diff = data['diff_rate']
        if diff != '-':
            diff_val = float(diff)
            color = "inverse" if diff_val > 1 else "normal"
            st.metric("折溢價率", f"{diff}%", delta=f"{diff}%", delta_color=color)
        else:
            st.metric("折溢價率", "暫無資料")

    with col4:
        st.metric("數據來源", source)

    # 投資建議區
    st.divider()
    if source == "Official API":
        diff_val = float(data['diff_rate'])
        if diff_val > 1:
            st.error(f"🚨 目前溢價達 {diff_val}%！市場過熱，買入即虧損，建議觀望。")
        elif diff_val < -0.5:
            st.success(f"💎 目前折價 {diff_val}%！價格低於淨值，適合分批佈局。")
        else:
            st.info("⚖️ 目前溢價幅度在正常範圍內。")

    # 第二排：歷史走勢圖 (使用 yfinance)
    st.subheader("📊 最近 30 日走勢圖")
    try:
        history = yf.Ticker("00679B.TWO").history(period="1mo")
        st.line_chart(history['Close'])
    except:
        st.write("暫時無法載入圖表")

else:
    st.error("❌ 無法獲取任何數據，請檢查網路連線或稍後再試。")

# --- 側邊欄控制 ---
with st.sidebar:
    st.header("控制台")
    if st.button('🔄 手動強制重新整理'):
        st.rerun()
    
    st.write("---")
    st.write("**投資小提醒**")
    st.write("1. 美債 ETF 主要受美債殖利率影響。")
    st.write("2. 溢價 > 1% 時，買入風險極高。")
    st.write("3. 2026 觀察點：Fed 利率決策。")
