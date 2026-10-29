from data_fetcher import get_realtime_spot, get_stock_hist
from quant_model import multi_factor_score
from concurrent.futures import ThreadPoolExecutor, as_completed
import pandas as pd
import time

def select_sh_stocks(min_score=65, min_mktcap=20, max_pe=100, exclude_st=True,
                     top_n=20, max_workers=2, hist_days=120, period="daily"):
    """
    全上证选股
    min_mktcap 单位是亿
    """
    spot = get_realtime_spot(sh_only=True)
    if spot.empty:
        return pd.DataFrame()
    
    df = spot.copy()
    df["总市值"] = pd.to_numeric(df["总市值"], errors="coerce")
    df["市盈率-动态"] = pd.to_numeric(df["市盈率-动态"], errors="coerce")
    
    # 市值过滤（转成元）
    df = df[df["总市值"] >= min_mktcap * 1e8]
    
    if max_pe and max_pe > 0:
        df = df[(df["市盈率-动态"] > 0) & (df["市盈率-动态"] <= max_pe)]
    
    if exclude_st:
        df = df[~df["名称"].str.contains(r"ST|\*ST", na=False, regex=True)]
    
    candidates = df["代码"].astype(str).tolist()[:300]  # 限制数量防止超时
    
    results = []
    
    def process(code):
        try:
            hist = get_stock_hist(code, days=hist_days, period=period)
            if hist.empty:
                return None
            score = multi_factor_score(hist)
            if score["综合评分"] >= min_score:
                row = df[df["代码"] == code].iloc[0]
                return {
                    "代码": code,
                    "名称": row["名称"],
                    "最新价": row["最新价"],
                    "涨跌幅": row["涨跌幅"],
                    "总市值(亿)": round(row["总市值"] / 1e8, 1),
                    "综合评分": score["综合评分"],
                    "信号": " | ".join(score["信号"][:4]),
                    "动量": score["动量"],
                    "趋势": score["趋势"]
                }
        except:
            return None
        return None
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(process, c): c for c in candidates}
        for future in as_completed(futures):
            res = future.result()
            if res:
                results.append(res)
            time.sleep(0.1)
    
    if not results:
        return pd.DataFrame()
    
    result_df = pd.DataFrame(results)
    result_df = result_df.sort_values("综合评分", ascending=False).head(top_n)
    return result_df.reset_index(drop=True)
