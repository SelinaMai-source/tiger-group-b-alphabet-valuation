# pe_model/pe_data.py
import yfinance as yf
import pandas as pd
from datetime import datetime

def get_alphabet_financial_data() -> pd.DataFrame:
    """
    拉取 Alphabet（GOOG）的核心财务数据，用于估值分析。
    包括：当前股价、市值、TTM每股收益、净利润、流通股数等。
    """
    ticker = yf.Ticker("GOOG")

    # 获取基本信息
    info = ticker.info
    price = info.get("currentPrice")  # 最新股价
    market_cap = info.get("marketCap")  # 当前市值
    eps_ttm = info.get("trailingEps")  # 每股收益（过去12个月）

    # 用于 DCF 和历史盈利增长趋势的财报
    income_stmt = ticker.financials.T  # 营收、净利润等
    balance_sheet = ticker.balance_sheet.T  # 用于计算股东权益、负债比率等
    cashflow_stmt = ticker.cashflow.T  # 自由现金流，供 DCF 使用

    # 自动推算流通股数和净利润（提高稳定性）
    shares_outstanding = market_cap / eps_ttm if eps_ttm and market_cap else None
    net_income_ttm = eps_ttm * shares_outstanding if shares_outstanding else None

    # 构建 DataFrame 输出
    data = {
        "Date": datetime.today().strftime("%Y-%m-%d"),
        "Company": "Alphabet",
        "Price": price,
        "MarketCap": market_cap,
        "EPS_TTM": eps_ttm,
        "NetIncome_TTM": net_income_ttm,
        "SharesOutstanding": shares_outstanding
    }

    df = pd.DataFrame([data])
    return df, income_stmt, balance_sheet, cashflow_stmt

if __name__ == "__main__":
    df, income, bs, cf = get_alphabet_financial_data()

    # 保存核心数据
    df.to_csv("data/processed/pe_data_alphabet.csv", index=False)

    # 可选：保存完整报表供 DCF 使用
    income.to_csv("data/processed/income_statement.csv")
    bs.to_csv("data/processed/balance_sheet.csv")
    cf.to_csv("data/processed/cashflow_statement.csv")

    print("已成功保存 Alphabet 财务数据")