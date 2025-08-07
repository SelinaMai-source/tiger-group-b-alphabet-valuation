# terminal_value.py
import pandas as pd
import numpy as np
from statsmodels.tsa.arima.model import ARIMA
from fcf_formula import get_historical_fcf
from wacc_formula import get_wacc


def forecast_fcf_next_year(fcf_series: pd.Series) -> float:
    """
    使用 ARIMA(1,1,0) 模型预测下一年的自由现金流（FCF）
    """
    fcf_series = fcf_series.dropna()
    if len(fcf_series) < 3:
        raise ValueError("历史 FCF 数据不足，至少需要3年以上数据用于建模。")
    
    model = ARIMA(fcf_series, order=(1, 1, 0))
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=1)
    return forecast.iloc[0]


def calculate_terminal_value(fcf_next_year: float, wacc: float, g: float = 0.025) -> float:
    """
    使用戈登增长模型（Gordon Growth Model）计算永续终值 Terminal Value
    """
    if wacc <= g:
        raise ValueError("⚠️ WACC 必须大于 g，否则终值无法计算。")
    return fcf_next_year / (wacc - g)



def get_fcf_and_tv(ticker="GOOG", g=0.025):
    """
    封装获取 fcf_next 和 tv 的函数，供其他模块调用
    """
    fcf_series = get_historical_fcf(ticker)
    fcf_next = forecast_fcf_next_year(fcf_series)
    wacc = get_wacc(ticker)
    tv = calculate_terminal_value(fcf_next, wacc, g)
    return fcf_next, tv


if __name__ == "__main__":
    TICKER = "GOOG"
    try:
        fcf_series = get_historical_fcf(TICKER)
        fcf_next = forecast_fcf_next_year(fcf_series)
        wacc = get_wacc(TICKER)

        tv = calculate_terminal_value(fcf_next, wacc)

        print("📈 使用 ARIMA 模型预测的下一年 FCF:")
        print(f"  FCF_next_year (预测): ${fcf_next:,.2f}")
        print(f"  WACC                : {wacc:.2%}")
        print(f"  永续增长率 g         : 2.5%")
        print(f"\n✅ 计算得到 Terminal Value（永续终值）: ${tv:,.2f}")

    except Exception as e:
        print(f"❌ Error calculating terminal value: {e}")