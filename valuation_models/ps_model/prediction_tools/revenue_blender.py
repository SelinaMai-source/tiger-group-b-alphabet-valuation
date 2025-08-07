from .linear_trend import forecast_revenue_linear
from .arima_forecast import forecast_revenue_arima
from .comparable_regression import (
    load_comparable_forecasts,
    train_revenue_regression,
    get_alphabet_struct,
    predict_alphabet_revenue
)
from .consensus_forecast import forecast_revenue_consensus

def get_blended_revenue(ticker="GOOG") -> float:
    # 📈 Linear trend model
    rev_linear = forecast_revenue_linear(ticker)
    print(f"📈 线性回归预测：${rev_linear / 1e9:.2f}B")

    # 🧠 ARIMA time series model
    rev_arima = forecast_revenue_arima(ticker)
    print(f"🧠 ARIMA 预测：${rev_arima / 1e9:.2f}B")

    # 🤝 Comparable companies regression model
    df_comps = load_comparable_forecasts()
    model_comps = train_revenue_regression(df_comps)
    mc, gm, nm = get_alphabet_struct(ticker)
    rev_comps = predict_alphabet_revenue(model_comps, mc, gm, nm)
    print(f"🤝 可比公司结构回归预测：${rev_comps / 1e9:.2f}B")

    # 🗣️ Consensus forecast
    rev_consensus = forecast_revenue_consensus(ticker)
    print(f"🗣️ 分析师共识预测：${rev_consensus / 1e9:.2f}B")

    # 🧮 融合计算（均等权重）
    weights = {
        "linear": 0.25,
        "arima": 0.25,
        "comps": 0.25,
        "consensus": 0.25
    }

    revenue_blended = (
        weights["linear"] * rev_linear +
        weights["arima"] * rev_arima +
        weights["comps"] * rev_comps +
        weights["consensus"] * rev_consensus
    )

    print(f"\n✅ 加权融合营收（2025E）：${revenue_blended / 1e9:.2f}B")
    return revenue_blended

if __name__ == "__main__":
    get_blended_revenue()