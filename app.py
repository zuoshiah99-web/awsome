import streamlit as st
import requests
import pandas as pd
from datetime import datetime

# 設定網頁標題與圖示
st.set_page_config(page_title="00679B 美債監控中心", page_icon="📈")

st.title("🛡️ 00679B 元大美債20年 - 監控儀表板")
st.caption(f"最後更新時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def fetch_data():
    url = "https://www.yuantaetfs.com/api/StkNav"
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        # 抓取 00679B
        target = next((item for item in data if item["stk_code"] == "00679B"), None)
        return target
    except Exception as e:
        st.error(f"連線失敗: {e}")
        return None

data = fetch_data()

if data:
    # 建立三欄位顯示關鍵數據
    col1, col2, col3 = st.columns(3)
    
    price = float(data['trade_price'])
    nav = float(data['nav'])
    diff_rate = float(data['diff_rate'])

    with col1:
        st.metric("即時市價", f"${price}")
    with col2:
        st.metric("預估淨值", f"${nav}")
    with col3:
        # 如果溢價 > 1%，顯示紅色警告
        delta_color = "inverse" if diff_rate > 1 else "normal"
        st.metric("折溢價率", f"{diff_rate}%", delta=f"{diff_rate}%", delta_color=delta_color)

    # 顯示進階資訊表格
    st.divider()
    st.subheader("詳細數據詳情")
    df_display = pd.DataFrame([data])
    st.dataframe(df_display[['stk_code', 'stk_name', 'trade_price', 'nav', 'diff_rate', 'up_down']])

    # 投資小建議
    if diff_rate > 1:
        st.warning("⚠️ 目前溢價過高（超過 1%），建議冷靜一下，不要盲目追高喔！")
    elif diff_rate < 0:
        st.success("✅ 目前處於折價狀態，價格比淨值還便宜，可以列入考慮。")
    else:
        st.info("ℹ️ 目前溢價幅度合理。")
else:
    st.warning("暫時抓不到資料，可能是非盤中時間或官網維護中。")

# 按鈕手動刷新
if st.button('手動刷新數據'):
    st.rerun()