import os
import yfinance as yf
import requests
from datetime import datetime, timedelta

FRED_API_KEY = os.environ.get("FRED_API_KEY", "")
FRED_BASE_URL = "https://api.stlouisfed.org/fred/series/observations"

FRED_SERIES = {
    "fed_funds_rate":   "FEDFUNDS",
    "inflation_cpi":    "CPIAUCSL",
    "unemployment":     "UNRATE",
    "gdp_growth":       "A191RL1Q225SBEA",
    "yield_10y":        "DGS10",
    "yield_2y":         "DGS2",
    "usd_index":        "DTWEXBGS",
}

def get_fred_data() -> dict:
    """Pull latest macro indicators from FRED."""
    results = {}
    for name, series_id in FRED_SERIES.items():
        try:
            resp = requests.get(FRED_BASE_URL, params={
                "series_id":     series_id,
                "api_key":       FRED_API_KEY,
                "file_type":     "json",
                "sort_order":    "desc",
                "limit":         2,       # latest + previous for delta
            }, timeout=10)
            obs = resp.json().get("observations", [])
            if len(obs) >= 2:
                latest   = float(obs[0]["value"]) if obs[0]["value"] != "." else None
                previous = float(obs[1]["value"]) if obs[1]["value"] != "." else None
                results[name] = {
                    "value":    latest,
                    "previous": previous,
                    "delta":    round(latest - previous, 4) if latest and previous else None,
                    "date":     obs[0]["date"]
                }
            elif len(obs) == 1:
                latest = float(obs[0]["value"]) if obs[0]["value"] != "." else None
                results[name] = {"value": latest, "previous": None, "delta": None, "date": obs[0]["date"]}
        except Exception as e:
            results[name] = {"value": None, "previous": None, "delta": None, "error": str(e)}
    
    # Derived signal — yield curve (10y minus 2y); negative = inverted = recession signal
    try:
        y10 = results.get("yield_10y", {}).get("value")
        y2  = results.get("yield_2y",  {}).get("value")
        if y10 and y2:
            results["yield_curve_spread"] = round(y10 - y2, 3)
    except Exception:
        results["yield_curve_spread"] = None

    return results


def get_stock_data(tickers: list) -> dict:
    """Pull price, momentum, and basic technical indicators for a list of tickers."""
    results = {}
    for ticker in tickers:
        try:
            tk   = yf.Ticker(ticker)
            hist = tk.history(period="3mo")   # 3 months for swing trade signals
            if hist.empty:
                continue

            close     = hist["Close"]
            current   = round(float(close.iloc[-1]), 2)
            prev_day  = round(float(close.iloc[-2]), 2)
            week_ago  = round(float(close.iloc[-5]), 2) if len(close) >= 5 else None
            month_ago = round(float(close.iloc[-21]), 2) if len(close) >= 21 else None
            high_52w  = round(float(close.rolling(252).max().iloc[-1]), 2)
            low_52w   = round(float(close.rolling(252).min().iloc[-1]), 2)

            # RSI (14-day)
            delta     = close.diff()
            gain      = delta.where(delta > 0, 0).rolling(14).mean()
            loss      = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs        = gain / loss
            rsi       = round(float(100 - (100 / (1 + rs.iloc[-1]))), 1)

            # MACD (12/26/9)
            ema12     = close.ewm(span=12).mean()
            ema26     = close.ewm(span=26).mean()
            macd_line = ema12 - ema26
            signal    = macd_line.ewm(span=9).mean()
            macd_hist = round(float((macd_line - signal).iloc[-1]), 4)

            # Volume trend
            avg_vol   = hist["Volume"].rolling(20).mean().iloc[-1]
            cur_vol   = hist["Volume"].iloc[-1]
            vol_ratio = round(float(cur_vol / avg_vol), 2) if avg_vol else None

            results[ticker] = {
                "current_price": current,
                "change_1d_pct": round((current - prev_day) / prev_day * 100, 2),
                "change_1w_pct": round((current - week_ago) / week_ago * 100, 2) if week_ago else None,
                "change_1m_pct": round((current - month_ago) / month_ago * 100, 2) if month_ago else None,
                "high_52w":      high_52w,
                "low_52w":       low_52w,
                "pct_from_52w_high": round((current - high_52w) / high_52w * 100, 2),
                "rsi_14":        rsi,
                "macd_histogram": macd_hist,
                "volume_ratio":  vol_ratio,   # >1.5 = elevated volume
            }
        except Exception as e:
            results[ticker] = {"error": str(e)}

    return results


def get_market_pulse_data(tickers: list) -> dict:
    """Master function — returns all data needed for analysis."""
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "macro":     get_fred_data(),
        "stocks":    get_stock_data(tickers),
    }