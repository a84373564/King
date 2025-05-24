import os
import json
import random
from datetime import datetime
from pathlib import Path

MODULE_COUNT = 500
KING_PATH = Path("~/Killcore/king_pool.json").expanduser()
PREVIOUS_PATH = Path("~/Killcore/v4_archive.json").expanduser()
MODULE_PATH = Path("~/Killcore/v4_modules").expanduser()

if not MODULE_PATH.exists():
    MODULE_PATH.mkdir(parents=True)

def mutate_parameters(params, mutation_boost=False):
    new_params = {}
    for k, v in params.items():
        if isinstance(v, int):
            factor = random.uniform(0.9, 1.2) if mutation_boost else random.uniform(0.95, 1.05)
            new_params[k] = max(1, int(v * factor))
        elif isinstance(v, float):
            factor = random.uniform(0.9, 1.2) if mutation_boost else random.uniform(0.95, 1.05)
            new_params[k] = round(v * factor, 4)
        else:
            new_params[k] = v
    return new_params

def generate_module(base_mod, generation_id, boost=False):
    new_id = f"{base_mod['id'].split('-')[0]}-{generation_id}"
    return {
        "id": new_id,
        "symbol": base_mod["symbol"],
        "strategy_type": base_mod["strategy_type"],
        "parameters": mutate_parameters(base_mod["parameters"], mutation_boost=boost),
        "virtual_capital": 1000.0,  # æ¯é»æ¨¡çµé è¨­è³éæå¥
        "parent_id": base_mod.get("id"),
        "mutate_generation": base_mod.get("mutate_generation", 0) + 1,
        "from_resurrection": base_mod.get("from_resurrection", False),
        "resurrected": base_mod.get("resurrected", False),
        "resurrection_chance": base_mod.get("resurrection_chance", 0),
        "bloodline": base_mod.get("bloodline", []) + [base_mod.get("id")],
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
    print("[v4] ååæ¨¡çµçæå¨")
    king_pool = load_json_list(KING_PATH)
    previous_modules = load_json_list(PREVIOUS_PATH)

    base_pool = []

    # ä¾æº 1ï¼çèæ± ï¼å æ¬ by king_rounds
    for mod in king_pool:
        weight = 1 + mod.get("king_rounds", 1)
        base_pool.extend([mod] * weight)

    # ä¾æº 2ï¼æ­·ä»£é«åæ¨¡çµï¼score > 80ï¼
    for mod in previous_modules:
        if mod.get("score", 0) > 80:
            base_pool.append(mod)

    # ä¾æº 3ï¼é«åå¤±ææ¨¡çµå¾©æ´»ï¼æå¤ 10 é»ï¼
    resurrected = []
    for mod in previous_modules:
        if mod.get("eliminated") and mod.get("score", 0) > 75 and len(resurrected) < 10:
            mod["from_resurrection"] = True
            mod["resurrected"] = True
            mod["resurrection_chance"] = 1.0
            resurrected.append(mod)
    base_pool.extend(resurrected)

    print(f"[v4] çªè®ä¾æºç¸½æ¸ï¼{len(base_pool)}ï¼å«å¾©æ´» {len(resurrected)} é»ï¼")

    # æ¨¡çµçæ
    new_modules = []
    for i in range(MODULE_COUNT):
        parent = random.choice(base_pool)
        is_king_boost = parent.get("king_rounds", 0) >= 2
        is_rebirth_boost = parent.get("from_resurrection", False)
        boosted = is_king_boost or is_rebirth_boost
        mod = generate_module(parent, i + 1, boost=boosted)
        save_module(mod)
        new_modules.append(mod)

    print(f"[v4] å·²çææ¨¡çµæ¸ï¼{len(new_modules)} é»")
    return new_modules

if __name__ == "__main__":
    main()
