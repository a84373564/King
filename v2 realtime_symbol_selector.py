import requests
import json
from datetime import datetime
from pathlib import Path

# === 設定參數 ===
LIMIT = 2
MIN_PRICE = 0.005
QUOTE_ASSET = "USDT"
BLACKLIST_KEYWORDS = ["PEPE", "SHIB", "FLOKI", "DOGE"]

def fetch_symbols_from_mexc():
    try:
        url = "https://api.mexc.com/api/v3/ticker/24hr"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"[x] API 連線失敗：{e}")
        return []

def filter_symbols(raw_data):
    filtered = []
    for item in raw_data:
        symbol = item.get("symbol", "")
        quote_vol = float(item.get("quoteVolume", 0))
        last_price = float(item.get("lastPrice", 0))

        # 條件過濾
        if not symbol.endswith(QUOTE_ASSET):
            continue
        if last_price < MIN_PRICE:
            continue
        if any(bad in symbol for bad in BLACKLIST_KEYWORDS):
            continue

        filtered.append({
            "symbol": symbol,
            "quote_volume": quote_vol
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
            "sort_by": "quoteVolume",
            "min_price": MIN_PRICE,
            "blacklist_keywords": BLACKLIST_KEYWORDS
        },
        "system_version": "Killcore-v∞",
        "schema_version": "v2.0"
    }
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    print(f"[v2] 幣池產出成功：{symbols}")

if __name__ == "__main__":
    print("[v2] 啟動 MEXC 幣池生成器")
    raw = fetch_symbols_from_mexc()
    if not raw:
        print("[v2] 無法取得幣種資料，終止")
        exit(1)
    filtered = filter_symbols(raw)
    top_symbols = select_top_symbols(filtered)
    save_symbol_pool(top_symbols)
