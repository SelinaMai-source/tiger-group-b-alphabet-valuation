import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA
from fcf_formula import get_historical_fcf
from wacc_formula import get_wacc  # 你之前模块化的 WACC 获取器

# -------------------------------
# ✅ ARIMA 预测未来 N 年 FCF
# -------------------------------
def forecast_fcf_arima(ticker: str, years_forward: int = 5) -> list:
    historical_fcf = get_historical_fcf(ticker)
    if historical_fcf.empty:
        raise ValueError("No historical FCF data found.")
    
    model = ARIMA(historical_fcf, order=(1, 1, 0))
    results = model.fit()

    forecast = results.forecast(steps=years_forward)
    return list(forecast)

# -------------------------------
# ✅ 计算终值（TV）
# -------------------------------
def calculate_terminal_value(last_fcf: float, wacc: float, g: float = 0.025) -> float:
    """
    使用永续增长模型 TV = FCF_{n+1} / (WACC - g)
    默认长期增长率 g = 2.5%
    """
    fcf_n_plus_1 = last_fcf * (1 + g)
    return fcf_n_plus_1 / (wacc - g)

# -------------------------------
# ✅ 计算 DCF 企业价值
# -------------------------------
def calculate_dcf_value(ticker: str, years_forward: int = 5, g: float = 0.025) -> float:
    fcfs = forecast_fcf_arima(ticker, years_forward)
    wacc = get_wacc(ticker)

    if wacc is None:
        raise ValueError("WACC is None, cannot proceed.")

    # 折现预测期内每年的FCF
    discounted_fcfs = [
        fcf / ((1 + wacc) ** (t + 1)) for t, fcf in enumerate(fcfs)
    ]

    # 折现 TV
    tv = calculate_terminal_value(fcfs[-1], wacc, g)
    discounted_tv = tv / ((1 + wacc) ** years_forward)

    total_value = sum(discounted_fcfs) + discounted_tv
    return total_value

# -------------------------------
# 🧪 测试主函数
# -------------------------------
if __name__ == "__main__":
    ticker = "GOOG"
    try:
        dcf_value = calculate_dcf_value(ticker)
        print(f"\n💰 估算企业价值（{ticker}）：${dcf_value:,.2f}")
    except Exception as e:
        print(f"❌ DCF 计算失败：{e}")