import os
import json
import random
from datetime import datetime
from pathlib import Path
from shutil import rmtree, copytree

# === 路徑設定 ===
MODULE_PATH = Path("~/Killcore/v4_modules").expanduser()
ARCHIVE_PATH = Path("~/Killcore/archive").expanduser()
REPORT_PATH = Path("~/Killcore/v4_report.json").expanduser()
KING_PATH = Path("~/Killcore/king_pool.json").expanduser()
STRATEGY_PLAN_PATH = Path("~/Killcore/v3_symbol_log.json").expanduser()

# === 全域常數 ===
TOTAL_MODULES = 500
MAX_KINGS = 3
STRATEGY_THEMES = ["balanced", "defensive", "breakout"]
PARAM_SPACE = {
    "ma_fast": (5, 20),
    "ma_slow": (30, 100),
    "sl_pct": (1.0, 5.0),
    "tp_pct": (3.0, 10.0)
}
MUTATION_WEIGHTS = {
    "ma_fast": 0.9,
    "ma_slow": 0.8,
    "sl_pct": 0.7,
    "tp_pct": 0.6
}

# === 模組初始化 ===
def generate_parameters(seed=None):
    params = {}
    mutated = []
    for key, (low, high) in PARAM_SPACE.items():
        if seed and random.random() < 0.5:
            base = seed["parameters"][key]
            jitter = (high - low) * 0.1
            new_val = max(low, min(high, base + random.uniform(-jitter, jitter)))
            if new_val != base:
                mutated.append(key)
            params[key] = round(new_val, 2)
        else:
            params[key] = round(random.uniform(low, high), 2)
            mutated.append(key)
    return params, mutated

# === 模組 ID 編碼器 ===
def make_module_id(strategy, idx):
    return f"{strategy.lower()}-{idx + 1}"

# === 模組主體建構 ===
def build_module(symbol, strategy, idx, parent=None, generation=1):
    theme = random.choice(STRATEGY_THEMES)
    parameters, mutated = generate_parameters(parent)
    module = {
        "id": make_module_id(strategy, idx),
        "symbol": symbol,
        "strategy_type": strategy,
        "parameters": parameters,
        "mutated_fields": mutated,
        "parent_id": parent["id"] if parent else None,
        "mutate_generation": generation if parent else 0,
        "strategy_theme": theme,
        "validated": False,
        "resurrected": False,
        "from_resurrection": False,
        "resurrection_chance": 0.0,
        "has_divine_protection": False,
        "created_at": datetime.now().isoformat(),
        "system_version": "Killcore-v∞",
        "schema_version": "v2.0"
    }
    return module

# === 載入王者模組（最多三隻） ===
def load_kings():
    if not KING_PATH.exists():
        return []
    with KING_PATH.open() as f:
        all_kings = json.load(f)
    kings = [k for k in all_kings if not k.get("eliminated", False)]
    kings = sorted(kings, key=lambda k: k["score"], reverse=True)
    return kings[:MAX_KINGS]
# === 模組生成主控器 ===
def generate_modules():
    if not STRATEGY_PLAN_PATH.exists():
        print("[v4] 無法載入策略分配表，請先執行 v3")
        return

    # 清除現有模組資料夾並重建
    if MODULE_PATH.exists():
        rmtree(MODULE_PATH)
    MODULE_PATH.mkdir(parents=True)

    # 載入分配表
    with STRATEGY_PLAN_PATH.open() as f:
        plans = json.load(f)[-1]["symbols"]

    kings = load_kings()
    king_pool = kings * (TOTAL_MODULES // 2 // max(len(kings), 1))  # 平均分配王者參與

    all_modules = []
    module_counts = {}
    idx_counters = {"A": 0, "B": 0, "C": 0}

    for plan in plans:
        symbol = plan["symbol"]
        strategy = plan["strategy_type"]
        count = plan["module_count"]

        for i in range(count):
            use_king = (random.random() < 0.5 and len(king_pool) > 0)
            parent = random.choice(king_pool) if use_king else None
            mod = build_module(symbol, strategy, idx_counters[strategy], parent)
            idx_counters[strategy] += 1
            all_modules.append(mod)

            # 寫入模組檔案
            mod_path = MODULE_PATH / f"{mod['id']}.json"
            with mod_path.open("w") as f:
                json.dump(mod, f, indent=2)

    print(f"[v4] 模組生成完成，共 {len(all_modules)} 隻")

    return all_modules, kings

# === 備份模組資料夾 ===
def backup_modules():
    today = datetime.now().strftime("v4_%Y%m%d")
    archive_folder = ARCHIVE_PATH / today
    if archive_folder.exists():
        rmtree(archive_folder)
    copytree(MODULE_PATH, archive_folder)
    print(f"[v4] 模組備份完成：{archive_folder.name}")

# === 輸出突變報表 ===
def write_report(modules, kings):
    strategy_count = {"A": 0, "B": 0, "C": 0}
    theme_count = {"balanced": 0, "defensive": 0, "breakout": 0}
    field_count = {}

    for mod in modules:
        strategy_count[mod["strategy_type"]] += 1
        theme_count[mod["strategy_theme"]] += 1
        for field in mod["mutated_fields"]:
            field_count[field] = field_count.get(field, 0) + 1

    report = {
        "timestamp": datetime.now().isoformat(),
        "kings_used": [k["id"] for k in kings],
        "strategies": strategy_count,
        "themes": theme_count,
        "mutated_fields": field_count
    }

    with REPORT_PATH.open("w") as f:
        json.dump(report, f, indent=2)
    print(f"[v4] 報表已產出：{REPORT_PATH.name}")

# === 執行入口 ===
if __name__ == "__main__":
    print("[v4] 啟動 Killcore 模組鍛爐")
    modules, kings = generate_modules()
    backup_modules()
    write_report(modules, kings)
