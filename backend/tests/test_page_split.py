from app.services.page_split import present_full, present_summary, present_ticket


def test_summary_counts_by_status_and_uses_ticket_fill():
    payload = {
        "id": 9,
        "lines": [
            {"lane_id": 1, "gap": 7, "fill_qty": 4, "status": "need_fill"},
            {"lane_id": 2, "gap": 0, "fill_qty": 0, "status": "full"},
            {"lane_id": 3, "gap": 5, "fill_qty": 0, "status": "blocked"},
        ],
        "overbooked_count": 0,
        "blocked_count": 1,
    }
    s = present_summary(1, payload)
    assert s["total_fill"] == 4
    assert s["need_fill_count"] == 1
    assert s["full_count"] == 1
    assert s["blocked_count"] == 1
    assert s["max_fill_qty"] == 0


def test_full_list_keeps_full_only_excludes_blocked_and_overbooked():
    payload = {
        "lines": [
            {"lane_id": 1, "fill_qty": 0, "status": "blocked", "reason": "货道封锁"},
            {"lane_id": 2, "fill_qty": 3, "status": "need_fill", "reason": ""},
            {"lane_id": 3, "fill_qty": 0, "status": "overbooked", "reason": "超占"},
            {"lane_id": 4, "fill_qty": 0, "status": "full", "reason": "已满仓"},
        ]
    }
    body = present_full(1, payload)
    ids = {l["lane_id"] for l in body["lanes"]}
    assert ids == {4}


def test_full_list_excludes_blocked_even_at_capacity():
    # 库存顶到容量但勾着封锁：满仓名单不许收，两套结论不得并句
    payload = {
        "lines": [
            {"lane_id": 1, "gap": 0, "fill_qty": 0, "status": "blocked", "reason": "货道封锁"},
        ]
    }
    assert present_full(1, payload)["lanes"] == []


def test_ticket_keeps_row_fill_qty():
    payload = {"lines": [{"lane_id": 1, "fill_qty": 4, "gap": 9}]}
    t = present_ticket(payload)
    assert t["total_fill"] == 4
