import yfinance as yf
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings
warnings.filterwarnings("ignore")

def forecast_revenue_arima(ticker="GOOG") -> float:
    """
    使用 ARIMA 模型预测 2025 年营收
    """
    try:
        t = yf.Ticker(ticker)
        revenue_series = t.financials.loc["Total Revenue"].sort_index()
        revenue_series.index = pd.to_datetime(revenue_series.index).year
        rev_series = pd.Series(revenue_series.values, index=revenue_series.index.astype(int))

        # 建模（ARIMA(1,1,0)）
        model = ARIMA(rev_series, order=(1, 1, 0))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=1)

        return forecast.iloc[0]
    except Exception as e:
        print(f"❌ ARIMA 预测营收失败：{e}")
        return None