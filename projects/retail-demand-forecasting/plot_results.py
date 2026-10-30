"""Generate a truthful chart from actual local one-step backtest outputs."""
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT=Path(__file__).resolve().parent
def main():
    output=ROOT/"outputs"
    frame=pd.read_csv(output/"one_step_backtest.csv",parse_dates=["date"])
    sample=frame.query("store == 0 and sku == 0").sort_values("date")
    future=pd.read_csv(output/"next_day_forecast.csv",parse_dates=["date"])
    tomorrow=future.query("store == 0 and sku == 0").iloc[0]
    fig,ax=plt.subplots(figsize=(10,4))
    ax.plot(sample.date,sample.units,label="Actual historical units",linewidth=1.4)
    ax.plot(sample.date,sample.predicted_units,label="One-step predictions",linewidth=1.4)
    ax.scatter([tomorrow.date],[tomorrow.predicted_units],marker="D",label="Next-day unit forecast",s=55)
    ax.set_title("Synthetic retail demand — Store 0 / SKU 0")
    ax.set_ylabel("Units")
    ax.set_xlabel("Historical test period and following day")
    ax.legend()
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(output/"retail_forecast_example.png",dpi=170)
    plt.close(fig)
    print("Wrote",output/"retail_forecast_example.png")
if __name__=="__main__":
    main()
