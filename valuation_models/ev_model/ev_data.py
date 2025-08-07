import yfinance as yf
import pandas as pd

def get_alphabet_ev_components(ticker="GOOG") -> dict:
    """
    抓取 Alphabet 的估值模型核心组成：
    市值、负债、现金、EBITDA、FCF 等
    """

    t = yf.Ticker(ticker)
    info = t.info

    # 🎯 市值/负债/现金
    market_cap = info.get("marketCap")
    total_debt = info.get("totalDebt", 0)
    cash = info.get("totalCash", 0)
    enterprise_value = market_cap + total_debt - cash if market_cap else None

    # 🎯 财报：income statement
    financials = t.financials
    try:
        net_income = financials.loc["Net Income"].iloc[0]
    except:
        net_income = info.get("netIncomeToCommon")

    try:
        taxes = financials.loc["Income Tax Expense"].iloc[0]
    except:
        taxes = 0

    try:
        interest = financials.loc["Interest Expense"].iloc[0]
    except:
        interest = 0

    try:
        depreciation = financials.loc["Depreciation"].iloc[0]
    except:
        depreciation = info.get("depreciation", 0)

    try:
        amortization = financials.loc["Amortization"].iloc[0]
    except:
        amortization = 0

    d_and_a = depreciation + amortization
    ebitda_ttm = net_income + taxes + interest + d_and_a

    # 🎯 自由现金流（FCF）获取
    try:
        fcf = info.get("freeCashflow")
    except:
        fcf = None

    return {
        "MarketCap": market_cap,
        "TotalDebt": total_debt,
        "Cash": cash,
        "EnterpriseValue": enterprise_value,
        "NetIncome": net_income,
        "Taxes": taxes,
        "Interest": interest,
        "Depreciation": depreciation,
        "Amortization": amortization,
        "D&A": d_and_a,
        "EBITDA_TTM": ebitda_ttm,
        "FCF_TTM": fcf
    }

if __name__ == "__main__":
    data = get_alphabet_ev_components()
    df = pd.DataFrame([data])
    print("📊 Alphabet EV 模型组成数据：")
    print(df.T)