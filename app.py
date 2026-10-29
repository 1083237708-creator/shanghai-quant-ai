import streamlit as st
import plotly.graph_objects as go
from datetime import datetime
import time
import pandas as pd

st.set_page_config(page_title="上证全市场量化AI", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("条件栏")
min_score = st.sidebar.slider("最低评分", 50, 90, 68)
min_mktcap = st.sidebar.number_input("最低市值(亿)", 5.0, 1000.0, 25.0)
max_pe = st.sidebar.number_input("最高PE", 0, 300, 80)
exclude_st = st.sidebar.checkbox("排除ST", True)
top_n = st.sidebar.slider("输出数量", 10, 50, 20)
period = st.sidebar.selectbox("K线周期", ["daily", "5", "15", "30", "60"], index=0)
run_btn = st.sidebar.button("全上证选股", type="primary")
code_input = st.sidebar.text_input("个股代码", "")
auto = st.sidebar.checkbox("60秒刷新", False)

st.title("上证全市场量化AI（缠论+江恩+道氏+量能）")
st.caption(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " | 仅供学习研究，不构成投资建议")

tab1, tab2, tab3 = st.tabs(["选股结果", "个股分析", "使用说明"])

with tab1:
    st.info("点击左侧「全上证选股」按钮开始扫描（完整功能需要后续文件）")
    if run_btn:
        st.success("选股功能需要 data_fetcher.py 和 selector.py 文件，下一步我们继续添加")

with tab2:
    if code_input:
        st.write(f"正在分析股票：{code_input}")
        st.info("完整K线和江恩扇形需要后续文件支持")
    else:
        st.write("请在左侧输入股票代码（例如 600000）")

with tab3:
    st.markdown("""
    ### 使用说明
    1. 左侧调整条件
    2. 点击「全上证选股」
    3. 输入个股代码查看详情
    4. 本版本为手机简化启动版，后续继续添加完整模块
    """)

if auto:
    time.sleep(60)
    st.rerun()
