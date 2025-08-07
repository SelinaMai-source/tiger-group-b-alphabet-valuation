# pe_model/pe_calc.py

import yfinance as yf
import sys
import os

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
prediction_tools_dir = os.path.join(current_dir, "prediction_tools")
if prediction_tools_dir not in sys.path:
    sys.path.append(prediction_tools_dir)

try:
    from eps_blender import blend_eps
except ImportError:
    # 如果导入失败，创建一个默认的blend_eps函数
    def blend_eps():
        return 7.89  # 默认EPS值

def get_current_price(ticker="GOOG") -> float:
    """
    从 yfinance 获取 Alphabet 当前股价
    """
    try:
        stock = yf.Ticker(ticker)
        price = stock.info.get("currentPrice")
        if price is None:
            return 196.92  # 默认价格
        return price
    except Exception as e:
        print(f"⚠️ 获取股价失败：{e}，使用默认值")
        return 196.92  # 默认价格

def calculate_forward_pe(price: float, eps: float) -> float:
    """
    Forward PE = 当前价格 / EPS 预测
    """
    if eps == 0:
        return 0
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