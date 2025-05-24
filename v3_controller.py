import json
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# === 開關設定 ===
ENABLE_SYMBOL_MEMORY = True
ENABLE_STRATEGY_MAPPING = True
ENABLE_ALLOCATION_PLANNING = True
ENABLE_MODULE_LINEAGE = True
ENABLE_SYMBOL_HISTORY = True
ENABLE_PERFORMANCE_INTEGRATOR = True
ENABLE_STRATEGY_COMPATIBILITY_MAP = True
ENABLE_SYMBOL_CREDIBILITY_SCORER = True
ENABLE_PREDICTIVE_SIMULATOR = True
ENABLE_SELECTED_SYMBOL_EXPORT = True  # ← 為 v4 加的

# === 檔案路徑 ===
SYMBOL_POOL_PATH = Path("~/Killcore/symbol_pool.json").expanduser()
SYMBOL_LOG_PATH = Path("~/Killcore/v3_symbol_log.json").expanduser()
LINEAGE_PATH = Path("~/Killcore/v3_lineage.json").expanduser()
STRATEGY_MAP_PATH = Path("~/Killcore/v3_strategy_map.json").expanduser()
CREDIBILITY_PATH = Path("~/Killcore/v3_credibility.json").expanduser()
V4_SELECTED_SYMBOL_PATH = Path("/root/Killcore/v3_selected_symbols.json")

# === 策略建議邏輯（精準版）===
def recommend_strategies(symbol):
    if symbol == "MATICUSDT":
        return ["A", "C"]
    elif symbol == "OPUSDT":
        return ["B", "C"]
    else:
        return ["C"]

# === 模組分配器（針對雙幣動態調整）===
def allocate_module_counts(symbol):
    if symbol == "MATICUSDT":
        return {
            "A": 150,
            "C": 100
        }
    elif symbol == "OPUSDT":
        return {
            "B": 180,
            "C": 70
        }
    else:
        return {
            "C": 100
        }

# === Layer 2 ===
def build_lineage(symbols):
    lineage = {}
    for sym in symbols:
        lineage[sym] = {
            "ancestors": [],
            "mutations": [],
            "king_status": "pending"
        }
    with LINEAGE_PATH.open("w") as f:
        json.dump(lineage, f, indent=2)
    print(f"[v3-L2] 建立族譜完成：{len(lineage)} 幣種")

def log_symbol_history(timestamp, data):
    log = []
    if SYMBOL_LOG_PATH.exists():
        with SYMBOL_LOG_PATH.open("r") as f:
            log = json.load(f)
    log.append({
        "timestamp": timestamp,
        "symbols": data
    })
    with SYMBOL_LOG_PATH.open("w") as f:
        json.dump(log, f, indent=2)
    print(f"[v3-L2] 歷史記錄完成，共 {len(data)} 策略分配")

def generate_strategy_map(assignments):
    mapper = defaultdict(set)
    for entry in assignments:
        mapper[entry["strategy_type"]].add(entry["symbol"])
    out = {k: list(v) for k, v in mapper.items()}
    with STRATEGY_MAP_PATH.open("w") as f:
        json.dump(out, f, indent=2)
    print(f"[v3-L2] 策略-幣適配圖譜完成：{len(out)} 種策略")

def credibility_scoring(symbols):
    score = {sym: 100 for sym in symbols}
    with CREDIBILITY_PATH.open("w") as f:
        json.dump(score, f, indent=2)
    print(f"[v3-L2] 信譽分已固定設定為 100")

def simulate_predictive_difficulty(symbols):
    for sym in symbols:
        print(f"[v3-L2] 預測模擬：{sym} → 可能陷入低頻橫盤區間")

# === 主流程 ===
def process_symbol_pool():
    if not SYMBOL_POOL_PATH.exists():
        print("[v3] 找不到 symbol_pool.json")
        return []

    with SYMBOL_POOL_PATH.open("r") as f:
        pool = json.load(f)

    symbols = pool.get("symbols", [])
    result = []

    for symbol in symbols:
        strategies = recommend_strategies(symbol)
        allocation = allocate_module_counts(symbol)
        for strat in strategies:
            count = allocation.get(strat, 0)
            result.append({
                "symbol": symbol,
                "strategy_type": strat,
                "module_count": count
            })

    if ENABLE_SYMBOL_MEMORY:
        log_symbol_history(pool.get("generated_at", datetime.now().isoformat()), result)

    if ENABLE_MODULE_LINEAGE:
        build_lineage(symbols)

    if ENABLE_STRATEGY_COMPATIBILITY_MAP:
        generate_strategy_map(result)

    if ENABLE_SYMBOL_CREDIBILITY_SCORER:
        credibility_scoring(symbols)

    if ENABLE_PREDICTIVE_SIMULATOR:
        simulate_predictive_difficulty(symbols)

    if ENABLE_SELECTED_SYMBOL_EXPORT:
        try:
            with V4_SELECTED_SYMBOL_PATH.open("w") as f:
                json.dump(symbols, f, indent=2)
            print(f"[v3-L2] 幣種已輸出供 v4 使用：{symbols}")
        except Exception as e:
            print(f"[v3-L2] 幣種輸出失敗：{e}")

    return result

# === 執行入口 ===
if __name__ == "__main__":
    print("[v3] 啟動 Killcore v3 中樞（分層邏輯 + 全開功能）")
    assignments = process_symbol_pool()
    for a in assignments:
        print(f"{a['symbol']} → 策略 {a['strategy_type']} × {a['module_count']} 模組")
