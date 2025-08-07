# pe_model/pe_calc.py

import yfinance as yf
from prediction_tools.eps_blender import blend_eps

def get_current_price(ticker="GOOG") -> float:
    """
    从 yfinance 获取 Alphabet 当前股价
    """
    stock = yf.Ticker(ticker)
    price = stock.info.get("currentPrice")
    if price is None:
        raise ValueError("⚠️ 当前价格获取失败，请检查 ticker 或 API 状态")
    return price

def calculate_forward_pe(price: float, eps: float) -> float:
    """
    Forward PE = 当前价格 / EPS 预测
    """
    if eps == 0:
        raise ZeroDivisionError("EPS 为 0，无法计算 PE")
    return round(price / eps, 2)

if __name__ == "__main__":
    print("📊 正在融合 EPS（三表 + ARIMA + Comps）...")
    eps_final = blend_eps()  # 调用三模型融合，已自动执行各模块

    print("\n💵 正在获取 Alphabet 当前股价...")
    price = get_current_price("GOOG")

    pe = calculate_forward_pe(price, eps_final)

    print(f"\n💰 当前 Alphabet 股价：${price:.2f}")
    print(f"🔮 融合 EPS 预测（2025E）：{eps_final:.2f}")
    print(f"📈 Forward PE (2025E) = {price:.2f} / {eps_final:.2f} = {pe}")