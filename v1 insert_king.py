import json

def insert_into_king_pool(v1_path, new_king):
    with open(v1_path, 'r') as f:
        king_pool = json.load(f)

    if len(king_pool) < 100:
        king_pool.append(new_king)
    else:
        min_score = min(king_pool, key=lambda x: x["score"])["score"]
        if new_king["score"] > min_score:
            king_pool.append(new_king)
            king_pool = sorted(king_pool, key=lambda x: x["score"], reverse=True)[:100]
        else:
            print(f"淘汰：{new_king['id']} 分數 {new_king['score']} 無法進入 v1")
            return

    with open(v1_path, 'w') as f:
        json.dump(king_pool, f, indent=2)
    print(f"成功寫入：{new_king['id']}")

# 測試用
if __name__ == "__main__":
    new_king = {
        "id": "pet_BTC_B-94",
        "symbol": "BTCUSDT",
        "strategy_type": "B",
        "parameters": { "ma_fast": 15, "ma_slow": 45, "sl_pct": 1.8, "tp_pct": 6 },
        "entry_price": 65400.0,
        "exit_price": 66920.0,
        "profit": 1520.0,
        "return_pct": 2.32,
        "drawdown": 1.0,
        "sharpe": 2.15,
        "win_rate": 71.1,
        "trade_count": 12,
        "score": 90.63,
        "score_rank": 2,
        "is_king": true,
        "king_rounds": 1,
        "resurrected": false,
        "from_resurrection": false,
        "resurrection_chance": 0.5,
        "has_divine_protection": true,
        "eliminated": false,
        "created_at": "2025-05-24T10:30:00",
        "updated_at": "2025-05-24T11:15:00",
        "system_version": "Killcore-v∞",
        "schema_version": "v2.0"
    }

    insert_into_king_pool('king_pool.json', new_king)
