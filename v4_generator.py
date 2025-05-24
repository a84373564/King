# -*- coding: utf-8 -*-

import os
import json
import random
import string
from datetime import datetime
from pathlib import Path

MODULE_COUNT = 500
KING_PATH = Path("~/Killcore/king_pool.json").expanduser()
PREVIOUS_PATH = Path("~/Killcore/v4_archive.json").expanduser()
SYMBOL_PATH = Path("~/Killcore/v3_selected_symbols.json").expanduser()
MODULE_PATH = Path("~/Killcore/v4_modules").expanduser()
REPORT_PATH = Path("~/Killcore/v4_report.json").expanduser()

if not MODULE_PATH.exists():
    MODULE_PATH.mkdir(parents=True)

def load_symbols():
    if SYMBOL_PATH.exists():
        with open(SYMBOL_PATH) as f:
            data = json.load(f)
            if isinstance(data, dict) and "symbols" in data:
                return data["symbols"]
            elif isinstance(data, list):
                return data
    return ["ETHUSDT", "BTCUSDT"]

def mutate_parameters(params, mutation_boost=False, divine_damp=False):
    new_params = {}
    strength_sum = 0
    for k, v in params.items():
        scale = 0.85 if mutation_boost else 0.95
        scale_high = 1.25 if mutation_boost else 1.05
        if divine_damp:
            scale, scale_high = 0.98, 1.02
        factor = random.uniform(scale, scale_high)
        strength_sum += abs(factor - 1)
        if isinstance(v, int):
            new_params[k] = max(1, int(v * factor))
        elif isinstance(v, float):
            new_params[k] = round(v * factor, 4)
        else:
            new_params[k] = v
    return new_params, round(strength_sum / max(1, len(new_params)), 4)

