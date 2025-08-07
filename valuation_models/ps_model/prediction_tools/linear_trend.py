import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

def forecast_revenue_linear(ticker="GOOG") -> float:
    """
    使用线性回归模型预测下一年的营收（2025E）
    """
    t = yf.Ticker(ticker)
    try:
        # 获取财报中的年度总营收
        revenue_series = t.financials.loc["Total Revenue"].sort_index()
        revenue_series.index = pd.to_datetime(revenue_series.index)
        revenue_series = revenue_series.sort_index()

        # 准备训练数据
        x = np.arange(len(revenue_series)).reshape(-1, 1)  # 0, 1, 2, ...
        y = revenue_series.values.reshape(-1, 1)

        model = LinearRegression()
        model.fit(x, y)

        # 预测下一年（x = len）
        next_revenue = model.predict([[len(revenue_series)]])[0][0]
        return next_revenue
    except Exception as e:
        print(f"❌ Linear trend prediction error: {e}")
        return None