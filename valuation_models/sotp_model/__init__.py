# sotp_model/__init__.py

"""
SOTP (Sum of the Parts) 估值模型

该模型将Alphabet的业务分为三个主要部分：
1. Google Services（主营搜索广告）：使用PE估值法
2. Google Cloud：使用EV估值法  
3. Other Bets（其他创新项目）：使用Real Option估值法

最终目标价格 = (Services Valuation + Cloud Valuation + Other Bets Valuation - Net Debt) / Shares Outstanding
"""

from .sotp_calc import calculate_sotp_valuation
from .sotp_data import get_sotp_components
from .sotp_visual import create_sotp_dashboard

__all__ = [
    'calculate_sotp_valuation',
    'get_sotp_components', 
    'create_sotp_dashboard'
]
