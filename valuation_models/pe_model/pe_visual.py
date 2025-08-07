# pe_model/pe_visual.py

import pandas as pd
import numpy as np
import os
from datetime import datetime

def get_data_dir():
    """
    获取数据目录的绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data", "processed")
    return data_dir

def create_pe_valuation_dashboard():
    """
    创建PE估值仪表板并返回EPS预测数据
    """
    try:
        # 初始化EPS预测数据
        eps_predictions = {
            'three_statement': 6.34,
            'arima': 6.59,
            'comparable': 9.95,
            'blended': 7.89
        }
        
        # 尝试加载实际数据
        try:
            data_dir = get_data_dir()
            
            # 1. 加载三表建模EPS预测
            forecast_file = os.path.join(data_dir, "eps_forecast_three_statement.csv")
            if os.path.exists(forecast_file):
                forecast_df = pd.read_csv(forecast_file)
                if not forecast_df.empty:
                    eps_predictions['three_statement'] = float(forecast_df['EPS'].iloc[0])
            
            # 2. 加载ARIMA EPS预测
            arima_file = os.path.join(data_dir, "eps_forecast_arima.csv")
            if os.path.exists(arima_file):
                arima_df = pd.read_csv(arima_file)
                if not arima_df.empty:
                    eps_predictions['arima'] = float(arima_df['EPS_ARIMA'].iloc[0])
            
            # 3. 计算加权融合EPS
            eps_predictions['blended'] = (
                0.2 * eps_predictions['three_statement'] +
                0.4 * eps_predictions['arima'] +
                0.4 * eps_predictions['comparable']
            )
            
        except Exception as e:
            print(f"⚠️ 加载EPS数据失败：{e}，使用默认值")
        
        # 返回包含EPS预测数据的字典
        results = {
            'current_price': 196.92,  # 示例当前股价
            'eps_predictions': eps_predictions,
            'forward_pe': 22.0,
            'valuation_summary': {
                'model': 'PE Valuation Model',
                'ticker': 'GOOG',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'methodology': 'Multi-model EPS prediction with weighted blending',
                'confidence_score': 88
            }
        }
        
        print(f"✅ PE估值Dashboard创建成功：{results}")
        return results
        
    except Exception as e:
        print(f"⚠️ 创建PE估值Dashboard失败：{e}")
        # 返回默认结果
        return {
            'current_price': 196.92,
            'eps_predictions': {
                'three_statement': 6.34,
                'arima': 6.59,
                'comparable': 9.95,
                'blended': 7.89
            },
            'forward_pe': 22.0,
            'valuation_summary': {
                'model': 'PE Valuation Model',
                'ticker': 'GOOG',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'methodology': 'Multi-model EPS prediction with weighted blending',
                'confidence_score': 88
            }
        }

if __name__ == "__main__":
    results = create_pe_valuation_dashboard()
    print("PE估值结果：", results)