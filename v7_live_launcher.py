import json
from pathlib import Path
from datetime import datetime

KING_PATH = Path("~/Killcore/king_pool.json").expanduser()

def format_percent(v):
    return f"{v:.1f}%" if isinstance(v, (float, int)) else "-"

def show_king_report(king):
    print("\n=== Killcore 王者戰鬥簡報 ===\n")

    print(f"王者編號     : {king.get('id')}")
    print(f"幣種         : {king.get('symbol')}")
    print(f"策略類型     : {king.get('strategy_type')}（策略 {strategy_label(king.get('strategy_type'))}）")
    print(f"策略風格     : {king.get('strategy_behavior', '未知')}")
    print(f"模組分數     : {king.get('score')}")
    print(f"報酬率       : +{format_percent(king.get('return_pct'))}")
    print(f"最大回撤     : {format_percent(king.get('drawdown'))}")
    print(f"Sharpe       : {king.get('sharpe')}")
    print(f"勝率         : {format_percent(king.get('win_rate'))}")
    print(f"交易次數     : {king.get('trade_count')}")
    print()

    print(f"重生者？     : {'是' if king.get('from_resurrection') else '否'}")
    print(f"血統來源     : {king.get('parent_id', '未知')}（第 {king.get('mutate_generation', '?')} 代）")
    print(f"神聖保護？   : {'是' if king.get('has_divine_protection') else '否'}")
    print(f"王者連任次數 : {king.get('king_rounds', 1)} 輪")
    print()

    print("策略參數：")
    for k, v in king.get("parameters", {}).items():
        print(f"  - {k:<8}: {v}")
    print()

    print(f"模組建立時間 : {king.get('created_at')}")
    print(f"最近更新時間 : {king.get('updated_at')}")
    print()

    print("本輪總戰力摘要：")
    remarks = []
    if king.get("drawdown", 0) < 1.5:
        remarks.append("低風險")
    if king.get("sharpe", 0) > 2.0:
        remarks.append("高穩定")
    if king.get("from_resurrection"):
        remarks.append("復活流派")
    if king.get("king_rounds", 1) > 1:
        remarks.append(f"連任 {king.get('king_rounds')} 輪")
    if not remarks:
        remarks.append("尚無特殊標籤")

    print("> " + "，".join(remarks))
    print()

def strategy_label(s):
    return {
        "A": "雙均線突破",
        "B": "區間反轉",
        "C": "穩定 scalping"
    }.get(s, "未知")

# === 主執行 ===
if __name__ == "__main__":
    if not KING_PATH.exists():
        print("[v7] 找不到王者資料 king_pool.json")
        exit(1)

    with KING_PATH.open() as f:
        data = json.load(f)
        if not data:
            print("[v7] 王者資料為空")
            exit(1)

        king = data[0]
        show_king_report(king)
