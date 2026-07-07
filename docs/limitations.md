# Limitations & Honest Caveats

This document consolidates the methodological caveats across the project. Surfacing these is deliberate — an interviewer or reviewer should not find a weakness the analysis didn't already acknowledge.

## 1. The single-purchase rate depends on the denominator

The "buy once" figure is reported as **97%** on the segmentation cohort (90,557 of 93,358 customers have frequency = 1). This differs slightly from the ~96% unique-customer ratio computed at the raw-data level (96,096 unique people among 99,441 customer records). The two figures use different denominators — the segmentation cohort counts only customers whose delivered orders survive the join to `order_items`, whereas the raw ratio counts all customer records. Both are correct for their respective scopes; the app and analysis use the 97% cohort figure consistently.

## 2. The spend classifier is near-definitional, not a sophisticated lifecycle model

The binary "high-value" classifier reports ROC-AUC 0.97, but this is **not** evidence of powerful predictive modeling. Because 97% of customers order exactly once, a one-time buyer's first-order value essentially *is* their lifetime monetary value — so predicting the (monetary-defined) high-value segment from first-order spend is close to a definitional relationship. The high AUC is expected and is reported as such rather than celebrated.

The genuinely informative result is the **negative** one: the model cannot predict *repeat behavior* (Repeat Buyers recall ~1%). Loyalty is not forecastable from a first order. This finding — not the AUC — is what motivated the causal inference layer.

## 3. The causal estimate is an upper bound

Propensity score matching estimates that delivering 3+ days early raises review scores by ATT +1.73 (on a 1–5 scale). Two caveats:

- **Treatment–outcome coupling.** A late delivery is often *literally what a negative review complains about*, so the review score is partly a direct readout of delivery timing rather than a fully independent outcome. PSM removes confounding but cannot remove this coupling. The +1.73 estimate should therefore be read as an **upper bound**; the defensible claim is directional (early delivery improves satisfaction), not the precise magnitude.
- **Unobserved confounders.** PSM only adjusts for measured covariates (order value, freight, category, region, promised delivery time, item count). Balance was achieved on all of these after matching (all standardized mean differences < 0.1; the key confounder `estimated_days` improved from 0.263 to 0.015), but unmeasured confounders may remain.
- **Treatment/control imbalance.** Most deliveries beat their estimate, so the treated group (85,173) vastly outnumbers the control group (7,661). Matching to the smaller control pool is valid but limits the effective sample.

## 4. The budget allocator runs on assumptions, not measured parameters

Olist provides no intervention costs or conversion rates. The budget allocator is therefore a **decision framework**, not a model fit to outcome data. All economic parameters (per-customer cost, success rate, value uplift) are stated assumptions exposed as adjustable sliders in the dashboard, so users can run their own scenarios. Default values are reasoned from segment behavior but should not be interpreted as empirical estimates.

## 5. Geographic and category features were tested and excluded

Region and product category were initially included as clustering inputs but found non-discriminative (every cluster was ~70% Southeast and ~37% "other" category). They were removed from the clustering (which improved silhouette from ~0.21 to 0.356) and retained only as descriptive profiling columns. The honest finding: Olist customers segment on value and recency, not geography or product taste.

## 6. Cohort sparsity in early months

The retention heatmap contains empty cells for some cohort-month combinations — typically the smallest early cohorts (e.g. Oct 2016) that had zero active customers at a given month offset. These are genuine data gaps from tiny cohort sizes, not rendering errors, and are distinct from the near-zero (but nonzero) retention cells.

## 7. Scope boundaries

- The review-NLP extension (analyzing whether review sentiment differs by segment) was scoped as optional and not implemented. It remains a documented future extension.
- CLV is computed historically (cohort revenue per member, cumulative), not via a predictive repeat-purchase model — which would predict near-zero given the data and add little.