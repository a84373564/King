import json
from datetime import datetime
from pathlib import Path

# === 固定幣池設定 ===
FIXED_SYMBOLS = ["MATICUSDT", "OPUSDT"]
OUTPUT_LIMIT = 2  # 強制輸出這兩個幣

def save_symbol_pool(symbols, output_path="~/Killcore/symbol_pool.json"):
    path = Path(output_path).expanduser()
    data = {
        "generated_at": datetime.now().isoformat(),
        "symbols": symbols,
        "limit": len(symbols),
        "filter": {
            "mode": "fixed_pair",
            "symbols": symbols
        },
        "system_version": "Killcore-v∞",
        "schema_version": "v2.1-lock"
    }
    with path.open("w") as f:
        json.dump(data, f, indent=2)
    print(f"[v2.1-lock] 幣池產出成功：{symbols}")

if __name__ == "__main__":
    print("[v2.1-lock] 啟動固定雙幣輸出器")
    save_symbol_pool(FIXED_SYMBOLS[:OUTPUT_LIMIT])
