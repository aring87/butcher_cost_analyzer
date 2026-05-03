# Butcher Shop Cost Analyzer — Streamlit Dashboard

A web dashboard for butcher shop order quotes and cost analysis.

## Features

- Customer/order form
- Product database table
- Add meat items to an order
- Final weighed pricing
- Yield/shrink cost calculation
- Labor, packaging, and overhead costs
- Target margin pricing
- Deposit and balance due
- Profit margin summary
- Downloadable cost analysis CSV
- Downloadable customer receipt

## Install

Open PowerShell or Command Prompt inside this folder.

```powershell
py -m pip install -r requirements.txt
```

## Run

```powershell
py -m streamlit run streamlit_app.py
```

Streamlit will open the dashboard in your browser.

## Edit Products

Edit this file:

```text
data/products.csv
```

Product CSV columns:

```csv
sku,name,category,wholesale_cost_per_lb,yield_percent,default_retail_price_per_lb
```

## Edit Default Business Settings

Edit:

```text
config.py
```

Defaults:

```python
LABOR_RATE_PER_HOUR = 24.00
OVERHEAD_COST_PER_ORDER_ITEM = 3.00
TARGET_MARGIN_PERCENT = 35.00
```

## Recommended Next Upgrade

Add an Excel import/upload screen so you can upload your existing butcher shop price sheet directly into the dashboard.
