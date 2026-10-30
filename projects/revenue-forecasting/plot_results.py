"""Plot public synthetic demo series without presenting them as client forecasts."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pipeline import demo_series

ROOT=Path(__file__).resolve().parent
def main():
    history=demo_series().query("series == 'series_00'").sort_values("month")
    forecasts=pd.read_csv(ROOT/"outputs"/"forecasts.csv",parse_dates=["month"])
    future=forecasts.query("series == 'series_00'").sort_values("month")
    scores=pd.read_csv(ROOT/"outputs"/"backtest.csv")
    choice=str(future.selected_model.iloc[0])
    fig,ax=plt.subplots(figsize=(10,4))
    ax.plot(history.month,history.revenue,label="Synthetic historical revenue")
    ax.plot(future.month,future.forecast,marker="o",linestyle="--",label=f"3-month forecast ({choice})")
    ax.set_title("Synthetic financial series 00 — model selection by 1-step MAE")
    ax.set_xlabel("Month"); ax.set_ylabel("Synthetic currency units")
    ax.legend();fig.autofmt_xdate();fig.tight_layout()
    fig.savefig(ROOT/"outputs"/"revenue_forecast_example.png",dpi=170)
    plt.close(fig)
    print("Wrote",ROOT/"outputs"/"revenue_forecast_example.png")
if __name__=="__main__":
    main()
