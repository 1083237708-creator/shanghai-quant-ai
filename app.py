import pandas as pd
import numpy as np
import ta
from typing import Dict, List

def detect_fractals(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fractal"] = 0
    for i in range(2, len(df)-2):
        h = df["high"].values
        l = df["low"].values
        if h[i] > h[i-1] and h[i] > h[i-2] and h[i] > h[i+1] and h[i] > h[i+2]:
            df.iloc[i, df.columns.get_loc("fractal")] = 1
        if l[i] < l[i-1] and l[i] < l[i-2] and l[i] < l[i+1] and l[i] < l[i+2]:
            df.iloc[i, df.columns.get_loc("fractal")] = -1
    return df

def build_bi(df: pd.DataFrame) -> List[dict]:
    fr = detect_fractals(df)
    pts = fr[fr["fractal"] != 0][["date", "high", "low", "close", "fractal"]].reset_index()
    bis = []
    for i in range(1, len(pts)):
        cur = pts.iloc[i]
        prev = pts.iloc[i-1]
        if cur["fractal"] != prev["fractal"]:
            direction = "up" if cur["fractal"] == 1 else "down"
            bis.append({
                "start_idx": int(prev["index"]),
                "end_idx": int(cur["index"]),
                "start_date": str(prev["date"]),
                "end_date": str(cur["date"]),
                "dir": direction
            })
    return bis

def dow_trend(df: pd.DataFrame) -> str:
    if len(df) < 20:
        return "数据不足"
    r = df.tail(30)
    if r["high"].iloc[-1] > r["high"].iloc[-15] and r["low"].iloc[-1] > r["low"].iloc[-15]:
        return "道氏上升趋势"
    if r["high"].iloc[-1] < r["high"].iloc[-15] and r["low"].iloc[-1] < r["low"].iloc[-15]:
        return "道氏下降趋势"
    return "道氏震荡"

def multi_factor_score(df: pd.DataFrame) -> dict:
    if df.empty or len(df) < 40:
        return {"综合评分": 0, "信号": ["数据不足"]}
    
    df = df.copy()
    df["ma5"] = df["close"].rolling(5).mean()
    df["ma20"] = df["close"].rolling(20).mean()
    df["rsi"] = ta.momentum.RSIIndicator(df["close"]).rsi()
    
    latest = df.iloc[-1]
    mom = min(100, max(0, (latest["rsi"] - 30) * 1.5)) if not np.isnan(latest["rsi"]) else 50
    
    bis = build_bi(df)
    form = 70 if bis and bis[-1]["dir"] == "up" else 45
    
    trend_str = dow_trend(df)
    trend = 75 if "上升" in trend_str else (35 if "下降" in trend_str else 55)
    if latest["close"] > latest["ma5"] > latest["ma20"]:
        trend = min(95, trend + 15)
    
    vol_ma = df["volume"].rolling(5).mean().iloc[-1]
    vol_score = 80 if latest["volume"] > vol_ma * 1.3 else 50
    
    total = mom * 0.25 + form * 0.20 + trend * 0.30 + vol_score * 0.25
    
    signals = [trend_str]
    if total >= 70:
        signals.append("偏多关注")
    if bis and bis[-1]["dir"] == "up":
        signals.append("缠论笔向上")
    
    return {
        "综合评分": round(total, 1),
        "动量": round(mom, 1),
        "形态": round(form, 1),
        "趋势": round(trend, 1),
        "量价": round(vol_score, 1),
        "信号": signals,
        "道氏": trend_str
    }
