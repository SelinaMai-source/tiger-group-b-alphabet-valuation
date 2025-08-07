# pe_model/prediction_tools/three_statement_forecast.py

import yfinance as yf
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os

def get_historical_revenue(ticker="GOOG") -> pd.Series:
    """
    从 yfinance 拉取 Alphabet 的历史营收（年级别）
    """
    t = yf.Ticker(ticker)
    try:
        revenue_series = t.financials.loc["Total Revenue"].sort_index()
        revenue_series.index = pd.to_datetime(revenue_series.index)
        revenue_series = revenue_series.sort_index()
        return revenue_series
    except Exception as e:
        print(f"Error fetching financials for {ticker}: {e}")
        return None

def get_data_dir():
    """
    获取数据目录的绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data", "processed")
    return data_dir

def reconstruct_past_eps(revenue_series: pd.Series, net_margin=0.22, shares_outstanding=13_000_000_000):
    """
    反推出过去10年的历史 EPS，用于 ARIMA 时间序列建模
    """
    df = pd.DataFrame({
        "Year": revenue_series.index.year,
        "Revenue": revenue_series.values
    })
    df["Net_Income"] = df["Revenue"] * net_margin
    df["EPS"] = df["Net_Income"] / shares_outstanding

    try:
        data_dir = get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "eps_history_reconstructed.csv")
        df.to_csv(file_path, index=False)
        print(f"✅ 已保存历史 EPS：{file_path}")
    except Exception as e:
        print(f"⚠️ 保存历史EPS失败：{e}")
    
    return df

def forecast_revenue(revenue_series: pd.Series, years_ahead=5) -> pd.DataFrame:
    """
    用线性回归预测未来5年营收
    """
    x = np.arange(len(revenue_series)).reshape(-1, 1)
    y = revenue_series.values.reshape(-1, 1)

    model = LinearRegression()
    model.fit(x, y)

    future_x = np.arange(len(revenue_series), len(revenue_series) + years_ahead).reshape(-1, 1)
    forecast_y = model.predict(future_x)

    forecast_years = [revenue_series.index[-1].year + i + 1 for i in range(years_ahead)]
    forecast_df = pd.DataFrame({
        "Year": forecast_years,
        "Forecast_Revenue": forecast_y.flatten()
    })
    return forecast_df

def forecast_eps(revenue_forecast_df: pd.DataFrame, net_margin=0.22, shares_outstanding=13_000_000_000):
    """
    用预测营收 × 净利率 / 股本，计算未来 EPS
    """
    df = revenue_forecast_df.copy()
    df["Net_Income"] = df["Forecast_Revenue"] * net_margin
    df["EPS"] = df["Net_Income"] / shares_outstanding
    return df

if __name__ == "__main__":
    revenue_series = get_historical_revenue("GOOG")
    if revenue_series is not None:
        # Step 1：重建历史 EPS（用于 ARIMA）
        hist_df = reconstruct_past_eps(revenue_series)
        print(hist_df.tail())

        # Step 2：预测未来 EPS
        forecast_df = forecast_revenue(revenue_series)
        result_df = forecast_eps(forecast_df)

        # Step 3：保存未来预测
        try:
            data_dir = get_data_dir()
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, "eps_forecast_three_statement.csv")
            result_df.to_csv(file_path, index=False)
            print(f"✅ 已保存未来预测 EPS：{file_path}")
        except Exception as e:
            print(f"⚠️ 保存未来预测EPS失败：{e}")
        
        print(result_df)

def load_three_statement_eps(forecast_path=None, target_year=2025) -> float:
    """
    加载三表预测模型生成的 EPS 并返回指定年份的预测值（默认2025）
    """
    if forecast_path is None:
        data_dir = get_data_dir()
        forecast_path = os.path.join(data_dir, "eps_forecast_three_statement.csv")
    
    if not os.path.exists(forecast_path):
        print(f"⚠️ 找不到预测文件：{forecast_path}，使用默认值")
        return 6.34  # 默认值

    try:
        df = pd.read_csv(forecast_path)
        row = df[df["Year"] == target_year]
        if row.empty:
            print(f"⚠️ 预测文件中不包含年份 {target_year} 的数据，使用最后一个值")
            return float(df["EPS"].iloc[-1])
        
        return float(row["EPS"].values[0])
    except Exception as e:
        print(f"⚠️ 读取预测文件失败：{e}，使用默认值")
        return 6.34  # 默认值