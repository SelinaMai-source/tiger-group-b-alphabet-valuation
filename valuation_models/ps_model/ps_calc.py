import yfinance as yf
import sys
import os

# 添加当前目录到路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_market_cap(ticker="GOOG") -> float:
    t = yf.Ticker(ticker)
    market_cap = t.info.get("marketCap")
    if market_cap is None:
        raise ValueError("⚠️ 无法获取市值")
    return market_cap

def calculate_forward_ps(market_cap: float, forecast_revenue: float) -> float:
    if forecast_revenue == 0:
        raise ZeroDivisionError("⚠️ 营收为0，无法计算 PS")
    return round(market_cap / forecast_revenue, 2)

if __name__ == "__main__":
    print("🔍 获取融合预测营收（2025E）...")
    try:
        from prediction_tools.revenue_blender import get_blended_revenue
        revenue_2025 = get_blended_revenue("GOOG")
    except ImportError:
        # 如果导入失败，使用默认值
        revenue_2025 = 374.9e9  # 374.9B
        print("⚠️ 无法导入revenue_blender，使用默认值")

    print("\n💰 获取当前市值...")
    market_cap = get_market_cap("GOOG")

    forward_ps = calculate_forward_ps(market_cap, revenue_2025)

    print(f"\n📈 Forward PS (2025E) = {market_cap / 1e9:.2f}B / {revenue_2025 / 1e9:.2f}B = {forward_ps}")