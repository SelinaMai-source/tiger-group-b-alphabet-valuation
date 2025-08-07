import requests

API_KEY = "gBJGrqoVRZ40Dax8mPohoP76xa5OOUhK"
TICKER = "GOOG"

def get_wacc_components(ticker: str = TICKER) -> dict:
    try:
        # 股票市值（E）和 Beta
        profile_url = f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={API_KEY}"
        profile = requests.get(profile_url).json()[0]
        market_cap = profile["mktCap"]
        beta = profile["beta"]

        # 总负债（D）
        balance_url = f"https://financialmodelingprep.com/api/v3/balance-sheet-statement/{ticker}?limit=1&apikey={API_KEY}"
        balance_data = requests.get(balance_url).json()[0]
        total_debt = balance_data["totalDebt"]

        # 利息支出（估算 Rd）
        income_url = f"https://financialmodelingprep.com/api/v3/income-statement/{ticker}?limit=1&apikey={API_KEY}"
        income_data = requests.get(income_url).json()[0]
        interest_expense = income_data.get("interestExpense", 0)

        # 税率（Tc）——用有效税率
        tax_rate = income_data["incomeTaxExpense"] / income_data["incomeBeforeTax"]

        # Rd = 利息支出 / 总负债
        cost_of_debt = abs(interest_expense) / total_debt if total_debt != 0 else 0

        # Re = Rf + beta × (Rm - Rf)
        risk_free_rate = 0.042
        market_risk_premium = 0.055
        cost_of_equity = risk_free_rate + beta * market_risk_premium

        # WACC = E/(E+D)×Re + D/(E+D)×Rd×(1 - Tc)
        total_value = market_cap + total_debt
        wacc = (
            (market_cap / total_value) * cost_of_equity
            + (total_debt / total_value) * cost_of_debt * (1 - tax_rate)
        )

        return {
            "Equity (E)": market_cap,
            "Debt (D)": total_debt,
            "Beta": beta,
            "Tax Rate (Tc)": tax_rate,
            "Cost of Equity (Re)": cost_of_equity,
            "Cost of Debt (Rd)": cost_of_debt,
            "WACC": wacc
        }

    except Exception as e:
        print(f"❌ Error calculating WACC: {e}")
        return None

def get_wacc(ticker: str = TICKER) -> float:
        components = get_wacc_components(ticker)
        return components["WACC"] if components else None


if __name__ == "__main__":
    result = get_wacc_components()
    if result:
        print("📊 Alphabet 最新一期 WACC 构成：")
        for k, v in result.items():
            print(f"  {k:<25}: {v:,.4f}" if isinstance(v, float) else f"  {k:<25}: {v:,}")