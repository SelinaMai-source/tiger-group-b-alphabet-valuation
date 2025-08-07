# 预测工具包
"""
预测工具包

包含以下模块：
- eps_blender: EPS融合工具
- arima_forecast: ARIMA预测
- three_statement_forecast: 三表建模预测
- comparable_regression: 可比公司回归分析
"""

from .eps_blender import blend_eps
from .arima_forecast import forecast_eps_arima
from .three_statement_forecast import forecast_eps_three_statement
from .comparable_regression import predict_eps_for_alphabet

__all__ = [
    'blend_eps',
    'forecast_eps_arima',
    'forecast_eps_three_statement', 
    'predict_eps_for_alphabet'
] 