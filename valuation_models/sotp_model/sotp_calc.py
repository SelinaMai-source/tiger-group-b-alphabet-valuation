# sotp_model/sotp_calc.py

import numpy as np
import pandas as pd
from .sotp_data import get_sotp_components, get_industry_multiples

def calculate_services_valuation(services_net_income, services_pe_multiple):
    """
    计算Google Services估值（PE估值法）
    
    Args:
        services_net_income (float): Services业务净收入
        services_pe_multiple (float): Services业务PE倍数
    
    Returns:
        float: Services业务估值
    """
    return services_net_income * services_pe_multiple

def calculate_cloud_valuation(cloud_ebitda, cloud_ev_ebitda_multiple, total_debt, cash):
    """
    计算Google Cloud估值（EV估值法）
    
    Args:
        cloud_ebitda (float): Cloud业务EBITDA
        cloud_ev_ebitda_multiple (float): Cloud业务EV/EBITDA倍数
        total_debt (float): 总债务
        cash (float): 现金
    
    Returns:
        float: Cloud业务估值
    """
    # 计算Cloud业务的EV
    cloud_ev = cloud_ebitda * cloud_ev_ebitda_multiple
    
    # 按比例分配净债务（基于收入比例）
    cloud_debt_ratio = 0.10  # Cloud约占10%的业务
    cloud_net_debt = (total_debt - cash) * cloud_debt_ratio
    
    # Cloud业务估值 = EV - 净债务
    cloud_valuation = cloud_ev - cloud_net_debt
    
    return max(cloud_valuation, 0)  # 确保估值不为负

def calculate_other_bets_valuation(other_bets_option_value, success_probability):
    """
    计算Other Bets估值（Real Option估值法）
    
    Args:
        other_bets_option_value (float): Other Bets期权价值
        success_probability (float): 成功概率
    
    Returns:
        float: Other Bets业务估值
    """
    # 简化的Real Option估值：期权价值 × 成功概率
    return other_bets_option_value * success_probability

def calculate_sotp_valuation(ticker="GOOG"):
    """
    计算SOTP估值
    
    Args:
        ticker (str): 股票代码
    
    Returns:
        dict: 包含各个业务线估值和最终目标价格的字典
    """
    # 获取数据
    data = get_sotp_components(ticker)
    multiples = get_industry_multiples()
    
    # 1. 计算Google Services估值（PE估值法）
    services_valuation = calculate_services_valuation(
        data["services_net_income"],
        multiples["services_pe_multiple"]
    )
    
    # 2. 计算Google Cloud估值（EV估值法）
    cloud_valuation = calculate_cloud_valuation(
        data["cloud_ebitda"],
        multiples["cloud_ev_ebitda_multiple"],
        data["total_debt"],
        data["cash"]
    )
    
    # 3. 计算Other Bets估值（Real Option估值法）
    other_bets_valuation = calculate_other_bets_valuation(
        multiples["other_bets_option_value"],
        multiples["other_bets_success_probability"]
    )
    
    # 4. 计算净债务
    net_debt = data["total_debt"] - data["cash"]
    
    # 5. 计算总估值
    total_valuation = services_valuation + cloud_valuation + other_bets_valuation - net_debt
    
    # 6. 计算目标股价
    target_price = total_valuation / data["shares_outstanding"]
    
    # 7. 计算各部分占比
    total_business_value = services_valuation + cloud_valuation + other_bets_valuation
    
    return {
        # 基础数据
        "current_price": data["current_price"],
        "shares_outstanding": data["shares_outstanding"],
        "net_debt": net_debt,
        
        # 各业务线估值
        "services_valuation": services_valuation,
        "cloud_valuation": cloud_valuation,
        "other_bets_valuation": other_bets_valuation,
        
        # 总估值
        "total_business_value": total_business_value,
        "total_valuation": total_valuation,
        "target_price": target_price,
        
        # 占比分析
        "services_percentage": (services_valuation / total_business_value) * 100 if total_business_value > 0 else 0,
        "cloud_percentage": (cloud_valuation / total_business_value) * 100 if total_business_value > 0 else 0,
        "other_bets_percentage": (other_bets_valuation / total_business_value) * 100 if total_business_value > 0 else 0,
        
        # 估值倍数
        "services_pe_multiple": multiples["services_pe_multiple"],
        "cloud_ev_ebitda_multiple": multiples["cloud_ev_ebitda_multiple"],
        "other_bets_success_probability": multiples["other_bets_success_probability"],
        
        # 财务数据
        "services_net_income": data["services_net_income"],
        "cloud_ebitda": data["cloud_ebitda"],
        "other_bets_option_value": multiples["other_bets_option_value"]
    }

def get_sotp_valuation_summary(ticker="GOOG"):
    """
    获取SOTP估值摘要
    
    Args:
        ticker (str): 股票代码
    
    Returns:
        dict: 包含估值摘要的字典
    """
    results = calculate_sotp_valuation(ticker)
    
    summary = {
        "当前股价": f"${results['current_price']:.2f}",
        "目标股价": f"${results['target_price']:.2f}",
        "估值溢价": f"{((results['target_price'] / results['current_price'] - 1) * 100):.1f}%",
        
        "Google Services估值": f"${results['services_valuation']/1e9:.1f}B",
        "Google Cloud估值": f"${results['cloud_valuation']/1e9:.1f}B", 
        "Other Bets估值": f"${results['other_bets_valuation']/1e9:.1f}B",
        "净债务": f"${results['net_debt']/1e9:.1f}B",
        
        "Services占比": f"{results['services_percentage']:.1f}%",
        "Cloud占比": f"{results['cloud_percentage']:.1f}%",
        "Other Bets占比": f"{results['other_bets_percentage']:.1f}%"
    }
    
    return summary

if __name__ == "__main__":
    print("🔍 正在计算SOTP估值...")
    results = calculate_sotp_valuation()
    
    print(f"\n📊 SOTP估值结果：")
    print(f"当前股价：${results['current_price']:.2f}")
    print(f"目标股价：${results['target_price']:.2f}")
    print(f"估值溢价：{((results['target_price'] / results['current_price'] - 1) * 100):.1f}%")
    
    print(f"\n🏢 各业务线估值：")
    print(f"Google Services：${results['services_valuation']/1e9:.1f}B ({results['services_percentage']:.1f}%)")
    print(f"Google Cloud：${results['cloud_valuation']/1e9:.1f}B ({results['cloud_percentage']:.1f}%)")
    print(f"Other Bets：${results['other_bets_valuation']/1e9:.1f}B ({results['other_bets_percentage']:.1f}%)")
    
    print(f"\n💰 总估值：${results['total_valuation']/1e9:.1f}B")
    print(f"净债务：${results['net_debt']/1e9:.1f}B")
