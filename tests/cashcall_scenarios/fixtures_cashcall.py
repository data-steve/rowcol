from datetime import datetime
from typing import List, Dict

COMPANY_ID = "co_demo"
BANK_ACCOUNT_ID = "ba_demo_operating"
PROCESSOR = "STRIPE"

# ---------- Scenario 1: Multi-installment ----------
jobber_invoices_s1: List[Dict] = [
    {"id": "INV_MALL_50",   "company_id": COMPANY_ID, "job_id": "JOB_MALL", "amount_cents": 750_000, "issued_at": "2024-02-25T09:00:00Z", "status": "paid"},
    {"id": "INV_MALL_FINAL","company_id": COMPANY_ID, "job_id": "JOB_MALL", "amount_cents": 750_000, "issued_at": "2024-03-20T17:00:00Z", "status": "paid"},
]

stripe_charges_s1: List[Dict] = [
    # Charge for 50% deposit
    {"id": "ch_mall_50", "amount_cents": 750_000, "fee_cents": 21_780, "net_cents": 728_220,
     "created": "2024-02-28T15:30:00Z", "payout_id": "po_mall_50",
     "metadata": {"jobber_invoice_id": "INV_MALL_50"}},
    # Charge for final
    {"id": "ch_mall_final", "amount_cents": 750_000, "fee_cents": 21_780, "net_cents": 728_220,
     "created": "2024-04-03T14:10:00Z", "payout_id": "po_mall_final",
     "metadata": {"jobber_invoice_id": "INV_MALL_FINAL"}},
]

stripe_payouts_s1: List[Dict] = [
    {"id": "po_mall_50",   "arrival_date": "2024-03-01", "net_cents": 728_220},
    {"id": "po_mall_final","arrival_date": "2024-04-05", "net_cents": 728_220},
]

bank_txns_s1: List[Dict] = [
    {"id": "bt_mall_50_settlement",   "account_id": BANK_ACCOUNT_ID, "posted_at": "2024-03-01T09:05:00Z",
     "amount_cents": +728_220, "description": "Stripe Payout *1234"},
    {"id": "bt_mall_final_settlement","account_id": BANK_ACCOUNT_ID, "posted_at": "2024-04-05T09:06:00Z",
     "amount_cents": +728_220, "description": "Stripe Payout *1234"},
]

# ---------- Scenario 2: Clean single-job ----------
jobber_invoices_s2 = [
    {"id": "INV_BACKYARD", "company_id": COMPANY_ID, "job_id": "JOB_BKYD", "amount_cents": 320_000, "issued_at": "2024-03-15T12:00:00Z", "status": "paid"},
]
stripe_charges_s2 = [
    # Fee = 2.9% + $0.30 -> 93.10; net 3,106.90
    {"id": "ch_backyard", "amount_cents": 320_000, "fee_cents": 9_310, "net_cents": 310_690,
     "created": "2024-03-28T16:00:00Z", "payout_id": "po_backyard",
     "metadata": {"jobber_invoice_id": "INV_BACKYARD"}},
]
stripe_payouts_s2 = [
    {"id": "po_backyard", "arrival_date": "2024-03-29", "net_cents": 310_690},
]
bank_txns_s2 = [
    {"id": "bt_backyard_settlement", "account_id": BANK_ACCOUNT_ID, "posted_at": "2024-03-29T09:02:00Z",
     "amount_cents": +310_690, "description": "Stripe Payout *1234"},
]

