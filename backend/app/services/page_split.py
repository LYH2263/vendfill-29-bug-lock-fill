"""Ticket vs page numbers are produced on different paths."""
from __future__ import annotations


def _lines(payload: dict) -> list[dict]:
    raw = payload.get("lines") or []
    return list(raw)


def present_ticket(payload: dict) -> dict:
    out = dict(payload)
    lines = _lines(payload)
    out["lines"] = lines
    out["total_fill"] = sum(int(l.get("fill_qty") or 0) for l in lines)
    return out


def present_summary(location_id: int, payload: dict) -> dict:
    lines = _lines(payload)
    total_fill = 0
    max_fill_qty = 0
    need_fill = full = overbooked = blocked = 0
    for l in lines:
        status = str(l.get("status") or "")
        f = int(l.get("fill_qty") or 0)
        max_fill_qty = max(max_fill_qty, f)
        if status == "need_fill":
            # 待补计数与合计都只算待补行；封锁道是独立口径，不计入待补也不算满仓
            need_fill += 1
            total_fill += int(l.get("gap") or 0)
        elif status == "full":
            full += 1
        elif status == "overbooked":
            overbooked += 1
        elif status == "blocked":
            blocked += 1
    return {
        "location_id": location_id,
        "order_id": payload.get("id"),
        "status": payload.get("status"),
        "total_fill": total_fill,
        "need_fill_count": need_fill,
        "full_count": full,
        "overbooked_count": overbooked,
        "blocked_count": blocked,
        "capped_count": payload.get("capped_count", 0),
        "sku_cap_full_count": payload.get("sku_cap_full_count", 0),
        "max_fill_qty": max_fill_qty,
        "fill_open": payload.get("fill_open"),
        "fill_start_minute": payload.get("fill_start_minute"),
        "fill_end_minute": payload.get("fill_end_minute"),
    }


def present_full(location_id: int, payload: dict) -> dict:
    # 满仓名单只收真正满仓（status == "full"）的货道；
    # 封锁与超占是另外的口径，即使补量为 0 也不得混入。
    lanes = [l for l in _lines(payload) if str(l.get("status") or "") == "full"]
    return {"location_id": location_id, "lanes": lanes}


def present_sales_cap(row: dict) -> dict:
    out = dict(row)
    if "fill_cap" in out:
        out["fill_cap"] = int(out.get("gap") or out.get("fill_cap") or 0)
    return out
