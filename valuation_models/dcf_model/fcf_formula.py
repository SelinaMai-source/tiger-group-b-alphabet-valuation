import requests
import pandas as pd

API_KEY = "gBJGrqoVRZ40Dax8mPohoP76xa5OOUhK"
TICKER = "GOOG"

# -------------------------------
# ✅ 最新一期 FCF 构成计算（TTM）
# -------------------------------
def get_fcf_components(ticker: str = TICKER) -> dict:
    try:
        # 📄 获取 income statement（TTM）
        income_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=1&apikey={API_KEY}"
        income_data = requests.get(income_url).json()[0]
        ebit = income_data["operatingIncome"]

        # ✅ 计算有效税率（Effective Tax Rate）
        income_before_tax = income_data.get("incomeBeforeTax", None)
        income_tax_expense = income_data.get("incomeTaxExpense", None)
        if income_before_tax and income_tax_expense and income_before_tax != 0:
            effective_tax_rate = abs(income_tax_expense / income_before_tax)
        else:
            effective_tax_rate = 0.21  # fallback 默认值

        # 📄 获取 cash flow statement（TTM）
        cashflow_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?limit=1&apikey={API_KEY}"
        cashflow_data = requests.get(cashflow_url).json()[0]
        da = cashflow_data["depreciationAndAmortization"]
        capex = cashflow_data["capitalExpenditure"]

        # 📄 获取 balance sheet（两期对比做营运资本变动）
        bs_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?limit=2&apikey={API_KEY}"
        bs_data = requests.get(bs_url).json()
        wc1 = bs_data[0]["totalCurrentAssets"] - bs_data[0]["totalCurrentLiabilities"]
        wc2 = bs_data[1]["totalCurrentAssets"] - bs_data[1]["totalCurrentLiabilities"]
        delta_wc = wc1 - wc2

        return {
            "EBIT": ebit,
            "Tax Rate": effective_tax_rate,
            "Depreciation & Amort.": da,
            "CAPEX": capex,
            "Δ Working Capital": delta_wc
        }

    except Exception as e:
        print(f"❌ Error fetching FCF components: {e}")
        return None

def calculate_fcf(components: dict) -> float:
    try:
        fcf = (
            components["EBIT"] * (1 - components["Tax Rate"])
            + components["Depreciation & Amort."]
            - abs(components["CAPEX"])
            - components["Δ Working Capital"]
        )
        return fcf
    except:
        return None


# -------------------------------
# ✅ 获取历史 FCF（过去 N 年）
# -------------------------------
def get_historical_fcf(ticker: str = TICKER, years: int = 5) -> pd.Series:
    """
    获取过去 N 年的年度 FCF（年报）
    返回 pd.Series，index 为年份，值为对应的 FCF
    """
    try:
        income_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit={years}&apikey={API_KEY}"
        cashflow_url = f"https://financialmodelingprep.com/api/v3/cash-flow-statement/{ticker}?limit={years}&apikey={API_KEY}"
        bs_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?limit={years + 1}&apikey={API_KEY}"

        income_data = requests.get(income_url).json()
        cashflow_data = requests.get(cashflow_url).json()
        bs_data = requests.get(bs_url).json()

        # ✅ 检查是否数据足够
        min_len = min(len(income_data), len(cashflow_data), len(bs_data) - 1)
        if min_len == 0:
            raise ValueError("Insufficient data from API")

        fcf_dict = {}

        for i in range(min_len):
            year = int(income_data[i]["calendarYear"])

            ebit = income_data[i]["operatingIncome"]
            income_before_tax = income_data[i].get("incomeBeforeTax", None)
            income_tax_expense = income_data[i].get("incomeTaxExpense", None)
            tax_rate = abs(income_tax_expense / income_before_tax) if income_before_tax and income_tax_expense and income_before_tax != 0 else 0.21

            da = cashflow_data[i]["depreciationAndAmortization"]
            capex = cashflow_data[i]["capitalExpenditure"]

            wc_now = bs_data[i]["totalCurrentAssets"] - bs_data[i]["totalCurrentLiabilities"]
            wc_prev = bs_data[i + 1]["totalCurrentAssets"] - bs_data[i + 1]["totalCurrentLiabilities"]
            delta_wc = wc_now - wc_prev

            fcf = ebit * (1 - tax_rate) + da - abs(capex) - delta_wc
            fcf_dict[year] = fcf

        return pd.Series(fcf_dict).sort_index()

    except Exception as e:
        print(f"❌ Error fetching historical FCF: {e}")
        return pd.Series()
        

# -------------------------------
# 🧪 测试运行
# -------------------------------
if __name__ == "__main__":
    comps = get_fcf_components()
    if comps:
        fcf = calculate_fcf(comps)
        print("📊 Alphabet 最新一期 FCF 构成：\n")
        for k, v in comps.items():
            print(f"  {k:<25}: ${v:,.2f}")
        print(f"\n✅ 计算得出 TTM 自由现金流（FCF）：${fcf:,.2f}")

    print("\n📈 获取历史 FCF：")
    hist = get_historical_fcf()
    print(hist)