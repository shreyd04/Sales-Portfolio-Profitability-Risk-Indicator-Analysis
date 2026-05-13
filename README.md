# Predictive Risk & Margin Diagnostic Tool — SuperStore Transaction Analysis

Project maintained as part of an applied research pipeline: a Predictive Risk & Margin Diagnostic Tool built to surface financial leakage and behavioral anomalies across retail transaction ecosystems. The work analyzes 10,000+ SuperStore transactions and produces actionable indicators for data-driven decision support, with a focus on ecosystem integrity and consumer-behavioral impacts.

## Major Findings (Executive Summary)
- Dataset: 10,000+ retail orders (SuperStore sample).
- Major discovery: a measured ~15% margin erosion in the `Home Office` segment versus baseline segment economics.
- Behavioral insight: observed "Discount Inelasticity" — deep discounts failed to increase order volume sufficiently, producing negative return on promotional spend and destroying unit economics for discounted SKUs.

These findings indicate systemic margins risk and motivate targeted interventions (pricing guardrails, discount caps, and prioritized monitoring of at-risk SKUs and customer cohorts).

## Project Overview
This repository implements a diagnostic tool that ingests order-level data, computes key risk signals, writes processed artifacts to a persistent store (PostgreSQL), and exposes an interactive Streamlit UI for exploration and monitoring. The analytic scope centers on margin diagnostics, leakage attribution, and behavioral signal construction that can be directly consumed by downstream AI systems (lead scoring, churn models, and promotional optimization).

Key objectives:
- Identify and quantify financial leakage at product/segment levels.
- Construct behavioral features (e.g., discount sensitivity, leakage flags) for model-ready feature stores.
- Provide an interactive, reproducible pipeline from notebook-based ETL to a production-like Streamlit UI.

## Technical Pipeline
This repository implements a compact ETL and reporting stack:

- Ingestion: raw CSV (SuperStore sample) loaded in Jupyter notebooks. The canonical raw file lives in `data/samplesuperstore.csv`.
- Preprocessing (notebooks & script): column standardization (spaces -> underscores, lowercasing), typed conversions, and engineered metrics (see Behavioral Data Science below). The primary processing notebook is `scripts/data_pipeline.ipynb`.
- Persistence: processed dataframe is written to a PostgreSQL table `orders` via SQLAlchemy and exported as `processed_sales_risk.csv` in the project root for compatibility with Streamlit and external consumers.
- UI & Visualization: a Streamlit app (see `scripts/app.py`) reads `processed_sales_risk.csv` and renders interactive Plotly visualizations for margin, leakage, and discount sensitivity.

Data flow (simplified):

1. data/samplesuperstore.csv (raw) ->
2. Jupyter ETL (`scripts/data_pipeline.ipynb`) -> pandas DataFrame (engineered columns) ->
3. PostgreSQL (`orders` table) + exported CSV: `processed_sales_risk.csv` ->
4. Streamlit UI (`scripts/app.py`) + plotly visualizations

Operational notes:
- The pipeline uses SQLAlchemy to stream the processed DataFrame into PostgreSQL (`orders` table). The pipeline also emits a CSV at the repository root to ensure Streamlit (which may run from the root) can access the artifact without path issues.

## Behavioral Data Science — Leakage Flag & Discount Sensitivity
The behavioral feature construction is intentionally minimal, interpretable, and directly actionable.

Engineered fields (naming follows pipeline normalization: lowercase with underscores):

- `margin_pct` — profit margin percentage per line: (profit / sales) * 100. Serves as the primary economic health metric.
- `leakage_flag` — a binary indicator of high-risk, promotional-induced leakage. Logic used in the pipeline:

  leakage_flag = 1 when (discount > 0.20) AND (profit < 0), else 0.

Rationale: an aggressive discount (greater than 20%) combined with negative profit denotes direct margin leakage driven by promotional mechanics. This flag is a conservative, interpretable signal intended for operational alerting and downstream feature ingestion.

Discount-Elasticity Analysis
- We analyze conditional distributions and segment-level aggregates to quantify whether discounting yields incremental volume that recovers margin. The core empirical observation — Discount Inelasticity — is that heavy discounts (20%+) in the `Home Office` cohort did not produce volume increases sufficient to offset margin loss, resulting in a net ~15% erosion of segment margin.

Correlation & Attribution
- The repo includes exploratory visualizations (Plotly) that show the relationship between discount bands and margin_pct, and segment-level aggregated profit curves. These support causal hypothesis generation (e.g., are discounts targeted to low-elasticity SKUs?) and help prioritize A/B or holdout experiments.

## Data Contract (Input / Output)

Input (expected canonical columns in `data/samplesuperstore.csv` — case-insensitive):

- order_id, order_date, ship_date, ship_mode, customer_id, customer_name,
- segment, country, city, state, postal_code, region,
- product_id, category, sub_category, product_name,
- sales, quantity, discount, profit

Processing outputs (added by the ETL):

