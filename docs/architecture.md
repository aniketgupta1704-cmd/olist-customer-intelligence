# Architecture

![Architecture diagram](images/architecture_diagram.png)

## Design principle

The pipeline separates **heavy offline computation** from a **lightweight serving layer**:

- **Offline (notebooks + src/):** SQL joins in DuckDB, feature engineering, clustering, model training, and causal analysis. These produce small artifacts — segmented customer tables, a cohort matrix, propensity scores, a metrics JSON, and pickled models.
- **Serving (Streamlit app):** reads only the precomputed artifacts. No heavy computation, no raw data dependency, no database at runtime. This keeps the deployed app fast and within cloud size limits.

This is the standard production pattern: compute once, serve many times.

## Data flow

```
9 Olist CSVs
     │
     ▼  (DuckDB: multi-table SQL, window functions, CTEs)
Feature engineering  ──►  RFM · CLV · cohort matrices
     │
     ▼  (K-Means, k=4)
RFM Segmentation
     │
     ├──►  Cohort Analysis            (triangular retention)
     ├──►  Repeat-Purchase Prediction (Random Forest, first-order features)
     └──►  Propensity Score Matching  (delivery → review score)
     │
     ▼
Business Strategy  ──►  Budget Optimizer  ──►  Streamlit Dashboard
```

The segmentation layer is the hub. It feeds three parallel analyses that converge into the business strategy and budget optimizer. The prediction→strategy path carries the project's key pivot: because loyalty proved unpredictable, the analysis turned to causal inference to find a lever the business can actually control.

## Layer responsibilities

| Layer | Location | Responsibility |
|---|---|---|
| Data loading | `src/data_loader.py` | DuckDB connection, CSV ingestion, query execution |
| Feature engineering | `src/feature_engineering.py` | RFM, cohort retention, CLV |
| Segmentation | `src/segmentation.py` | preprocessing, clustering, labeling |
| Prediction | `src/predictor.py` | first-order feature pipeline, classifiers |
| Causal analysis | `src/causal_analysis.py` | propensity model, matching, balance, ATT |
| Budget allocation | `src/budget_allocator.py` | expected-value framework, greedy ROI allocation |
| Reporting | `src/pdf_report.py` | executive-summary PDF generation |
| Presentation | `app/` | Streamlit dashboard (Home + 6 pages) |
