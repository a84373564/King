import requests
import json
from datetime import datetime
from pathlib import Path

# === 參數設定 ===
LIMIT = 2
PRICE_MIN = 1
PRICE_MAX = 40
QUOTE_ASSET = "USDT"
MAX_CHANGE = 20.0  # % 單日最大漲跌幅
BLACKLIST_KEYWORDS = [
    "PEPE", "SHIB", "FLOKI", "DOGE", "WIF",
    "TRUMP", "MAGA", "BODEN", "INU", "ELON"
]

def fetch_symbols_from_mexc():
    try:
        url = "https://api.mexc.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[x] API 錯誤：{e}")
        return []

def filter_symbols(raw_data):
    filtered = []
    for item in raw_data:
        symbol = item.get("symbol", "")
        quote_vol = float(item.get("quoteVolume", 0))
        last_price = float(item.get("lastPrice", 0))
        percent_change = abs(float(item.get("priceChangePercent", 0)))

        # 過濾：USDT 幣對
        if not symbol.endswith(QUOTE_ASSET):
            continue
        # 價格限制
        if last_price < PRICE_MIN or last_price > PRICE_MAX:
            continue
        # 漲跌幅過大排除
        if percent_change > MAX_CHANGE:
            continue
        # 黑名單關鍵字排除
        if any(bad in symbol.upper() for bad in BLACKLIST_KEYWORDS):
            continue

        filtered.append({
            "symbol": symbol,
            "quote_volume": quote_vol,
            "price": last_price,
            "change_percent": percent_change
        })

    return filtered

def select_top_symbols(filtered_data, limit=LIMIT):
    sorted_data = sorted(filtered_data, key=lambda x: x["quote_volume"], reverse=True)
    return [s["symbol"] for s in sorted_data[:limit]]

def save_symbol_pool(symbols, output_path="~/Killcore/symbol_pool.json"):
    path = Path(output_path).expanduser()
    data = {
        "generated_at": datetime.now().isoformat(),
        "symbols": symbols,
        "limit": len(symbols),
        "filter": {
            "quoteAsset": QUOTE_ASSET,
            "price_range": [PRICE_MIN, PRICE_MAX],
            "blacklist_keywords": BLACKLIST_KEYWORDS,
            "max_daily_change_percent": MAX_CHANGE,
            "source": "mexc_api",
            "sort_by": "quoteVolume"
        },
        "system_version": "Killcore-v∞",
        "schema_version": "v2.1"
    }
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    print(f"[v2.1] 幣池產出成功：{symbols}")

if __name__ == "__main__":
    print("[v2.1] 啟動強化版選幣器（實戰模擬用）")
    raw = fetch_symbols_from_mexc()
    if not raw:
        print("[v2.1] 無法取得資料，終止")
        exit(1)
    filtered = filter_symbols(raw)
    top_symbols = select_top_symbols(filtered)
    save_symbol_pool(top_symbols)
