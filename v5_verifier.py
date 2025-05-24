import os
import json
import random
from datetime import datetime
from pathlib import Path

MODULE_PATH = Path("~/Killcore/v4_modules").expanduser()
KING_PATH = Path("~/Killcore/king_pool.json").expanduser()
RESULT_PATH = Path("~/Killcore/v5_result.json").expanduser()

# === 模擬市場場型 ===
MARKET_SCENARIOS = ["high_volatility", "low_volatility", "trend_up", "range_chop"]

# === 模擬引擎（隨機市場 + 策略參數判定） ===
def simulate_module(mod):
    scenario = random.choice(MARKET_SCENARIOS)
    params = mod["parameters"]
    strategy = mod["strategy_type"]

    # 基礎模擬參數（可對應實際策略架構）
    base_return = {
        "A": random.uniform(1.0, 4.0),
        "B": random.uniform(0.5, 3.5),
        "C": random.uniform(0.8, 2.8)
    }[strategy]

    drawdown = random.uniform(0.8, 3.5)
    win_rate = random.uniform(50, 80)
    trade_count = random.randint(8, 20)

    # 場型對報酬修正
    if scenario == "trend_up" and strategy == "A":
        base_return += 1.5
    elif scenario == "low_volatility" and strategy == "C":
        base_return -= 1.0

    # 分數計算核心
    sharpe = round(base_return / drawdown, 2)
    return_pct = round(base_return, 2)
    score = round(return_pct * 0.5 + sharpe * 10 + win_rate * 0.3 - drawdown * 5, 2)

    # 模組類型判定
    if drawdown > 3.0:
        behavior = "爆倉型"
    elif return_pct < 1.0:
        behavior = "慢熱型"
    else:
        behavior = "穩定型"

    # 模擬錯誤記憶判定
    fail_reason = []
    if return_pct < 1.0:
        fail_reason.append("未觸 TP")
    if drawdown > 3.0:
        fail_reason.append("止損過大")
    if sharpe < 0.5:
        fail_reason.append("風險報酬比過低")

    mod.update({
        "return_pct": return_pct,
        "drawdown": drawdown,
        "sharpe": sharpe,
        "win_rate": round(win_rate, 2),
        "trade_count": trade_count,
        "score": score,
        "market_scenario": scenario,
        "strategy_behavior": behavior,
        "fail_reasons": fail_reason,
        "validated": True,
        "updated_at": datetime.now().isoformat()
    })

    return mod
# === 模組結果處理 + 王者決選 ===
def evaluate_modules():
    if not MODULE_PATH.exists():
        print("[v5] 找不到模組資料夾，請先執行 v4")
        return

    all_mods = []
    for file in MODULE_PATH.glob("*.json"):
        with file.open() as f:
            mod = json.load(f)
            mod = simulate_module(mod)
            all_mods.append(mod)

    # 分數排序
    sorted_mods = sorted(all_mods, key=lambda x: x["score"], reverse=True)
    for rank, mod in enumerate(sorted_mods, start=1):
        mod["score_rank"] = rank
        mod["is_king"] = (rank == 1)
        mod["eliminated"] = (rank > 1)

    # 寫回每隻模組
    for mod in sorted_mods:
        mod_path = MODULE_PATH / f"{mod['id']}.json"
        with mod_path.open("w") as f:
            json.dump(mod, f, indent=2)

    # 寫入王者池
    top_king = sorted_mods[0]
    top_king["king_rounds"] = top_king.get("king_rounds", 0) + 1
    top_king["has_divine_protection"] = True

    with KING_PATH.open("w") as f:
        json.dump([top_king], f, indent=2)

    print(f"[v5] 王者誕生：{top_king['id']}（Score: {top_king['score']}）")

    return sorted_mods

# === 輸出模擬報表 ===
def write_result_report(mods):
    behavior_map = {}
    strategy_score = {}
    for mod in mods:
        b = mod["strategy_behavior"]
        behavior_map[b] = behavior_map.get(b, 0) + 1
        s = mod["strategy_type"]
        strategy_score[s] = strategy_score.get(s, []) + [mod["score"]]

    strategy_avg = {k: round(sum(v)/len(v), 2) for k, v in strategy_score.items()}
    report = {
        "timestamp": datetime.now().isoformat(),
        "total_modules": len(mods),
        "average_score": round(sum(m["score"] for m in mods) / len(mods), 2),
        "behavior_distribution": behavior_map,
        "average_score_per_strategy": strategy_avg
    }

    with RESULT_PATH.open("w") as f:
        json.dump(report, f, indent=2)
    print(f"[v5] 報表已輸出：{RESULT_PATH.name}")

# === 主流程入口 ===
if __name__ == "__main__":
    print("[v5] 啟動 Killcore 模擬驗證場")
    mods = evaluate_modules()
    write_result_report(mods)
