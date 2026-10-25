# Hierarchical Retail Demand Forecasting

**Status: scaffold only — not trained or benchmarked.**

## Business question
Forecast 28-day item-store unit sales, then evaluate accuracy and uncertainty across item, category and store levels. Do not mislabel unit sales as revenue.

## Primary data: M5 Forecasting Accuracy
Official source: https://www.kaggle.com/competitions/m5-forecasting-accuracy/data

- `calendar.csv`: day identifiers, dates, calendar events and SNAP indicators
- `sales_train_validation.csv`: item/store historical daily demand (d_1 through d_1913)
- `sell_prices.csv`: store/item/week sell prices
- Access may require Kaggle login and competition rules. Do not redistribute data.

## First MVP
1. Select one manageable store/category for reproducibility.
2. Validate dates, IDs, missingness, intermittent zeros and price joins.
3. Implement seasonal naive (7-day lag), moving-average and optional ETS.
4. Rolling-origin backtest, strictly using history available at each forecast origin.
5. Evaluate MAE, WAPE, sMAPE and optional WRMSSE with correctly applied M5 scales.
6. Plot actual versus 28-day forecast, errors, and uncertainty diagnostics.
7. Add global lag-feature model, hierarchy reconciliation, dashboard and CI only once baseline works.

## Proposed stack
Python, pandas, matplotlib, statsmodels, scikit-learn/LightGBM candidate, pytest, MLflow optional.

See [source register](../../docs/DATASET_REGISTER.md), [data card](docs/DATA_CARD.md), [research review](docs/RESEARCH_REVIEW.md).

**No forecast results or validated production pipeline currently exist.**