# ---------- Scenario 3: Recurring + emergency ----------
jobber_invoices_s3 = [
    {"id": "INV_RECUR_MAR",   "company_id": COMPANY_ID, "job_id": "JOB_COMM", "amount_cents": 120_000, "issued_at": "2024-03-01T08:00:00Z", "status": "paid"},
    {"id": "INV_EMERGENCY",   "company_id": COMPANY_ID, "job_id": "JOB_COMM", "amount_cents": 80_000,  "issued_at": "2024-03-20T10:00:00Z", "status": "paid"},
]
stripe_charges_s3 = [
    {"id": "ch_recur_mar", "amount_cents": 120_000, "fee_cents": 3_510, "net_cents": 116_490,
     "created": "2024-03-01T09:00:00Z", "payout_id": "po_recur_mar",
     "metadata": {"jobber_invoice_id": "INV_RECUR_MAR"}},
    {"id": "ch_emergency", "amount_cents": 80_000,  "fee_cents": 2_350, "net_cents": 77_650,
     "created": "2024-04-05T11:15:00Z", "payout_id": "po_emergency",
     "metadata": {"jobber_invoice_id": "INV_EMERGENCY"}},
]
stripe_payouts_s3 = [
    {"id": "po_recur_mar", "arrival_date": "2024-03-01", "net_cents": 116_490},
    {"id": "po_emergency", "arrival_date": "2024-04-07", "net_cents": 77_650},
]
bank_txns_s3 = [
    {"id": "bt_recur_settlement", "account_id": BANK_ACCOUNT_ID, "posted_at": "2024-03-01T10:00:00Z",
     "amount_cents": +116_490, "description": "Stripe Payout *1234"},
    {"id": "bt_emergency_settlement", "account_id": BANK_ACCOUNT_ID, "posted_at": "2024-04-07T10:00:00Z",
     "amount_cents": +77_650, "description": "Stripe Payout *1234"},
]

# ---------- Scenario 4: Ambiguous multi-job payout ----------
# Two different subsets yield same net:
#  A(180k) + C(150k)  -> nets 174,750 + 145,620 = 320,370
#  B(170k) + D(160k)  -> nets 165,040 + 155,330 = 320,370
jobber_invoices_s4 = [
    {"id": "INV_A", "company_id": COMPANY_ID, "job_id": "JOB_A", "amount_cents": 180_000, "issued_at": "2024-03-18T09:00:00Z", "status": "paid"},
    {"id": "INV_B", "company_id": COMPANY_ID, "job_id": "JOB_B", "amount_cents": 170_000, "issued_at": "2024-03-18T09:10:00Z", "status": "paid"},
    {"id": "INV_C", "company_id": COMPANY_ID, "job_id": "JOB_C", "amount_cents": 150_000, "issued_at": "2024-03-18T09:20:00Z", "status": "paid"},
    {"id": "INV_D", "company_id": COMPANY_ID, "job_id": "JOB_D", "amount_cents": 160_000, "issued_at": "2024-03-18T09:30:00Z", "status": "paid"},
]
stripe_charges_s4 = [
    {"id": "ch_a", "amount_cents": 180_000, "fee_cents": 5_250, "net_cents": 174_750,
     "created": "2024-03-20T12:00:00Z", "payout_id": "po_ambig"},
    {"id": "ch_b", "amount_cents": 170_000, "fee_cents": 4_960, "net_cents": 165_040,
     "created": "2024-03-20T12:02:00Z", "payout_id": "po_ambig"},
    {"id": "ch_c", "amount_cents": 150_000, "fee_cents": 4_380, "net_cents": 145_620,
     "created": "2024-03-20T12:04:00Z", "payout_id": "po_ambig"},
    {"id": "ch_d", "amount_cents": 160_000, "fee_cents": 4_670, "net_cents": 155_330,
     "created": "2024-03-20T12:06:00Z", "payout_id": "po_ambig"},
]
stripe_payouts_s4 = [
    {"id": "po_ambig", "arrival_date": "2024-03-22", "net_cents": 320_370},
]
bank_txns_s4 = [
    {"id": "bt_ambig_settlement", "account_id": BANK_ACCOUNT_ID, "posted_at": "2024-03-22T09:00:00Z",
     "amount_cents": +320_370, "description": "Stripe Payout *1234"},
]

# ---------- Scenario 5: Ghost AR (ops "paid", no bank/processor) ----------
jobber_invoices_s5 = [
    {"id": "INV_OFFPLATFORM", "company_id": COMPANY_ID, "job_id": "JOB_OP", "amount_cents": 2_000_00, "issued_at": "2024-03-10T09:00:00Z", "status": "paid"},
]
# No corresponding processor or bank events -> should become GHOST_AR

# ---------- Scenario 6: Timing guardrail (late settlement) ----------
# Payout arrival says 2024-03-30, but bank settles 2024-04-04 (> 2d window)
stripe_payouts_s6 = [
    {"id": "po_late", "arrival_date": "2024-03-30", "net_cents": 101_000},
]
bank_txns_s6 = [
    {"id": "bt_late_settlement", "account_id": BANK_ACCOUNT_ID, "posted_at": "2024-04-04T09:00:00Z",
     "amount_cents": +101_000, "description": "Stripe Payout *1234"},
]
