from tests.cashola_ap.fixtures_ap import bank_outflows
# Suppose we have ap_timing_guardrail(vendor, posted_at) -> exception|None

def ap_timing_guardrail(description: str, posted_at_iso: str):
    # Simplified: rent expected near 1st (±2d), else TIMING exception
    if "RENT" in description.upper():
        day = int(posted_at_iso[8:10])
        if day < 29 and day > 3:  # outside ±2d window
            return {"kind":"TIMING","reason":"Rent settled outside expected window"}
    return None

def test_rent_outside_window_triggers_timing():
    late = [b for b in bank_outflows if b["id"]=="bt_rent_late_2024_04_06"][0]
    ex = ap_timing_guardrail(late["description"], late["posted_at"])
    assert ex and ex["kind"]=="TIMING"
