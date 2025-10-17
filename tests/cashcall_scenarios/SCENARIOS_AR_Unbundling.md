# CashCall Scenarios — AR Unbundling & Reconciliation

**Purpose:** validate ingest → identity graph → consolidation (count once, bank-timed) → AR unbundling → exceptions → digest math.

Scenarios covered by fixtures:
1) Multi-installment job (two invoices; Feb & Mar/Apr) → two payouts, two settlements.
2) Clean single-job invoice → exact match; fees as composition; one INFLOW at bank date.
3) Recurring + emergency → recurring settles in-period; emergency paid later (shows up as AR until bank settles).
4) Ambiguous multi-job payout → two different invoice subsets yield the same net; expect AR_AMBIG.
5) Ghost AR → ops shows paid, no bank/processor; expect GHOST_AR.
6) Timing guardrail → settlement arrives >2d outside expected; expect TIMING.

Success gates: ≥95% reconciled inflow value, ≤10 tray items, ≥70% auto by wk 4, runway error <±0.3 wks.
