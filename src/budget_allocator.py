"""Segment-based retention budget allocator.

All economic parameters are STATED ASSUMPTIONS, not data-derived facts.
They are exposed as editable inputs in the dashboard so users can run their
own scenarios. Defaults are reasoned from segment behavior (see notebook 05).
"""
import pandas as pd

DEFAULT_ASSUMPTIONS = {
    "High-Value One-Timers": {"intervention_cost": 15.0, "success_rate": 0.08,
                              "value_uplift": 1.0},
    "Repeat Buyers":         {"intervention_cost": 10.0, "success_rate": 0.20,
                              "value_uplift": 1.0},
    "Low-Value Recent":      {"intervention_cost": 8.0,  "success_rate": 0.05,
                              "value_uplift": 0.7},
    "Dormant Low-Value":     {"intervention_cost": 8.0,  "success_rate": 0.02,
                              "value_uplift": 0.5},
}


def compute_expected_value(seg_summary: pd.DataFrame,
                           assumptions: dict = None) -> pd.DataFrame:
    """seg_summary needs columns: segment, n_customers, avg_value."""
    assumptions = assumptions or DEFAULT_ASSUMPTIONS
    rows = []
    for _, r in seg_summary.iterrows():
        a = assumptions[r["segment"]]
        total_cost = r["n_customers"] * a["intervention_cost"]
        gain = (r["n_customers"] * r["avg_value"]
                * a["value_uplift"] * a["success_rate"])
        net = gain - total_cost
        rows.append({
            "segment": r["segment"], "n_customers": r["n_customers"],
            "avg_value": r["avg_value"],
            "intervention_cost_total": total_cost,
            "expected_gain": gain, "expected_net": net,
            "roi": net / total_cost if total_cost else 0.0,
        })
    return pd.DataFrame(rows).sort_values("roi", ascending=False)


def allocate_budget(ev_table: pd.DataFrame, total_budget: float) -> pd.DataFrame:
    """Greedy allocation by descending ROI; never funds negative-ROI segments."""
    ev_sorted = ev_table.sort_values("roi", ascending=False).copy()
    remaining, allocations = total_budget, []
    for _, r in ev_sorted.iterrows():
        spend = min(remaining, r["intervention_cost_total"]) if r["roi"] > 0 else 0.0
        allocations.append(spend)
        remaining -= spend
    ev_sorted["allocated_budget"] = allocations
    ev_sorted["pct_of_budget"] = ev_sorted["allocated_budget"] / total_budget * 100
    return ev_sorted
