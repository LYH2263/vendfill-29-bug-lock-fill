from app.services.page_split import present_full, present_summary, present_ticket


def test_summary_uses_gap_sum_not_ticket_fill():
    payload = {
        "id": 9,
        "lines": [
            {"lane_id": 1, "gap": 7, "fill_qty": 4, "status": "need_fill"},
            {"lane_id": 2, "gap": 0, "fill_qty": 0, "status": "full"},
            {"lane_id": 3, "gap": 10, "fill_qty": 0, "status": "blocked"},
        ],
        "overbooked_count": 0,
    }
    s = present_summary(1, payload)
    # 合计按待补行缺口累加（非票面补量）；封锁道的缺口不进合计
    assert s["total_fill"] == 7
    # 待补/满仓/封锁各算各的：封锁不计入待补，也不算满仓
    assert s["need_fill_count"] == 1
    assert s["full_count"] == 1
    assert s["blocked_count"] == 1
    assert s["max_fill_qty"] == 4


def test_full_list_only_contains_truly_full_lanes():
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
    # 满仓名单只收真正满仓的道：封锁、超占、待补都不得混入
    assert ids == {4}


def test_ticket_keeps_row_fill_qty():
    payload = {"lines": [{"lane_id": 1, "fill_qty": 4, "gap": 9}]}
    t = present_ticket(payload)
    assert t["total_fill"] == 4
