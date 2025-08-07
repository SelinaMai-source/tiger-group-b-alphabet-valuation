import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import yfinance as yf

def load_comps_data(filepath="data/processed/comps_table.csv") -> pd.DataFrame:
    """
    加载可比公司数据，并清洗缺失值
    """
    df = pd.read_csv(filepath)
    df = df.dropna(subset=["EPS", "Gross Margin", "Net Margin", "Revenue YoY"])
    return df

def train_eps_model(df: pd.DataFrame) -> LinearRegression:
    """
    用 comps 数据训练 EPS 回归预测器
    """
    X = df[["Gross Margin", "Net Margin", "Revenue YoY"]]
    y = df["EPS"]
    model = LinearRegression()
    model.fit(X, y)
    return model

def get_alphabet_financials() -> tuple:
    """
    自动拉取 Alphabet 最新财务数据，计算毛利率、净利率、营收增长率
    """
    t = yf.Ticker("GOOG")
    info = t.info

    # 收入、利润数据
    revenue = info.get("totalRevenue")
    gross_profit = info.get("grossProfits")
    net_income = info.get("netIncomeToCommon")

    # 利润率计算
    gross_margin = gross_profit / revenue if gross_profit and revenue else None
    net_margin = net_income / revenue if net_income and revenue else None

    # 营收增长率
    financials = t.financials
    revenue_series = financials.loc["Total Revenue"]
    revenue_series = revenue_series.sort_index()

    if len(revenue_series) >= 2:
        rev_growth = (revenue_series.iloc[0] - revenue_series.iloc[1]) / revenue_series.iloc[1]
    else:
        rev_growth = None

    return gross_margin, net_margin, rev_growth

def predict_eps_for_alphabet(model: LinearRegression, gross_margin, net_margin, revenue_growth) -> float:
    """
    输入 Alphabet 的财务指标，预测其 EPS
    """
    if None in [gross_margin, net_margin, revenue_growth]:
        raise ValueError("Missing one or more input variables for prediction.")
    
    X_pred = np.array([[gross_margin, net_margin, revenue_growth]])
    eps_pred = model.predict(X_pred)
    return eps_pred[0]

if __name__ == "__main__":
    # Step 1: 加载可比公司数据并训练模型
    df = load_comps_data()
    model = train_eps_model(df)

    # Step 2: 抓取 Alphabet 最新指标
    gm, nm, rg = get_alphabet_financials()
    print(f"🔍 Alphabet 当前指标：Gross Margin={gm:.2%}, Net Margin={nm:.2%}, Revenue YoY={rg:.2%}")

    # Step 3: 用回归模型预测 EPS
    eps_pred = predict_eps_for_alphabet(model, gross_margin=gm, net_margin=nm, revenue_growth=rg)
    print(f"📈 可比公司回归模型预测 Alphabet 的 EPS：{eps_pred:.2f}")

# pe_model/prediction_tools/comparable_regression.py

import pandas as pd
import os

def load_comparable_eps(filepath="data/processed/eps_forecast_comparables.csv") -> float:
    """
    加载 Comparable 公司回归预测 EPS（用于可视化）
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Comparable EPS 文件未找到：{filepath}")

    df = pd.read_csv(filepath)
    if "EPS" not in df.columns:
        raise ValueError("❌ 文件缺少 'EPS' 列")

    # 默认使用最新预测年份的 EPS
    latest_eps = df.sort_values("Year").iloc[-1]["EPS"]
    return latest_eps