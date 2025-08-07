# pe_model/comp_fetcher.py

import yfinance as yf
import pandas as pd
from comparables import comparable_tickers

def fetch_comparable_financials(tickers: dict) -> pd.DataFrame:
    """
    拉取所有可比公司的核心财务指标：
    市值、EPS、PE、营收增长率、净利率、毛利率
    """
    results = []

    for symbol, name in tickers.items():
        try:
            t = yf.Ticker(symbol)
            info = t.info

            # 当前数据
            price = info.get("currentPrice")
            eps = info.get("trailingEps")
            market_cap = info.get("marketCap")
            pe = price / eps if eps else None
            revenue_ttm = info.get("totalRevenue")
            net_income = info.get("netIncomeToCommon")
            gross_profit = info.get("grossProfits")

            # 毛利率和净利率
            gross_margin = gross_profit / revenue_ttm if gross_profit and revenue_ttm else None
            net_margin = net_income / revenue_ttm if net_income and revenue_ttm else None

            # 过去两年营收：计算增长率
            financials = t.financials
            revenue_series = financials.loc["Total Revenue"]
            if len(revenue_series) >= 2:
                revenue_yoy = (revenue_series[0] - revenue_series[1]) / revenue_series[1]
            else:
                revenue_yoy = None

            results.append({
                "Ticker": symbol,
                "Company": name,
                "Price": price,
                "EPS": eps,
                "PE": pe,
                "MarketCap": market_cap,
                "Revenue YoY": revenue_yoy,
                "Gross Margin": gross_margin,
                "Net Margin": net_margin
            })

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")

    return pd.DataFrame(results)


if __name__ == "__main__":
    df = fetch_comparable_financials(comparable_tickers)
    df.to_csv("data/processed/comps_table.csv", index=False)
    print(df)