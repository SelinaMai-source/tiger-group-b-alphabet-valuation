# pe_model/prediction_tools/eps_blender.py

import os
import pandas as pd
from prediction_tools.comparable_regression import (
    predict_eps_for_alphabet,
    train_eps_model,
    load_comps_data,
    get_alphabet_financials
)

def get_data_dir():
    """
    获取数据目录的绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data", "processed")
    return data_dir

def run_all_dependencies():
    print("🚀 运行三表建模预测器...")
    try:
        os.system("python prediction_tools/three_statement_forecast.py")
    except Exception as e:
        print(f"⚠️ 三表建模预测失败：{e}")

    print("🔁 运行 ARIMA 时间序列预测器...")
    try:
        os.system("python prediction_tools/arima_forecast.py")
    except Exception as e:
        print(f"⚠️ ARIMA预测失败：{e}")

def load_three_statement_eps(filepath=None) -> float:
    if filepath is None:
        data_dir = get_data_dir()
        filepath = os.path.join(data_dir, "eps_forecast_three_statement.csv")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 未找到文件：{filepath}")
    df = pd.read_csv(filepath)
    return df["EPS"].iloc[0]

def load_arima_eps(filepath=None) -> float:
    if filepath is None:
        data_dir = get_data_dir()
        filepath = os.path.join(data_dir, "eps_forecast_arima.csv")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ 未找到文件：{filepath}")
    df = pd.read_csv(filepath)
    return df["EPS_ARIMA"].iloc[0]

def load_comparable_eps() -> float:
    try:
        df = load_comps_data()
        model = train_eps_model(df)
        gm, nm, rg = get_alphabet_financials()
        return predict_eps_for_alphabet(model, gross_margin=gm, net_margin=nm, revenue_growth=rg)
    except Exception as e:
        print(f"⚠️ 可比公司EPS预测失败：{e}")
        return 6.0  # 默认值

def blend_eps(
    weight_struct=0.2,
    weight_arima=0.4,
    weight_comps=0.4
) -> float:
    try:
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
    except Exception as e:
        print(f"⚠️ EPS融合失败：{e}")
        return 6.0  # 默认值

if __name__ == "__main__":
    blend_eps()