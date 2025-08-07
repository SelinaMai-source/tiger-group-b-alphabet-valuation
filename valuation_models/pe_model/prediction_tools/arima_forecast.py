# pe_model/prediction_tools/arima_forecast.py

import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
import os

def get_data_dir():
    """
    获取数据目录的绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data", "processed")
    return data_dir

def load_historical_eps(filepath=None):
    """
    加载历史 EPS 数据
    """
    if filepath is None:
        data_dir = get_data_dir()
        filepath = os.path.join(data_dir, "eps_history_reconstructed.csv")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 未找到历史EPS文件：{filepath}")
    
    df = pd.read_csv(filepath)
    return df["EPS"].values

def forecast_eps_arima(eps_series, periods=5):
    """
    使用 ARIMA 模型预测未来 EPS
    """
    try:
        # 拟合 ARIMA(1,1,1) 模型
        model = ARIMA(eps_series, order=(1, 1, 1))
        fitted_model = model.fit()
        
        # 预测未来5年
        forecast = fitted_model.forecast(steps=periods)
        
        return forecast.values
    except Exception as e:
        print(f"⚠️ ARIMA预测失败：{e}")
        # 如果ARIMA失败，使用简单的线性趋势
        return np.linspace(eps_series[-1], eps_series[-1] * 1.2, periods)

if __name__ == "__main__":
    try:
        # 加载历史数据
        eps_series = load_historical_eps()
        
        # 预测未来EPS
        forecast_values = forecast_eps_arima(eps_series)
        
        # 创建预测结果DataFrame
        forecast_years = [2025 + i for i in range(len(forecast_values))]
        forecast_df = pd.DataFrame({
            "Year": forecast_years,
            "EPS_ARIMA": forecast_values
        })
        
        # 保存预测结果
        data_dir = get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "eps_forecast_arima.csv")
        forecast_df.to_csv(file_path, index=False)
        print(f"✅ ARIMA EPS 预测完成：{file_path}")
        print(forecast_df)
        
    except Exception as e:
        print(f"❌ ARIMA预测失败：{e}")

def load_arima_eps(filepath=None, target_year=2025):
    """
    加载ARIMA预测的EPS数据
    """
    if filepath is None:
        data_dir = get_data_dir()
        filepath = os.path.join(data_dir, "eps_forecast_arima.csv")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 未找到ARIMA预测文件：{filepath}")
    
    df = pd.read_csv(filepath)
    row = df[df["Year"] == target_year]
    if row.empty:
        raise ValueError(f"❌ ARIMA预测文件中不包含年份 {target_year} 的数据")
    
    return float(row["EPS_ARIMA"].values[0])