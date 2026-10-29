import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import time
import pandas as pd

from data_fetcher import get_realtime_spot, get_stock_hist, get_cls_news
from quant_model import multi_factor_score
from selector import select_sh_stocks

st.set_page_config(page_title="上证全市场量化AI", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("条件设置")
min_score = st.sidebar.slider("最低综合评分", 50, 90, 68)
min_mktcap = st.sidebar.number_input("最低市值(亿)", 5.0, 1000.0, 25.0)
max_pe = st.sidebar.number_input("最高动态市盈率", 0, 300, 80)
exclude_st = st.sidebar.checkbox("排除ST/*ST", True)
top_n = st.sidebar.slider("输出数量", 10, 50, 20)
period = st.sidebar.selectbox("K线周期", ["daily", "5", "15", "30", "60"], index=0)
run_btn = st.sidebar.button("开始全上证选股", type="primary")
code_input = st.sidebar.text_input("个股代码（如600000）", "")
auto_refresh = st.sidebar.checkbox("自动刷新(60秒)", False)

st.title("上证全市场量化AI")
st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | 仅供学习研究")

tab1, tab2, tab3 = st.tabs(["智能选股", "个股深度分析", "市场新闻"])

with tab1:
    if run_btn:
        with st.spinner("正在扫描全上证股票，请耐心等待..."):
            try:
                result = select_sh_stocks(
                    min_score=min_score,
                    min_mktcap=min_mktcap,
                    max_pe=max_pe if max_pe > 0 else None,
                    exclude_st=exclude_st,
                    top_n=top_n,
                    period=period
                )
                st.session_state["select_result"] = result
            except Exception as e:
                st.error(f"选股出错: {e}")
                st.session_state["select_result"] = pd.DataFrame()

    if "select_result" in st.session_state:
        df = st.session_state["select_result"]
        if not df.empty:
            st.success(f"共选出 {len(df)} 只股票")
            st.dataframe(df, use_container_width=True)
            csv = df.to_csv(index=False).encode("utf-8-sig")
            st.download_button("下载CSV", csv, "select.csv", "text/csv")
        else:
            st.info("没有符合条件的股票，请放宽条件再试")
    else:
        st.info("请点击左侧「开始全上证选股」按钮")

with tab2:
    if code_input:
        hist = get_stock_hist(code_input)
        if not hist.empty:
            score = multi_factor_score(hist)
            c1, c2, c3, c4, c5 = st.columns(5)
            c1.metric("综合评分", score["综合评分"])
            c2.metric("动量", score["动量"])
            c3.metric("形态", score["形态"])
            c4.metric("趋势", score["趋势"])
            c5.metric("量价", score["量价"])
            st.write("信号：", " | ".join(score["信号"]))
            
            fig = go.Figure(data=[go.Candlestick(
                x=hist["date"], open=hist["open"], high=hist["high"],
                low=hist["low"], close=hist["close"]
            )])
            fig.update_layout(height=450, xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.error("获取数据失败")
    else:
        st.write("请在左侧输入股票代码")

with tab3:
    st.subheader("财联社新闻")
    news_list = get_cls_news(15)
    for n in news_list:
        st.markdown(f"**{n['time']}** {n['title']}")

if auto_refresh:
    time.sleep(60)
    st.rerun()
