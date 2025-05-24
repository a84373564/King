import os
import json
import random
from datetime import datetime
from pathlib import Path

MODULE_PATH = Path("~/Killcore/v4_modules").expanduser()
KING_PATH = Path("~/Killcore/king_pool.json").expanduser()
RESULT_PATH = Path("~/Killcore/v5_result.json").expanduser()
GODLINE_PATH = Path("~/Killcore/godline.json").expanduser()

MARKET_SCENARIOS = ["high_volatility", "low_volatility", "trend_up", "range_chop"]

def simulate_module(mod):
    scenario = random.choice(MARKET_SCENARIOS)
    params = mod["parameters"]
    strategy = mod["strategy_type"]

    base_return = {
        "A": random.uniform(1.0, 4.0),
        "B": random.uniform(0.5, 3.5),
        "C": random.uniform(0.8, 2.8)
    }[strategy]

    if mod.get("is_king", False):
        base_return += 0.3
        mod["king_rounds"] = mod.get("king_rounds", 1) + 1
    else:
        mod["king_rounds"] = 0

    drawdown = random.uniform(0.8, 3.5)
    if mod.get("is_king"):
        drawdown *= 0.95

    win_rate = random.uniform(50, 80)
    trade_count = random.randint(8, 20)

    mod["return_pct"] = base_return
    mod["drawdown"] = drawdown
    mod["win_rate"] = win_rate
    mod["trade_count"] = trade_count
    mod["sharpe"] = round(base_return / drawdown, 2)

    score = (
        base_return * 1.5
        - drawdown * 1.2
        + mod["sharpe"] * 2
        + win_rate * 0.2
    )
    mod["score"] = round(score, 2)

    mod["score_history"] = mod.get("score_history", [])
    mod["score_history"].append(mod["score"])
    last_scores = mod["score_history"][-3:]
    mod["score_rolling_avg"] = round(sum(last_scores) / len(last_scores), 2)

    mod["final_score"] = round(0.7 * mod["score"] + 0.3 * mod["score_rolling_avg"], 2)

    return mod

def load_modules():
    return [json.load(open(p)) for p in MODULE_PATH.glob("*.json")]

def load_king_id():
    if KING_PATH.exists():
        with open(KING_PATH) as f:
            king_pool = json.load(f)
            if king_pool:
                return king_pool[0]["id"]
    return None

def write_result(modules):
    with open(RESULT_PATH, "w") as f:
        json.dump(modules, f, indent=2)

def write_king(mod):
    with open(KING_PATH, "w") as f:
        json.dump([mod], f, indent=2)

def update_godline(new_king):
    if not GODLINE_PATH.exists():
        godline = []
    else:
        with open(GODLINE_PATH) as f:
            godline = json.load(f)

    last_entry = godline[-1] if godline else None
    bloodline = last_entry["bloodline"][:] if last_entry else []
    bloodline.append(new_king["id"])

    entry = {
        "id": new_king["id"],
        "slayer_of": new_king.get("slayer_of"),
        "king_rounds": new_king.get("king_rounds", 1),
        "bloodline": bloodline,
        "title": "god_candidate",
        "has_fallen": False
    }

    godline.append(entry)

    with open(GODLINE_PATH, "w") as f:
        json.dump(godline, f, indent=2)

def main():
    modules = load_modules()
    previous_king_id = load_king_id()

    verified = [simulate_module(mod) for mod in modules]
    verified.sort(key=lambda m: m["final_score"], reverse=True)

    new_king = verified[0]
    new_king["is_king"] = True
    new_king["resurrected"] = False
    new_king["has_divine_protection"] = True
    new_king["from_resurrection"] = False
    new_king["eliminated"] = False

    if previous_king_id and new_king["id"] != previous_king_id:
        new_king["slayer_of"] = previous_king_id

    for m in verified[1:]:
        m["is_king"] = False
        m["eliminated"] = True

    write_result(verified)
    write_king(new_king)
    update_godline(new_king)

if __name__ == "__main__":
    main()