def generate_module(base_mod, generation_index, symbols, stage="L1", boost=False):
    id_prefix = chr(97 + (generation_index // 50) % 26)
    new_id = f"{id_prefix}-{generation_index}"
    divine = base_mod.get("is_divine", False)
    params, strength = mutate_parameters(base_mod["parameters"], mutation_boost=boost, divine_damp=divine)

    mod = {
        "id": new_id,
        "symbol": random.choice(symbols),
        "strategy_type": base_mod["strategy_type"],
        "parameters": params,
        "mutation_strength": strength,
        "mutation_reason": stage if not boost else f"{stage}_resurrected",
        "generation_label": f"G{base_mod.get('mutate_generation', 0)+1}",
        "virtual_capital": 1000.0,
        "parent_id": base_mod.get("id"),
        "mutate_generation": base_mod.get("mutate_generation", 0) + 1,
        "from_resurrection": base_mod.get("from_resurrection", False),
        "resurrected": base_mod.get("resurrected", False),
        "resurrection_chance": base_mod.get("resurrection_chance", 0),
        "bloodline": base_mod.get("bloodline", []) + [base_mod.get("id")],
        "mutate_stage": stage,
        "mutate_boost": boost,
        "ancestor_god_id": base_mod.get("ancestor_god_id") or (base_mod.get("id") if divine else None),
        "vengeance_mode": base_mod.get("resurrected", False),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "score": base_mod.get("score", 0),
        "sharpe": base_mod.get("sharpe", 0),
        "win_rate": base_mod.get("win_rate", 0),
        "drawdown": base_mod.get("drawdown", 0),
        "type": base_mod.get("type", "未知"),
        "fail_reason": base_mod.get("fail_reason", ""),
        "fail_count": base_mod.get("fail_count", 0),
        "verified_env": base_mod.get("verified_env", "default"),
        "is_divine": divine,
        "divine_rounds": base_mod.get("divine_rounds", 0)
    }

    if mod["is_divine"]:
        mod["blood_mark"] = "godline"
    elif mod["vengeance_mode"]:
        mod["blood_mark"] = "vengeance"
    elif mod["type"] == "爆倉型":
        mod["blood_mark"] = "unstable"
    else:
        mod["blood_mark"] = "neutral"

    return mod

def load_json_list(path):
    if path.exists():
        with path.open() as f:
            return json.load(f)
    return []

def save_module(mod):
    path = MODULE_PATH / f"{mod['id']}.json"
    with path.open("w") as f:
        json.dump(mod, f, indent=2)

def main():
    print("[v4] 啟動模組生成（最終完全體 + 報表 + 血統欄位）")
    king_pool = load_json_list(KING_PATH)
    previous_modules = load_json_list(PREVIOUS_PATH)
    symbols = load_symbols()

    base_pool_L1, base_pool_L2, base_pool_L3 = [], [], []
    for mod in king_pool:
        weight = 1 + mod.get("king_rounds", 1)
        mod["is_divine"] = mod.get("is_divine", False)
        base_pool_L3.extend([mod] * weight)

    for mod in previous_modules:
        score = mod.get("score", 0)
        gen = mod.get("mutate_generation", 0)
        if mod.get("eliminated") and score > 75 and len(base_pool_L1) < 100:
            mod["from_resurrection"] = True
            mod["resurrected"] = True
            mod["resurrection_chance"] = 1.0
            base_pool_L1.append(mod)
        elif score > 85 or gen >= 3:
            base_pool_L2.append(mod)
        elif mod.get("type") != "爆倉型":
            base_pool_L1.append(mod)

    if not base_pool_L1:
        base_pool_L1.append({
            "id": "fallback_X1",
            "symbol": "BTCUSDT",
            "strategy_type": "A",
            "parameters": {
                "ma_fast": 10, "ma_slow": 30, "sl_pct": 1.5, "tp_pct": 3.0
            }
        })

    print(f"[v4] symbols: {symbols}")
    print(f"[v4] L1來源: {len(base_pool_L1)} | L2: {len(base_pool_L2)} | L3: {len(base_pool_L3)}")

    report = {"stage_counts": {"L1": 0, "L2": 0, "L3": 0}, "divine": 0, "resurrected": 0, "avg_strength": 0}
    new_modules, total_strength = [], 0

    for i in range(300):
        parent = random.choice(base_pool_L1)
        mod = generate_module(parent, i + 1, symbols, stage="L1", boost=parent.get("resurrected", False))
        save_module(mod)
        new_modules.append(mod)
        report["stage_counts"]["L1"] += 1
        total_strength += mod["mutation_strength"]
        if mod["is_divine"]: report["divine"] += 1
        if mod["resurrected"]: report["resurrected"] += 1

    for i in range(300, 450):
        parent = random.choice(base_pool_L2 if base_pool_L2 else base_pool_L1)
        mod = generate_module(parent, i + 1, symbols, stage="L2", boost=True)
        save_module(mod)
        new_modules.append(mod)
        report["stage_counts"]["L2"] += 1
        total_strength += mod["mutation_strength"]
        if mod["is_divine"]: report["divine"] += 1

    for i in range(450, 500):
        fallback_pool = base_pool_L3 if base_pool_L3 else (base_pool_L2 if base_pool_L2 else base_pool_L1)
        parent = random.choice(fallback_pool)
        mod = generate_module(parent, i + 1, symbols, stage="L3", boost=True)
        mod["divine_candidate"] = True
        mod["divine_score"] = round(random.uniform(0.7, 1.0), 4)
        save_module(mod)
        new_modules.append(mod)
        report["stage_counts"]["L3"] += 1
        total_strength += mod["mutation_strength"]
        if mod["is_divine"]: report["divine"] += 1

    report["total"] = len(new_modules)
    report["avg_strength"] = round(total_strength / len(new_modules), 5)
    report["generated_at"] = datetime.now().isoformat()

    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"[v4] 生成完成：{len(new_modules)}，報表寫入 v4_report.json")

if __name__ == "__main__":
    main()
