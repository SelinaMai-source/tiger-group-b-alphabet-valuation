# PE估值模型包
"""
PE估值模型包

包含以下模块：
- pe_visual: PE估值仪表板
- pe_calc: PE计算工具
- pe_data: PE数据获取
- comp_fetcher: 可比公司数据获取
- prediction_tools: 预测工具
"""

from .pe_visual import create_pe_valuation_dashboard
from .pe_calc import get_current_price, calculate_forward_pe

__all__ = [
    'create_pe_valuation_dashboard',
    'get_current_price', 
    'calculate_forward_pe'
] 