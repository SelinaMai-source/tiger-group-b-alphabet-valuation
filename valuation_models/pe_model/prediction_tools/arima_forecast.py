# pe_model/prediction_tools/arima_forecast.py

import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
import warnings
import os
warnings.filterwarnings("ignore")

def load_eps_series(filepath="data/processed/eps_history_reconstructed.csv") -> pd.Series:
    """
    从三表重建结果中加载历史 EPS 序列，用于时间序列预测
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ EPS 历史文件未找到：{filepath}")
    
    df = pd.read_csv(filepath)
    eps_series = pd.Series(df["EPS"].values, index=df["Year"])
    eps_series.index = eps_series.index.astype(int)
    eps_series.name = "EPS"
    return eps_series

def forecast_eps_arima(eps_series: pd.Series, forecast_years=5) -> pd.DataFrame:
    """
    使用 ARIMA 模型预测未来 EPS（年度）
    """
    model = ARIMA(eps_series, order=(1, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=forecast_years)

    forecast_years_index = [eps_series.index[-1] + i + 1 for i in range(forecast_years)]
    forecast_df = pd.DataFrame({
        "Year": forecast_years_index,
        "EPS_ARIMA": forecast.values
    })

    os.makedirs("data/processed", exist_ok=True)
    forecast_df.to_csv("data/processed/eps_forecast_arima.csv", index=False)
    return forecast_df

if __name__ == "__main__":
    eps_series = load_eps_series()
    forecast_df = forecast_eps_arima(eps_series)
    print("✅ ARIMA EPS 预测完成：")
    print(forecast_df)

def load_arima_eps(filepath="data/processed/eps_forecast_arima.csv") -> float:
    """
    加载 ARIMA 模型预测的第一年 EPS（用于 PE 模型）
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ ARIMA EPS 文件未找到：{filepath}")
    
    df = pd.read_csv(filepath)
    if df.empty:
        raise ValueError("❌ ARIMA EPS 预测结果为空")
    
    return float(df.iloc[0]["EPS_ARIMA"])