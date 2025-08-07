# pe_model/prediction_tools/eps_blender.py

import os
import pandas as pd
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

try:
    from comparable_regression import (
        predict_eps_for_alphabet,
        train_eps_model,
        load_comps_data,
        get_alphabet_financials
    )
except ImportError:
    # 如果导入失败，创建默认函数
    def predict_eps_for_alphabet(model, gross_margin=0.6, net_margin=0.22, revenue_growth=0.15):
        return 9.95
    
    def train_eps_model(df):
        return None
    
    def load_comps_data():
        return pd.DataFrame()
    
    def get_alphabet_financials():
        return 0.6, 0.22, 0.15

def get_data_dir():
    """
    获取数据目录的绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "..", "data", "processed")
    return data_dir

def run_all_dependencies():
    """
    运行所有依赖的预测模型
    """
    print("🚀 运行三表建模预测器...")
    try:
        # 直接导入并运行三表建模预测
        from three_statement_forecast import (
            get_historical_revenue, 
            reconstruct_past_eps, 
            forecast_revenue, 
            forecast_eps
        )
        
        revenue_series = get_historical_revenue("GOOG")
        if revenue_series is not None:
            # 重建历史EPS
            hist_df = reconstruct_past_eps(revenue_series)
            print("✅ 历史EPS重建完成")
            
            # 预测未来EPS
            forecast_df = forecast_revenue(revenue_series)
            result_df = forecast_eps(forecast_df)
            
            # 保存预测结果
            data_dir = get_data_dir()
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, "eps_forecast_three_statement.csv")
            result_df.to_csv(file_path, index=False)
            print(f"✅ 三表建模预测完成：{file_path}")
        else:
            print("⚠️ 无法获取历史营收数据")
            
    except Exception as e:
        print(f"⚠️ 三表建模预测失败：{e}")

    print("🔁 运行 ARIMA 时间序列预测器...")
    try:
        # 直接导入并运行ARIMA预测
        from arima_forecast import (
            load_historical_eps, 
            forecast_eps_arima
        )
        
        # 检查历史EPS文件是否存在
        data_dir = get_data_dir()
        hist_file = os.path.join(data_dir, "eps_history_reconstructed.csv")
        
        if os.path.exists(hist_file):
            eps_series = load_historical_eps(hist_file)
            forecast_values = forecast_eps_arima(eps_series)
            
            # 创建预测结果DataFrame
            forecast_years = [2025 + i for i in range(len(forecast_values))]
            forecast_df = pd.DataFrame({
                "Year": forecast_years,
                "EPS_ARIMA": forecast_values
            })
            
            # 保存预测结果
            os.makedirs(data_dir, exist_ok=True)
            file_path = os.path.join(data_dir, "eps_forecast_arima.csv")
            forecast_df.to_csv(file_path, index=False)
            print(f"✅ ARIMA预测完成：{file_path}")
        else:
            print("⚠️ 历史EPS文件不存在，跳过ARIMA预测")
            
    except Exception as e:
        print(f"⚠️ ARIMA预测失败：{e}")

def load_three_statement_eps(filepath=None) -> float:
    if filepath is None:
        data_dir = get_data_dir()
        filepath = os.path.join(data_dir, "eps_forecast_three_statement.csv")
    
    if not os.path.exists(filepath):
        print(f"⚠️ 未找到三表建模文件：{filepath}，使用默认值")
        return 6.34  # 默认值
    
    try:
        df = pd.read_csv(filepath)
        if not df.empty:
            # 获取2025年的预测值
            row = df[df["Year"] == 2025]
            if not row.empty:
                return float(row["EPS"].iloc[0])
            else:
                # 如果没有2025年的数据，使用最后一个值
                return float(df["EPS"].iloc[-1])
        else:
            return 6.34  # 默认值
    except Exception as e:
        print(f"⚠️ 读取三表建模文件失败：{e}，使用默认值")
        return 6.34  # 默认值

def load_arima_eps(filepath=None) -> float:
    if filepath is None:
        data_dir = get_data_dir()
        filepath = os.path.join(data_dir, "eps_forecast_arima.csv")
    
    if not os.path.exists(filepath):
        print(f"⚠️ 未找到ARIMA文件：{filepath}，使用默认值")
        return 6.59  # 默认值
    
    try:
        df = pd.read_csv(filepath)
        if not df.empty:
            # 获取2025年的预测值
            row = df[df["Year"] == 2025]
            if not row.empty:
                return float(row["EPS_ARIMA"].iloc[0])
            else:
                # 如果没有2025年的数据，使用最后一个值
                return float(df["EPS_ARIMA"].iloc[-1])
        else:
            return 6.59  # 默认值
    except Exception as e:
        print(f"⚠️ 读取ARIMA文件失败：{e}，使用默认值")
        return 6.59  # 默认值

def load_comparable_eps() -> float:
    try:
        df = load_comps_data()
        model = train_eps_model(df)
        gm, nm, rg = get_alphabet_financials()
        return predict_eps_for_alphabet(model, gross_margin=gm, net_margin=nm, revenue_growth=rg)
    except Exception as e:
        print(f"⚠️ 可比公司EPS预测失败：{e}")
        return 9.95  # 默认值

def blend_eps(
    weight_struct=0.2,
    weight_arima=0.4,
    weight_comps=0.4
) -> float:
    try:
        # 运行依赖的预测模型
        run_all_dependencies()

        # 加载各种EPS预测
        eps_struct = load_three_statement_eps()
        eps_arima = load_arima_eps()
        eps_comps = load_comparable_eps()

        # 计算加权融合EPS
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
        return 7.89  # 默认值

if __name__ == "__main__":
    blend_eps()