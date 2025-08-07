import yfinance as yf
import pandas as pd

# 可比公司列表（可根据行业自定义扩展）
comparable_tickers = {
    "MSFT": "Microsoft",
    "META": "Meta Platforms",
    "AMZN": "Amazon",
    "AAPL": "Apple",
    "NVDA": "NVIDIA"
}

def fetch_ev_ebitda_multiples(tickers: dict) -> pd.DataFrame:
    """
    拉取同行公司的 EV 和 EBITDA 数据，并计算 EV/EBITDA 倍数
    """
    results = []

    for symbol, name in tickers.items():
        try:
            t = yf.Ticker(symbol)
            info = t.info
            financials = t.financials

            market_cap = info.get("marketCap", None)
            total_debt = info.get("totalDebt", 0)
            cash = info.get("totalCash", 0)
            ev = market_cap + total_debt - cash if market_cap else None

            # 获取净利润、税、利息、折旧摊销
            net_income = financials.loc["Net Income"].iloc[0] if "Net Income" in financials.index else info.get("netIncomeToCommon")
            taxes = financials.loc["Income Tax Expense"].iloc[0] if "Income Tax Expense" in financials.index else 0
            interest = financials.loc["Interest Expense"].iloc[0] if "Interest Expense" in financials.index else 0
            depreciation = financials.loc["Depreciation"].iloc[0] if "Depreciation" in financials.index else info.get("depreciation", 0)
            amortization = financials.loc["Amortization"].iloc[0] if "Amortization" in financials.index else 0
            d_and_a = depreciation + amortization

            ebitda = net_income + taxes + interest + d_and_a if net_income else None
            multiple = ev / ebitda if ev and ebitda else None

            results.append({
                "Ticker": symbol,
                "Company": name,
                "EV": ev,
                "EBITDA": ebitda,
                "EV/EBITDA": multiple
            })

        except Exception as e:
            print(f"❌ Error fetching {symbol}: {e}")

    return pd.DataFrame(results)

if __name__ == "__main__":
    df = fetch_ev_ebitda_multiples(comparable_tickers)
        
    # 自动创建目录
    import os
    os.makedirs("data/processed", exist_ok=True)
    
    df.to_csv("data/processed/comps_ev_multiples.csv", index=False)
    print("📊 可比公司 EV/EBITDA 倍数表：")
    print(df)