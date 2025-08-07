# pe_model/prediction_tools/eps_blender.py

import os
import pandas as pd
from prediction_tools.comparable_regression import (
    predict_eps_for_alphabet,
    train_eps_model,
    load_comps_data,
    get_alphabet_financials
)

def run_all_dependencies():
    print("🚀 运行三表建模预测器...")
    os.system("python prediction_tools/three_statement_forecast.py")

    print("🔁 运行 ARIMA 时间序列预测器...")
    os.system("python prediction_tools/arima_forecast.py")

def load_three_statement_eps(filepath="data/processed/eps_forecast_three_statement.csv") -> float:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 未找到文件：{filepath}")
    df = pd.read_csv(filepath)
    return df["EPS"].iloc[0]

def load_arima_eps(filepath="data/processed/eps_forecast_arima.csv") -> float:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 未找到文件：{filepath}")
    df = pd.read_csv(filepath)
    return df["EPS_ARIMA"].iloc[0]

def load_comparable_eps() -> float:
    df = load_comps_data()
    model = train_eps_model(df)
    gm, nm, rg = get_alphabet_financials()
    return predict_eps_for_alphabet(model, gross_margin=gm, net_margin=nm, revenue_growth=rg)

def blend_eps(
    weight_struct=0.2,
    weight_arima=0.4,
    weight_comps=0.4
) -> float:
    run_all_dependencies()

    eps_struct = load_three_statement_eps()
    eps_arima = load_arima_eps()
    eps_comps = load_comparable_eps()

    eps_final = (
        weight_struct * eps_struct +
        weight_arima * eps_arima +
        weight_comps * eps_comps
    )

    print(f"\n📊 三表建模 EPS：{eps_struct:.2f}")
    print(f"🧠 ARIMA EPS：{eps_arima:.2f}")
    print(f"🤝 可比公司回归 EPS：{eps_comps:.2f}")
    print(f"\n✅ 加权融合 EPS_Final（结构0.2 + ARIMA0.4 + Comps0.4）：{eps_final:.2f}")

    return eps_final

if __name__ == "__main__":
    blend_eps()