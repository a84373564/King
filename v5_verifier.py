# -*- coding: utf-8 -*-
import json
import random
from pathlib import Path

MODULE_PATH = Path("~/Killcore/v4_modules").expanduser()
RESULT_PATH = Path("~/Killcore/v5_result.json").expanduser()
KING_PATH = Path("~/Killcore/king_pool.json").expanduser()
GODLINE_PATH = Path("~/Killcore/godline.json").expanduser()

def simulate_trade(mod):
    slip = mod.setdefault("slippage_pct", round(random.uniform(-0.003, 0.003), 4))
    fee = mod.setdefault("tx_fee_pct", 0.001)
    ep = mod.setdefault("entry_price", 1000.0)
    xp = mod.setdefault("exit_price", 1000.0)

    entry_adj = ep * (1 + slip)
    exit_adj = xp * (1 - slip)
    gross_profit = exit_adj - entry_adj
    net_fee = (entry_adj + exit_adj) * fee
    net_profit = gross_profit - net_fee
    return_pct_adj = round((net_profit / entry_adj) * 100, 2) if entry_adj != 0 else 0
    slip_impact = round((xp - exit_adj) / xp * 100, 4)

    mod["entry_adj"] = round(entry_adj, 4)
    mod["exit_adj"] = round(exit_adj, 4)
    mod["net_profit"] = round(net_profit, 2)
    mod["adjusted_return_pct"] = return_pct_adj
    mod["slippage_impact_pct"] = slip_impact

modules = []
for file in MODULE_PATH.glob("*.json"):
    with open(file) as f:
        mod = json.load(f)

        mod.setdefault("return_pct", 0.0)
        mod.setdefault("sharpe", 0.0)
        mod.setdefault("win_rate", 0.0)
        mod.setdefault("drawdown", 0.0)
        mod.setdefault("entry_delay_sec", random.randint(1, 3))
        mod.setdefault("type", "unknown")
        mod.setdefault("fail_count", 0)
        mod.setdefault("fail_reason", "")
        mod.setdefault("verified_env", "default")
        mod.setdefault("resurrected", False)
        mod.setdefault("is_divine", False)
        mod.setdefault("divine_rounds", 0)
        mod.setdefault("simulated_capital_start", 70.51)
        mod.setdefault("live_rounds", 0)
        mod.setdefault("capital_curve", [70.51])
        mod.setdefault("market_type", random.choice(["sideways", "trending", "high_volatility"]))
        mod.setdefault("funding_plan", "AutoDynamic")
        mod.setdefault("FRI", round(random.uniform(0.1, 0.9), 3))

        simulate_trade(mod)

        end_capital = mod["simulated_capital_start"] * (1 + mod["adjusted_return_pct"] / 100)
        mod["simulated_capital_end"] = round(end_capital, 2)
        mod["capital_curve"].append(mod["simulated_capital_end"])

        modules.append(mod)

for mod in modules:
    score = round(mod["adjusted_return_pct"] * 0.5 + mod["sharpe"] * 10 + mod["win_rate"] * 0.3 - mod["drawdown"] * 5, 2)
    mod["score"] = score

modules = sorted(modules, key=lambda x: x["score"], reverse=True)
for i, mod in enumerate(modules):
    mod["score_rank"] = i + 1
    mod["is_king"] = (i == 0)
    mod["eliminated"] = (i != 0)

top_king = modules[0]
top_king["king_rounds"] = top_king.get("king_rounds", 0) + 1
top_king["has_divine_protection"] = True

prev_divine_id = None
if GODLINE_PATH.exists():
    with open(GODLINE_PATH) as f:
        godline = json.load(f)
        if godline and godline[-1].get("is_divine"):
            prev_divine_id = godline[-1]["id"]

if prev_divine_id and prev_divine_id != top_king["id"]:
    for mod in modules:
        if mod["id"] == prev_divine_id:
            mod.pop("is_divine", None)
            mod.pop("divine_title", None)
            mod["was_god"] = True
            mod["eliminated"] = True

top_king["is_divine"] = True
top_king["divine_title"] = f"True God #{top_king['king_rounds']}"
top_king["divine_rounds"] = top_king.get("divine_rounds", 0) + 1
top_king["eliminated"] = False

if prev_divine_id and prev_divine_id != top_king["id"]:
    for mod in modules:
        if mod["id"] != prev_divine_id and mod["score_rank"] == 1:
            mod["is_godslayer"] = True
            mod["slain_god_id"] = prev_divine_id

for mod in modules:
    if mod["drawdown"] > 25 or mod["net_profit"] < -100:
        mod["type"] = "explosive"
        mod["fail_reason"] = "heavy loss"
    elif mod["sharpe"] < 0.5:
        mod["fail_reason"] = "low risk control"
    elif mod["adjusted_return_pct"] < 0:
        mod["fail_reason"] = "negative return"
    else:
        mod["type"] = "stable"
    if mod.get("fail_count", 0) > 2:
        mod["score"] -= 5
        mod["fail_reason"] += " | too many retries"

for mod in modules:
    if mod.get("is_divine") and mod.get("king_rounds", 0) > 1:
        mod["has_divine_protection"] = True
        mod["eliminated"] = False
    if not mod.get("is_divine") and not mod.get("is_king"):
        mod["eliminated"] = True

    if not mod["eliminated"]:
        mod["live_rounds"] = mod.get("live_rounds", 0) + 1

with RESULT_PATH.open("w") as f:
    json.dump(modules, f, indent=2)
with KING_PATH.open("w") as f:
    json.dump([top_king], f, indent=2)

godline_all = []
if GODLINE_PATH.exists():
    with open(GODLINE_PATH) as f:
        godline_all = json.load(f)
godline_all.append(top_king)
with GODLINE_PATH.open("w") as f:
    json.dump(godline_all[-20:], f, indent=2)

print(f"[v5] New King: {top_king['id']} (Score: {top_king['score']})")
if top_king.get("is_divine"):
    print(f"[v5] True God: {top_king['divine_title']} (Rounds: {top_king['divine_rounds']})")
if top_king.get("king_rounds", 0) > 1:
    print(f"[v5] Consecutive Reign: {top_king['king_rounds']} rounds")
for mod in modules:
    if mod.get("is_godslayer"):
        print(f"[v5] Godslayer: {mod['id']} (Killed: {mod['slain_god_id']})")
