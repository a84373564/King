# -*- coding: utf-8 -*-
import json
from datetime import datetime
from pathlib import Path

# === 固定戰鬥幣種 ===
FIXED_SYMBOLS = ["MATICUSDT", "OPUSDT"]
OUTPUT_PATH = Path("~/Killcore/v2_candidates.json").expanduser()
LOG_PATH = Path("~/Killcore/v2_rank_log.json").expanduser()

ENABLE_LOGGING = True

def save_fixed_candidates():
    data = {
        "generated_at": datetime.now().isoformat(),
        "symbols": FIXED_SYMBOLS
    }
    with OUTPUT_PATH.open("w") as f:
        json.dump(data, f, indent=2)
    print(f"[v2-lock] 成功選出幣種：{data['symbols']}")

def log_selection():
    if not ENABLE_LOGGING:
        return
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "source": "fixed",
        "symbols": FIXED_SYMBOLS
    }
    if LOG_PATH.exists():
        with LOG_PATH.open("r") as f:
            logs = json.load(f)
    else:
        logs = []
    logs.append(log_entry)
    with LOG_PATH.open("w") as f:
        json.dump(logs, f, indent=2)
    print("[v2-log] 固定幣種已記錄入 log")

def main():
    save_fixed_candidates()
    log_selection()

if __name__ == "__main__":
    main()
