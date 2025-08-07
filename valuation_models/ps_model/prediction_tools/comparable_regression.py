import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
import yfinance as yf

def load_comparable_forecasts(tickers=["AAPL", "MSFT", "AMZN", "META", "NVDA"]) -> pd.DataFrame:
    """
    自动抓取可比公司结构特征 + 市值 + 营收，用于结构性回归预测 Alphabet 营收
    """
    comps = []
    for ticker in tickers:
        try:
            t = yf.Ticker(ticker)
            info = t.info

            market_cap = info.get("marketCap")
            revenue = info.get("totalRevenue")
            gross_profit = info.get("grossProfits")
            net_income = info.get("netIncomeToCommon")

            gross_margin = gross_profit / revenue if gross_profit and revenue else None
            net_margin = net_income / revenue if net_income and revenue else None

            if market_cap and revenue and gross_margin and net_margin:
                comps.append({
                    "Ticker": ticker,
                    "MarketCap": market_cap,
                    "GrossMargin": gross_margin,
                    "NetMargin": net_margin,
                    "RevForecast2025": revenue * 1.10  # 假设2025年增长10%
                })
        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")
            continue

    return pd.DataFrame(comps)

def train_revenue_regression(df: pd.DataFrame) -> LinearRegression:
    """
    训练结构回归模型：RevForecast2025 ~ MarketCap + GrossMargin + NetMargin
    """
    X = df[["MarketCap", "GrossMargin", "NetMargin"]]
    y = df["RevForecast2025"]
    model = LinearRegression()
    model.fit(X, y)
    return model

def get_alphabet_struct(ticker="GOOG"):
    """
    抓取 Alphabet 当前结构特征
    """
    t = yf.Ticker(ticker)
    info = t.info

    market_cap = info.get("marketCap")
    revenue = info.get("totalRevenue")
    gross_profit = info.get("grossProfits")
    net_income = info.get("netIncomeToCommon")

    gross_margin = gross_profit / revenue if gross_profit and revenue else None
    net_margin = net_income / revenue if net_income and revenue else None

    return market_cap, gross_margin, net_margin

def predict_alphabet_revenue(model: LinearRegression, market_cap, gross_margin, net_margin):
    """
    预测 Alphabet 2025 营收
    """
    X_pred = np.array([[market_cap, gross_margin, net_margin]])
    revenue_pred = model.predict(X_pred)
    return revenue_pred[0]

if __name__ == "__main__":
    df = load_comparable_forecasts()
    print("✅ 可比公司结构数据：")
    print(df)

    model = train_revenue_regression(df)
    mc, gm, nm = get_alphabet_struct()
    pred = predict_alphabet_revenue(model, mc, gm, nm)

    print(f"📈 结构性回归预测 Alphabet 2025 营收：${pred / 1e9:.2f}B")