# pe_model/comp_fetcher.py

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

def fetch_comparable_companies():
    """
    获取可比公司的财务数据
    """
    # 定义可比公司列表
    comps = [
        "MSFT", "AAPL", "AMZN", "META", "NVDA", "TSLA", "NFLX", "ADBE", "CRM", "ORCL"
    ]
    
    data = []
    
    for ticker in comps:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # 获取财务指标
            market_cap = info.get('marketCap', 0)
            revenue = info.get('totalRevenue', 0)
            net_income = info.get('netIncomeToCommon', 0)
            pe_ratio = info.get('trailingPE', 0)
            
            if market_cap and revenue and net_income:
                data.append({
                    'ticker': ticker,
                    'market_cap': market_cap,
                    'revenue': revenue,
                    'net_income': net_income,
                    'pe_ratio': pe_ratio,
                    'gross_margin': (revenue - info.get('costOfRevenue', 0)) / revenue if revenue else 0,
                    'net_margin': net_income / revenue if revenue else 0
                })
        except Exception as e:
            print(f"⚠️ 获取 {ticker} 数据失败：{e}")
            continue
    
    return pd.DataFrame(data)

def save_comps_data(df):
    """
    保存可比公司数据
    """
    try:
        data_dir = get_data_dir()
        os.makedirs(data_dir, exist_ok=True)
        file_path = os.path.join(data_dir, "comps_table.csv")
        df.to_csv(file_path, index=False)
        print(f"✅ 可比公司数据已保存：{file_path}")
    except Exception as e:
        print(f"⚠️ 保存可比公司数据失败：{e}")

if __name__ == "__main__":
    print("🔍 正在获取可比公司数据...")
    comps_df = fetch_comparable_companies()
    
    if not comps_df.empty:
        save_comps_data(comps_df)
        print(f"✅ 成功获取 {len(comps_df)} 家可比公司数据")
        print(comps_df.head())
    else:
        print("❌ 未能获取可比公司数据")