- margin_pct (float): profit / sales * 100
- leakage_flag (int: 0|1): defined above
- normalized column naming: all columns converted to snake_case and lowercased for downstream consistency

Note: The pipeline uses latin1 decoding on CSV ingestion to handle SuperStore export encodings.

## How to Run (Professional, reproducible instructions)
The following steps produce a reproducible environment, a PostgreSQL instance, run the ETL, and launch the Streamlit UI. All commands assume macOS / zsh.

1) Create and activate a Conda environment

```bash
conda create -n superstore-ai python=3.10 -y
conda activate superstore-ai
pip install --upgrade pip
pip install pandas sqlalchemy psycopg2-binary streamlit plotly jupyterlab scikit-learn
```

2) PostgreSQL (local) — create DB and user

```bash
# Start postgres (homebrew) if not running
brew services start postgresql

# Launch psql and run (replace <your_password> if setting a password):
psql postgres
CREATE DATABASE sales_db;
CREATE ROLE shreyd04 WITH LOGIN;
GRANT ALL PRIVILEGES ON DATABASE sales_db TO shreyd04;
\q
```

Connection string used by the pipeline (SQLAlchemy):

postgresql://shreyd04@localhost:5432/sales_db

If you set a password for `shreyd04`, update the connection string to: `postgresql://shreyd04:<password>@localhost:5432/sales_db`.

3) Run the ETL

Option A — Run interactively in JupyterLab / Notebook:

```bash
jupyter lab
# Open scripts/data_pipeline.ipynb and run all cells (the notebook will write `processed_sales_risk.csv` and persist to PostgreSQL)
```

Option B — Convert the notebook to a script and run (recommended for automation):

```bash
jupyter nbconvert --to script "scripts/data_pipeline.ipynb" --output "scripts/data_pipeline.py"
python3 "scripts/data_pipeline.py"
```

After completion, verify `processed_sales_risk.csv` exists at the repository root and/or validate the `orders` table in `sales_db`.

4) Launch Streamlit UI

```bash
streamlit run scripts/app.py --server.port 8501
```

Open http://localhost:8501/ in your browser. The app reads `processed_sales_risk.csv` by default; if you prefer the database-backed flow, modify the app configuration to point to PostgreSQL via SQLAlchemy.

## Verification & Quick Checks
- Inspect summary statistics:

```python
import pandas as pd
df = pd.read_csv('processed_sales_risk.csv')
df.groupby('segment')['margin_pct'].agg(['mean','median','count']).sort_values('mean')
df[df['segment']=='Home Office']['margin_pct'].mean()
df['leakage_flag'].sum()
```

- Expected audit: Home Office segment mean margin shows ~15 percentage points lower than the primary cohort baseline (see Executive Summary).

## Future AI Scope (Feature Store & Model Integration)
This repository is intentionally structured to serve as an upstream feature source for AI systems in digital ecosystems. Concrete next steps:

- Feature hygiene & versioning: publish engineered fields (`margin_pct`, `leakage_flag`, discount bands, recency-frequency-value metrics) to a lightweight feature store (Feast or a columnar store) with schema and lineage.
- Lead scoring: augment customer-level aggregates with behavioral signals (propensity-to-return, discount-sensitivity index) and feed into supervised lead-scoring models for retention campaigns.
- Churn & cohort models: use segment-level margin dynamics and leakage incidence as features to predict account-level churn risk or SKU de-listing risk.
- Counterfactual and uplift modeling: design holdout/promotion experiments and use this dataset to estimate incremental volume and margin at different promotional levels.

AI-ready data contract: each feature should carry (1) stable name, (2) dtype, (3) computation SQL/pseudocode, and (4) last-refresh timestamp. This README and the `processed_sales_risk.csv` provide the first iteration of that contract.

## Governance and Ecosystem Integrity
The diagnostic tool is positioned to support policy guardrails in retail-fintech ecosystems: detect predatory promotion patterns, protect unit economics, and maintain long-term marketplace liquidity. Use the `leakage_flag` and segment diagnostics to implement automated rules (alerting, discount caps) and to feed human-in-the-loop review workflows.

## Suggested Next Steps
1. Surface feature versioning (add a lightweight `features/` manifest or adopt Feast).
2. Add unit tests and data validation (great_expectations or pandera) on ingestion outputs.
3. Implement a scheduled ETL job (Airflow/Cron) that writes time-partitioned feature tables for downstream model training.

## Contact & Attribution
Project: SuperStore Transaction Margin Diagnostic
Author: repository maintainer
Institutional fit: aligns with Jio Institute’s interest in AI for Digital Ecosystems and Consumer Behavior—bridging microeconomic analysis with actionable ML-ready features.

---
For operational issues or to request feature definitions for model integration, open an issue or submit a Pull Request with a `features/` manifest and test vector.

Tableau Dashboard : 
https://public.tableau.com/app/profile/shreya.dubey1172/viz/ProtfolioProfitabilityandRiskIndicatorDashboard/SuperStoreSalesDashboard