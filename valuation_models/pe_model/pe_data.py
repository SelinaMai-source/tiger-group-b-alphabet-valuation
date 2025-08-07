# pe_model/pe_data.py

import yfinance as yf
import pandas as pd
import os

def get_data_dir():
    """
    获取数据目录的绝对路径
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "data", "processed")
    return data_dir

def fetch_alphabet_data(ticker="GOOG"):
    """
    获取Alphabet的财务数据
    """
    try:
        stock = yf.Ticker(ticker)
        
        # 获取财务报表
        income = stock.financials
        bs = stock.balance_sheet
        cf = stock.cashflow
        
        # 获取基本信息
        info = stock.info
        
        # 创建数据字典
        data = {
            'ticker': ticker,
            'current_price': info.get('currentPrice', 0),
            'market_cap': info.get('marketCap', 0),
            'pe_ratio': info.get('trailingPE', 0),
            'eps': info.get('trailingEps', 0),
            'revenue': info.get('totalRevenue', 0),
            'net_income': info.get('netIncomeToCommon', 0)
        }
        
        return data, income, bs, cf
        
    except Exception as e:
        print(f"⚠️ 获取Alphabet数据失败：{e}")
        return None, None, None, None

def save_alphabet_data(data, income, bs, cf):
    """
    保存Alphabet数据
    """
    try:
        data_dir = get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        
        # 保存主要数据
        df = pd.DataFrame([data])
        df.to_csv(os.path.join(data_dir, "pe_data_alphabet.csv"), index=False)
        
        # 保存财务报表
        if income is not None:
            income.to_csv(os.path.join(data_dir, "income_statement.csv"))
        if bs is not None:
            bs.to_csv(os.path.join(data_dir, "balance_sheet.csv"))
        if cf is not None:
            cf.to_csv(os.path.join(data_dir, "cashflow_statement.csv"))
            
        print(f"✅ Alphabet数据已保存到：{data_dir}")
        
    except Exception as e:
        print(f"⚠️ 保存Alphabet数据失败：{e}")

if __name__ == "__main__":
    print("🔍 正在获取Alphabet财务数据...")
    data, income, bs, cf = fetch_alphabet_data("GOOG")
    
    if data:
        save_alphabet_data(data, income, bs, cf)
        print("✅ 数据获取完成")
        print(pd.DataFrame([data]))
    else:
        print("❌ 数据获取失败")