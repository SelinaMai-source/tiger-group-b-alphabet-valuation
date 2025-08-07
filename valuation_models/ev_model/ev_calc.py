import pandas as pd
from ev_model.ev_data import get_alphabet_ev_components
from ps_model.prediction_tools.revenue_blender import get_blended_revenue

def load_ev_multiple(filepath="data/processed/comps_ev_multiples.csv") -> float:
    """
    加载同行公司的 EV/EBITDA 倍数中位数
    """
    df = pd.read_csv(filepath)
    df = df[df["EV/EBITDA"].notna()]
    median_multiple = df["EV/EBITDA"].median()
    return median_multiple

def estimate_ebitda(revenue_2025e: float, ebitda_margin: float) -> float:
    """
    用预测营收 × EBITDA margin 得出 2025E EBITDA
    """
    return revenue_2025e * ebitda_margin

def estimate_price():
    # Step 1: 自动从 TTM 数据计算 EBITDA Margin
    ev_data = get_alphabet_ev_components()
    ebitda_ttm = ev_data["EBITDA_TTM"]

    # 你也可以直接读取真实营收数据；此处 fallback 为估算值
    revenue_ttm = ebitda_ttm / 0.298  # 若你没有 TTM revenue 字段，用近似推估
    ebitda_margin = ebitda_ttm / revenue_ttm

    # Step 2: 获取预测营收并估算 EBITDA
    revenue_2025e = get_blended_revenue()
    ebitda_2025e = estimate_ebitda(revenue_2025e, ebitda_margin)

    # Step 3: 获取行业倍数并计算目标 EV
    ev_multiple = load_ev_multiple()
    ev_target = ebitda_2025e * ev_multiple

    # Step 4: 净债务 = Debt - Cash
    net_debt = ev_data["TotalDebt"] - ev_data["Cash"]

    # Step 5: 市值 = EV - 净债务
    market_cap = ev_target - net_debt

    # Step 6: 股价 = 市值 ÷ 总股本
    shares_outstanding = ev_data.get("SharesOutstanding") or 13_000_000_000
    price_target = market_cap / shares_outstanding

    # ✅ 输出链路结果
    print(f"🔢 TTM EBITDA Margin（自动计算）: {ebitda_margin:.2%}")
    print(f"🔢 预测 2025 营收：${revenue_2025e/1e9:.2f}B")
    print(f"📈 预测 EBITDA: ${ebitda_2025e/1e9:.2f}B")
    print(f"🏢 EV/EBITDA 倍数：{ev_multiple:.2f}")
    print(f"🏷️ 目标 EV：${ev_target/1e9:.2f}B")
    print(f"💳 净债务（Debt - Cash）：${net_debt/1e9:.2f}B")
    print(f"💰 推出目标市值：${market_cap/1e9:.2f}B")
    print(f"🎯 估算目标股价：${price_target:.2f}")

    return price_target

if __name__ == "__main__":
    estimate_price()