import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import hashlib
import requests

def get_realtime_spot(sh_only: bool = True) -> pd.DataFrame:
    """获取实时行情"""
    try:
        df = ak.stock_zh_a_spot_em()
        if sh_only:
            df = df[df["代码"].astype(str).str.startswith(("60", "68"))]
        df["更新时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return df
    except Exception as e:
        print("实时行情获取失败:", e)
        return pd.DataFrame()

def get_stock_hist(symbol: str, days: int = 250, adjust: str = "qfq", period: str = "daily") -> pd.DataFrame:
    """获取历史K线（支持日线和分钟）"""
    try:
        if period == "daily":
            end = datetime.now().strftime("%Y%m%d")
            start = (datetime.now() - timedelta(days=int(days*1.6))).strftime("%Y%m%d")
            df = ak.stock_zh_a_hist(symbol=symbol, period="daily", start_date=start, end_date=end, adjust=adjust)
            df = df.rename(columns={"日期": "date", "开盘": "open", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"})
        else:
            df = ak.stock_zh_a_hist_min_em(symbol=symbol, period=period, adjust=adjust)
            df = df.rename(columns={"时间": "date", "开盘": "open", "收盘": "close", "最高": "high", "最低": "low", "成交量": "volume"})
        df["date"] = pd.to_datetime(df["date"])
        return df.tail(days).reset_index(drop=True)
    except Exception as e:
        print(f"{symbol} 历史数据失败: {e}")
        return pd.DataFrame()

def get_cls_news(page_size: int = 30) -> list:
    """获取财联社新闻"""
    try:
        params = {
            "appName": "CailianpressWeb",
            "os": "web",
            "sv": "7.7.5",
            "last_time": "",
            "refresh_type": "1",
            "rn": str(page_size)
        }
        qs = "&".join(f"{k}={params[k]}" for k in sorted(params))
        sign = hashlib.md5(hashlib.sha1(qs.encode()).hexdigest().encode()).hexdigest()
        url = f"https://www.cls.cn/v1/roll/get_roll_list?{qs}&sign={sign}"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.cls.cn/"}
        r = requests.get(url, headers=headers, timeout=10)
        d = r.json()
        rows = []
        for item in (d.get("data") or {}).get("roll_data") or []:
            ts = item.get("ctime")
            t = datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S") if ts else ""
            rows.append({
                "title": item.get("title") or item.get("brief", ""),
                "content": item.get("content") or item.get("brief", ""),
                "time": t,
                "source": "财联社"
            })
        return rows
    except Exception as e:
        print("新闻获取失败:", e)
        return []
