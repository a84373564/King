# -*- coding: utf-8 -*-

import os
import json
import random
from datetime import datetime
from pathlib import Path

MODULE_COUNT = 500
KING_PATH = Path("~/Killcore/king_pool.json").expanduser()
PREVIOUS_PATH = Path("~/Killcore/v4_archive.json").expanduser()
SYMBOL_PATH = Path("~/Killcore/v3_selected_symbols.json").expanduser()
MODULE_PATH = Path("~/Killcore/v4_modules").expanduser()

if not MODULE_PATH.exists():
    MODULE_PATH.mkdir(parents=True)

def load_symbols():
    if SYMBOL_PATH.exists():
        with open(SYMBOL_PATH) as f:
            return json.load(f)
    return ["ETHUSDT", "BTCUSDT"]

def mutate_parameters(params, mutation_boost=False):
    new_params = {}
    for k, v in params.items():
        if isinstance(v, int):
            factor = random.uniform(0.85, 1.25) if mutation_boost else random.uniform(0.95, 1.05)
            new_params[k] = max(1, int(v * factor))
        elif isinstance(v, float):
            factor = random.uniform(0.85, 1.25) if mutation_boost else random.uniform(0.95, 1.05)
            new_params[k] = round(v * factor, 4)
        else:
            new_params[k] = v
    return new_params

def generate_module(base_mod, generation_id, symbols, stage="L1", boost=False):
    new_id = f"{base_mod['id'].split('-')[0]}-{generation_id}"
    return {
        "id": new_id,
        "symbol": random.choice(symbols),
        "strategy_type": base_mod["strategy_type"],
        "parameters": mutate_parameters(base_mod["parameters"], mutation_boost=boost),
        "virtual_capital": 1000.0,
        "parent_id": base_mod.get("id"),
        "mutate_generation": base_mod.get("mutate_generation", 0) + 1,
        "from_resurrection": base_mod.get("from_resurrection", False),
        "resurrected": base_mod.get("resurrected", False),
        "resurrection_chance": base_mod.get("resurrection_chance", 0),
        "bloodline": base_mod.get("bloodline", []) + [base_mod.get("id")],
        "mutate_stage": stage,
        "mutate_boost": boost,
        "ancestor_god_id": base_mod.get("id") if base_mod.get("is_divine") else None,
        "vengeance_mode": base_mod.get("resurrected", False),
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }

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
    print("[v4] 啟動模組生成（神血＋復仇強化版）")
    king_pool = load_json_list(KING_PATH)
    previous_modules = load_json_list(PREVIOUS_PATH)
    symbols = load_symbols()

    base_pool_L1 = []
    base_pool_L2 = []
    base_pool_L3 = []

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
        else:
            base_pool_L1.append(mod)

    if not base_pool_L1 and not base_pool_L2 and not base_pool_L3:
        print("[v4] 無有效來源，補 fallback 模組")
        base_pool_L1.append({
            "id": "fallback_X1",
            "symbol": "BTCUSDT",
            "strategy_type": "A",
            "parameters": {
                "ma_fast": 10,
                "ma_slow": 30,
                "sl_pct": 1.5,
                "tp_pct": 3.0
            }
        })

    print(f"[v4] symbols: {symbols}")
    print(f"[v4] L1來源: {len(base_pool_L1)} | L2: {len(base_pool_L2)} | L3: {len(base_pool_L3)}")

    new_modules = []
    for i in range(300):
        parent = random.choice(base_pool_L1)
        boost = parent.get("resurrected", False)
        mod = generate_module(parent, i + 1, symbols, stage="L1", boost=boost)
        save_module(mod)
        new_modules.append(mod)

    for i in range(300, 450):
        parent = random.choice(base_pool_L2 if base_pool_L2 else base_pool_L1)
        mod = generate_module(parent, i + 1, symbols, stage="L2", boost=True)
        save_module(mod)
        new_modules.append(mod)

    for i in range(450, 500):
        parent = random.choice(base_pool_L3 if base_pool_L3 else base_pool_L2)
        mod = generate_module(parent, i + 1, symbols, stage="L3", boost=True)
        mod["divine_candidate"] = True
        mod["divine_score"] = round(random.uniform(0.7, 1.0), 4)
        save_module(mod)
        new_modules.append(mod)

    print(f"[v4] 完成模組生成數量：{len(new_modules)}")

if __name__ == "__main__":
    main()
