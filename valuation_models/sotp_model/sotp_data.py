# sotp_model/sotp_data.py

import yfinance as yf
import pandas as pd
import numpy as np
import os
import sys

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

def get_sotp_components(ticker="GOOG"):
    """
    获取SOTP模型所需的各个业务线数据
    
    Returns:
        dict: 包含各个业务线财务数据的字典
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # 获取财务报表
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        
        # 基础财务数据
        market_cap = info.get("marketCap", 0)
        total_debt = info.get("totalDebt", 0)
        cash = info.get("totalCash", 0)
        shares_outstanding = info.get("sharesOutstanding", 13_000_000_000)
        
        # 获取净收入数据
        try:
            net_income = financials.loc["Net Income"].iloc[0]
        except:
            net_income = info.get("netIncomeToCommon", 0)
        
        # 估算各个业务线的收入分配（基于公开数据）
        # Google Services约占85%，Google Cloud约占10%，Other Bets约占5%
        total_revenue = info.get("totalRevenue", 0)
        
        # 业务线收入分配
        services_revenue = total_revenue * 0.85
        cloud_revenue = total_revenue * 0.10
        other_bets_revenue = total_revenue * 0.05
        
        # 业务线净收入分配（基于利润率估算）
        services_net_income = net_income * 0.90  # Services利润率较高
        cloud_net_income = net_income * 0.08     # Cloud还在成长期
        other_bets_net_income = net_income * 0.02  # Other Bets还在投资期
        
        # 获取EBITDA数据
        try:
            ebitda = info.get("ebitda", 0)
        except:
            ebitda = net_income * 1.3  # 估算EBITDA
        
        # Cloud业务的EBITDA
        cloud_ebitda = ebitda * 0.08  # Cloud约占8%的EBITDA
        
        return {
            # 基础数据
            "market_cap": market_cap,
            "total_debt": total_debt,
            "cash": cash,
            "shares_outstanding": shares_outstanding,
            "total_revenue": total_revenue,
            "net_income": net_income,
            "ebitda": ebitda,
            
            # Google Services数据
            "services_revenue": services_revenue,
            "services_net_income": services_net_income,
            
            # Google Cloud数据
            "cloud_revenue": cloud_revenue,
            "cloud_net_income": cloud_net_income,
            "cloud_ebitda": cloud_ebitda,
            
            # Other Bets数据
            "other_bets_revenue": other_bets_revenue,
            "other_bets_net_income": other_bets_net_income,
            
            # 其他财务指标
            "current_price": info.get("currentPrice", 196.92),
            "pe_ratio": info.get("trailingPE", 25.0)
        }
        
    except Exception as e:
        print(f"⚠️ 获取SOTP数据失败：{e}")
        # 返回默认数据
        return {
            "market_cap": 2_500_000_000_000,
            "total_debt": 15_000_000_000,
            "cash": 120_000_000_000,
            "shares_outstanding": 13_000_000_000,
            "total_revenue": 300_000_000_000,
            "net_income": 80_000_000_000,
            "ebitda": 100_000_000_000,
            "services_revenue": 255_000_000_000,
            "services_net_income": 72_000_000_000,
            "cloud_revenue": 30_000_000_000,
            "cloud_net_income": 6_400_000_000,
            "cloud_ebitda": 8_000_000_000,
            "other_bets_revenue": 15_000_000_000,
            "other_bets_net_income": 1_600_000_000,
            "current_price": 196.92,
            "pe_ratio": 25.0
        }

def get_industry_multiples():
    """
    获取行业估值倍数
    
    Returns:
        dict: 包含各个业务线行业倍数的字典
    """
    return {
        # Google Services PE倍数（基于科技公司平均PE，调整为更保守的倍数）
        "services_pe_multiple": 20.0,  # 从25.0调整为20.0
        
        # Google Cloud EV/EBITDA倍数（基于云计算公司平均倍数）
        "cloud_ev_ebitda_multiple": 12.0,  # 从15.0调整为12.0
        
        # Other Bets Real Option估值参数
        "other_bets_option_value": 30_000_000_000,  # 从50B调整为30B
        "other_bets_success_probability": 0.25,     # 从30%调整为25%
    }

if __name__ == "__main__":
    data = get_sotp_components()
    print("📊 SOTP模型数据：")
    for key, value in data.items():
        if isinstance(value, (int, float)) and value > 1e6:
            print(f"{key}: ${value/1e9:.2f}B")
        else:
            print(f"{key}: {value}")
