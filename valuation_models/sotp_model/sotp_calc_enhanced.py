# sotp_model/sotp_calc_enhanced.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import sys
import os
import yfinance as yf
from scipy import stats
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.append(project_root)

# 导入自定义模块
try:
    from .sotp_data_detailed import get_alphabet_business_breakdown, get_other_bets_detailed_breakdown, get_market_data
    from .real_option_model import RealOptionModel, calculate_other_bets_real_option_valuation
    from .statistical_models import StatisticalPredictionModels
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from sotp_data_detailed import get_alphabet_business_breakdown, get_other_bets_detailed_breakdown, get_market_data
    from real_option_model import RealOptionModel, calculate_other_bets_real_option_valuation
    from statistical_models import StatisticalPredictionModels

class AdvancedSOTPCalculator:
    """
    高级SOTP计算器
    包含：
    1. 更多历史数据收集
    2. 更复杂的统计模型
    3. 详细的可比公司分析
    4. Monte Carlo模拟进行敏感性分析
    """
    
    def __init__(self):
        self.real_option_model = RealOptionModel()
        self.statistical_model = StatisticalPredictionModels()
        self.historical_data = {}
        self.comparable_companies = {}
        self.monte_carlo_results = {}
        
    def collect_historical_data(self, ticker="GOOG"):
        """
        收集更多历史数据
        """
        print("📊 收集历史数据...")
        
        try:
            stock = yf.Ticker(ticker)
            
            # 获取历史财务数据
            income_stmt = stock.financials
            balance_sheet = stock.balance_sheet
            cash_flow = stock.cashflow
            
            # 获取历史股价数据
            hist = stock.history(period="5y")
            
            # 获取基本信息
            info = stock.info
            
            # 计算历史PE倍数
            pe_ratios = []
            for year in range(2019, 2024):
                try:
                    if year in income_stmt.columns:
                        eps = income_stmt.loc['Net Income', year] / info.get('sharesOutstanding', 13e9)
                        if year in hist.index:
                            price = hist.loc[hist.index.year == year, 'Close'].mean()
                            if eps > 0:
                                pe_ratios.append(price / eps)
                except:
                    continue
            
            # 计算历史EV/EBITDA倍数
            ev_ebitda_ratios = []
            for year in range(2019, 2024):
                try:
                    if year in income_stmt.columns and year in balance_sheet.columns:
                        ebitda = income_stmt.loc['EBITDA', year] if 'EBITDA' in income_stmt.index else income_stmt.loc['Net Income', year] * 1.2
                        market_cap = info.get('marketCap', 0)
                        total_debt = balance_sheet.loc['Total Debt', year] if 'Total Debt' in balance_sheet.index else 0
                        cash = balance_sheet.loc['Cash', year] if 'Cash' in balance_sheet.index else 0
                        ev = market_cap + total_debt - cash
                        if ebitda > 0:
                            ev_ebitda_ratios.append(ev / ebitda)
                except:
                    continue
            
            self.historical_data = {
                'pe_ratios': pe_ratios,
                'ev_ebitda_ratios': ev_ebitda_ratios,
                'income_stmt': income_stmt,
                'balance_sheet': balance_sheet,
                'cash_flow': cash_flow,
                'hist': hist,
                'info': info
            }
            
            print(f"✅ 历史数据收集完成：{len(pe_ratios)}年PE数据，{len(ev_ebitda_ratios)}年EV/EBITDA数据")
            
        except Exception as e:
            print(f"⚠️ 历史数据收集失败：{e}")
            self.historical_data = {}
    
    def analyze_comparable_companies(self):
        """
        进行详细的可比公司分析
        """
        print("🔍 分析可比公司...")
        
        # 定义可比公司
        comparable_companies = {
            'google_services': ['META', 'AMZN', 'NFLX', 'TSLA'],
            'google_cloud': ['MSFT', 'AMZN', 'ORCL', 'CRM']
        }
        
        for business, companies in comparable_companies.items():
            self.comparable_companies[business] = {}
            
            for company in companies:
                try:
                    stock = yf.Ticker(company)
                    info = stock.info
                    
                    # 获取财务指标
                    pe_ratio = info.get('trailingPE', 0)
                    ev_ebitda = info.get('enterpriseToEbitda', 0)
                    revenue = info.get('totalRevenue', 0)
                    net_income = info.get('netIncomeToCommon', 0)
                    market_cap = info.get('marketCap', 0)
                    
                    self.comparable_companies[business][company] = {
                        'pe_ratio': pe_ratio,
                        'ev_ebitda': ev_ebitda,
                        'revenue': revenue,
                        'net_income': net_income,
                        'market_cap': market_cap,
                        'revenue_growth': self._calculate_revenue_growth(stock),
                        'profit_margin': net_income / revenue if revenue > 0 else 0
                    }
                    
                except Exception as e:
                    print(f"⚠️ 获取{company}数据失败：{e}")
                    continue
        
        print("✅ 可比公司分析完成")
    
    def _calculate_revenue_growth(self, stock):
        """
        计算收入增长率
        """
        try:
            financials = stock.financials
            if 'Total Revenue' in financials.index and len(financials.columns) >= 2:
                current_revenue = financials.loc['Total Revenue', financials.columns[0]]
                previous_revenue = financials.loc['Total Revenue', financials.columns[1]]
                return (current_revenue - previous_revenue) / previous_revenue
        except:
            pass
        return 0.1  # 默认10%增长
    
    def run_monte_carlo_simulation(self, base_results, n_simulations=10000):
        """
        使用Monte Carlo模拟进行敏感性分析
        """
        print("🎲 运行Monte Carlo模拟...")
        
        # 定义参数分布
        parameters = {
            'pe_multiple': {'mean': 24.0, 'std': 3.0, 'min': 15.0, 'max': 35.0},
            'ev_ebitda_multiple': {'mean': 13.0, 'std': 2.0, 'min': 8.0, 'max': 20.0},
            'revenue_growth': {'mean': 0.08, 'std': 0.03, 'min': 0.02, 'max': 0.15},
            'profit_margin': {'mean': 0.25, 'std': 0.05, 'min': 0.15, 'max': 0.35},
            'success_probability': {'mean': 0.25, 'std': 0.1, 'min': 0.1, 'max': 0.5}
        }
        
        # 运行Monte Carlo模拟
        results = []
        
        for i in range(n_simulations):
            # 生成随机参数
            pe_multiple = np.random.normal(parameters['pe_multiple']['mean'], parameters['pe_multiple']['std'])
            pe_multiple = np.clip(pe_multiple, parameters['pe_multiple']['min'], parameters['pe_multiple']['max'])
            
            ev_ebitda_multiple = np.random.normal(parameters['ev_ebitda_multiple']['mean'], parameters['ev_ebitda_multiple']['std'])
            ev_ebitda_multiple = np.clip(ev_ebitda_multiple, parameters['ev_ebitda_multiple']['min'], parameters['ev_ebitda_multiple']['max'])
            
            revenue_growth = np.random.normal(parameters['revenue_growth']['mean'], parameters['revenue_growth']['std'])
            revenue_growth = np.clip(revenue_growth, parameters['revenue_growth']['min'], parameters['revenue_growth']['max'])
            
            profit_margin = np.random.normal(parameters['profit_margin']['mean'], parameters['profit_margin']['std'])
            profit_margin = np.clip(profit_margin, parameters['profit_margin']['min'], parameters['profit_margin']['max'])
            
            success_probability = np.random.normal(parameters['success_probability']['mean'], parameters['success_probability']['std'])
            success_probability = np.clip(success_probability, parameters['success_probability']['min'], parameters['success_probability']['max'])
            
            # 计算估值
            services_valuation = self._calculate_services_valuation_with_parameters(
                base_results['business_breakdown'], pe_multiple, revenue_growth, profit_margin
            )
            
            cloud_valuation = self._calculate_cloud_valuation_with_parameters(
                base_results['business_breakdown'], ev_ebitda_multiple, revenue_growth, profit_margin
            )
            
            other_bets_valuation = base_results['other_bets_valuation'] * success_probability / 0.25  # 调整成功概率
            
            total_valuation = services_valuation + cloud_valuation + other_bets_valuation - base_results['net_debt']
            target_price = total_valuation / base_results['shares_outstanding']
            
            results.append({
                'target_price': target_price,
                'total_valuation': total_valuation,
                'services_valuation': services_valuation,
                'cloud_valuation': cloud_valuation,
                'other_bets_valuation': other_bets_valuation,
                'pe_multiple': pe_multiple,
                'ev_ebitda_multiple': ev_ebitda_multiple,
                'revenue_growth': revenue_growth,
                'profit_margin': profit_margin,
                'success_probability': success_probability
            })
        
        # 计算统计结果
        target_prices = [r['target_price'] for r in results]
        
        self.monte_carlo_results = {
            'simulations': results,
            'target_price_mean': np.mean(target_prices),
            'target_price_std': np.std(target_prices),
            'target_price_median': np.median(target_prices),
            'target_price_5th_percentile': np.percentile(target_prices, 5),
            'target_price_95th_percentile': np.percentile(target_prices, 95),
            'confidence_interval': (np.percentile(target_prices, 2.5), np.percentile(target_prices, 97.5))
        }
        
        print(f"✅ Monte Carlo模拟完成：{n_simulations}次模拟")
        print(f"   目标股价均值：${self.monte_carlo_results['target_price_mean']:.2f}")
        print(f"   目标股价标准差：${self.monte_carlo_results['target_price_std']:.2f}")
        print(f"   95%置信区间：${self.monte_carlo_results['confidence_interval'][0]:.2f} - ${self.monte_carlo_results['confidence_interval'][1]:.2f}")
    
    def _calculate_services_valuation_with_parameters(self, business_breakdown, pe_multiple, revenue_growth, profit_margin):
        """
        使用给定参数计算Google Services估值
        """
        services_data = business_breakdown['google_services']
        revenue_2025 = services_data['revenue_2023'] * (1 + revenue_growth) ** 2
        operating_income_2025 = revenue_2025 * profit_margin
        return operating_income_2025 * pe_multiple
    
    def _calculate_cloud_valuation_with_parameters(self, business_breakdown, ev_ebitda_multiple, revenue_growth, profit_margin):
        """
        使用给定参数计算Google Cloud估值
        """
        cloud_data = business_breakdown['google_cloud']
        revenue_2025 = cloud_data['revenue_2023'] * (1 + revenue_growth) ** 2
        ebitda_2025 = revenue_2025 * profit_margin * 1.2
        return ebitda_2025 * ev_ebitda_multiple
    
    def calculate_advanced_sotp_valuation(self, ticker="GOOG"):
        """
        计算高级SOTP估值
        """
        print("🚀 开始计算高级SOTP估值...")
        
        # 1. 收集历史数据
        self.collect_historical_data(ticker)
        
        # 2. 分析可比公司
        self.analyze_comparable_companies()
        
        # 3. 获取基础数据
        business_breakdown = get_alphabet_business_breakdown()
        other_bets_breakdown = get_other_bets_detailed_breakdown()
        market_data = get_market_data()
        
        # 4. 使用历史数据调整倍数
        adjusted_market_data = self._adjust_market_data_with_historical_data(market_data)
        
        # 5. 计算基础估值
        services_valuation = self._calculate_services_valuation_advanced(business_breakdown, adjusted_market_data)
        cloud_valuation = self._calculate_cloud_valuation_advanced(business_breakdown, adjusted_market_data)
        other_bets_valuation = self._calculate_other_bets_valuation_advanced(other_bets_breakdown)
        
        # 6. 计算净债务
        net_debt = self._calculate_net_debt()
        
        # 7. 计算总估值
        total_valuation = services_valuation + cloud_valuation + other_bets_valuation - net_debt
        
        # 8. 计算目标股价
        shares_outstanding = 13_000_000_000
        target_price = total_valuation / shares_outstanding
        
        # 9. 计算占比
        total_revenue_2023 = (business_breakdown['google_services']['revenue_2023'] + 
                             business_breakdown['google_cloud']['revenue_2023'] + 
                             business_breakdown['other_bets']['revenue_2023'])
        
        services_percentage = (business_breakdown['google_services']['revenue_2023'] / total_revenue_2023) * 100
        cloud_percentage = (business_breakdown['google_cloud']['revenue_2023'] / total_revenue_2023) * 100
        other_bets_percentage = (business_breakdown['other_bets']['revenue_2023'] / total_revenue_2023) * 100
        
        # 10. 运行Monte Carlo模拟
        base_results = {
            'business_breakdown': business_breakdown,
            'other_bets_valuation': other_bets_valuation,
            'net_debt': net_debt,
            'shares_outstanding': shares_outstanding
        }
        self.run_monte_carlo_simulation(base_results)
        
        return {
            # 基础数据
            'current_price': self._get_current_price(),
            'shares_outstanding': shares_outstanding,
            'net_debt': net_debt,
            
            # 各业务线估值
            'services_valuation': services_valuation,
            'cloud_valuation': cloud_valuation,
            'other_bets_valuation': other_bets_valuation,
            
            # 总估值
            'total_business_value': services_valuation + cloud_valuation + other_bets_valuation,
            'total_valuation': total_valuation,
            'target_price': target_price,
            
            # 占比分析
            'services_percentage': services_percentage,
            'cloud_percentage': cloud_percentage,
            'other_bets_percentage': other_bets_percentage,
            
            # 高级分析结果
            'historical_data': self.historical_data,
            'comparable_companies': self.comparable_companies,
            'monte_carlo_results': self.monte_carlo_results,
            
            # 详细数据
            'business_breakdown': business_breakdown,
            'other_bets_breakdown': other_bets_breakdown,
            'market_data': adjusted_market_data
        }
    
    def _adjust_market_data_with_historical_data(self, market_data):
        """
        使用历史数据调整市场数据
        """
        adjusted_market_data = market_data.copy()
        
        # 调整PE倍数
        if self.historical_data.get('pe_ratios'):
            historical_pe_mean = np.mean(self.historical_data['pe_ratios'])
            historical_pe_std = np.std(self.historical_data['pe_ratios'])
            
            # 使用历史数据的加权平均
            adjusted_market_data['google_services_pe_multiple']['current'] = (
                0.6 * market_data['google_services_pe_multiple']['current'] +
                0.4 * historical_pe_mean
            )
            
            print(f"📊 PE倍数调整：原始{market_data['google_services_pe_multiple']['current']:.1f} -> 调整后{adjusted_market_data['google_services_pe_multiple']['current']:.1f}")
        
        # 调整EV/EBITDA倍数
        if self.historical_data.get('ev_ebitda_ratios'):
            historical_ev_ebitda_mean = np.mean(self.historical_data['ev_ebitda_ratios'])
            historical_ev_ebitda_std = np.std(self.historical_data['ev_ebitda_ratios'])
            
            adjusted_market_data['google_cloud_ev_ebitda_multiple']['current'] = (
                0.6 * market_data['google_cloud_ev_ebitda_multiple']['current'] +
                0.4 * historical_ev_ebitda_mean
            )
            
            print(f"📊 EV/EBITDA倍数调整：原始{market_data['google_cloud_ev_ebitda_multiple']['current']:.1f} -> 调整后{adjusted_market_data['google_cloud_ev_ebitda_multiple']['current']:.1f}")
        
        return adjusted_market_data
    
    def _calculate_services_valuation_advanced(self, business_breakdown, market_data):
        """
        计算Google Services估值（高级版）
        """
        services_data = business_breakdown['google_services']
        
        # 使用统计模型预测未来收入增长和利润率
        historical_revenue = [
            services_data['revenue_2021'],
            services_data['revenue_2022'],
            services_data['revenue_2023']
        ]
        
        historical_margins = [
            services_data['operating_income_2021'] / services_data['revenue_2021'],
            services_data['operating_income_2022'] / services_data['revenue_2022'],
            services_data['operating_income_2023'] / services_data['revenue_2023']
        ]
        
        # 预测未来5年的收入增长和利润率
        predicted_revenue_growth = self.statistical_model.predict_revenue_growth(historical_revenue)
        predicted_margin = self.statistical_model.predict_operating_margin(historical_margins, predicted_revenue_growth)
        
        # 预测2025年收入
        revenue_2025 = services_data['revenue_2023'] * (1 + predicted_revenue_growth) ** 2
        
        # 预测2025年营业利润
        operating_income_2025 = revenue_2025 * predicted_margin
        
        # 使用调整后的PE倍数
        pe_multiple = market_data['google_services_pe_multiple']['current']
        
        # 计算估值
        services_valuation = operating_income_2025 * pe_multiple
        
        print(f"📊 Google Services估值（高级版）：")
        print(f"  2025年预测收入：${revenue_2025/1e9:.1f}B")
        print(f"  2025年预测营业利润：${operating_income_2025/1e9:.1f}B")
        print(f"  PE倍数：{pe_multiple:.1f}")
        print(f"  估值：${services_valuation/1e9:.1f}B")
        
        return services_valuation
    
    def _calculate_cloud_valuation_advanced(self, business_breakdown, market_data):
        """
        计算Google Cloud估值（高级版）
        """
        cloud_data = business_breakdown['google_cloud']
        
        # 使用统计模型预测未来收入增长和利润率
        historical_revenue = [
            cloud_data['revenue_2021'],
            cloud_data['revenue_2022'],
            cloud_data['revenue_2023']
        ]
        
        historical_margins = [
            cloud_data['operating_income_2021'] / cloud_data['revenue_2021'],
            cloud_data['operating_income_2022'] / cloud_data['revenue_2022'],
            cloud_data['operating_income_2023'] / cloud_data['revenue_2023']
        ]
        
        # 预测未来5年的收入增长和利润率
        predicted_revenue_growth = self.statistical_model.predict_revenue_growth(historical_revenue)
        predicted_margin = self.statistical_model.predict_operating_margin(historical_margins, predicted_revenue_growth)
        
        # 预测2025年收入和EBITDA
        revenue_2025 = cloud_data['revenue_2023'] * (1 + predicted_revenue_growth) ** 2
        ebitda_2025 = revenue_2025 * predicted_margin * 1.2  # EBITDA通常比营业利润高20%
        
        # 使用调整后的EV/EBITDA倍数
        ev_ebitda_multiple = market_data['google_cloud_ev_ebitda_multiple']['current']
        
        # 计算EV
        cloud_ev = ebitda_2025 * ev_ebitda_multiple
        
        # 按比例分配净债务
        net_debt = self._calculate_net_debt()
        cloud_debt_ratio = cloud_data['revenue_2023'] / (business_breakdown['google_services']['revenue_2023'] + cloud_data['revenue_2023'])
        cloud_net_debt = net_debt * cloud_debt_ratio
        
        # 计算估值
        cloud_valuation = cloud_ev - cloud_net_debt
        
        print(f"📊 Google Cloud估值（高级版）：")
        print(f"  2025年预测收入：${revenue_2025/1e9:.1f}B")
        print(f"  2025年预测EBITDA：${ebitda_2025/1e9:.1f}B")
        print(f"  EV/EBITDA倍数：{ev_ebitda_multiple:.1f}")
        print(f"  估值：${cloud_valuation/1e9:.1f}B")
        
        return max(cloud_valuation, 0)
    
    def _calculate_other_bets_valuation_advanced(self, other_bets_breakdown):
        """
        计算Other Bets估值（高级版）
        """
        print("🔍 计算Other Bets Real Option估值（高级版）...")
        
        # 使用Real Option模型计算每个项目的估值
        real_option_results = calculate_other_bets_real_option_valuation(other_bets_breakdown)
        
        # 汇总所有项目的估值
        total_other_bets_valuation = 0
        detailed_valuations = {}
        
        for bet_name, result in real_option_results.items():
            valuation = result['final_valuation']
            total_other_bets_valuation += valuation
            
            detailed_valuations[bet_name] = {
                'valuation': valuation,
                'option_value': result['option_result']['option_value'],
                'real_option_value': result['option_result']['real_option_value'],
                'success_probability': result['option_result']['success_probability'],
                'volatility': result['option_result']['volatility'],
                'risk_adjusted_rate': result['option_result']['risk_adjusted_rate']
            }
            
            print(f"  {bet_name}: ${valuation/1e9:.2f}B (成功概率: {result['option_result']['success_probability']:.1%})")
        
        print(f"📊 Other Bets总估值（高级版）：${total_other_bets_valuation/1e9:.1f}B")
        
        return total_other_bets_valuation
    
    def _calculate_net_debt(self):
        """
        计算净债务
        """
        # 基于Alphabet 2023年财报数据
        total_debt = 15_000_000_000  # 15B
        cash = 120_000_000_000       # 120B
        net_debt = total_debt - cash
        
        return net_debt
    
    def _get_current_price(self):
        """
        获取当前股价
        """
        try:
            stock = yf.Ticker("GOOG")
            current_price = stock.info.get("currentPrice", 197.12)
            return current_price
        except:
            return 197.12  # 默认价格

def calculate_enhanced_sotp_valuation(ticker="GOOG"):
    """
    计算增强版SOTP估值的主函数
    """
    calculator = AdvancedSOTPCalculator()
    results = calculator.calculate_advanced_sotp_valuation(ticker)
    
    # 创建增强版报告
    report = f"""
    🎯 Alphabet增强版SOTP估值报告
    
    📊 估值结果：
    - 当前股价：${results['current_price']:.2f}
    - 目标股价：${results['target_price']:.2f}
    - 估值溢价：{((results['target_price'] / results['current_price'] - 1) * 100):.1f}%
    
    🏢 业务线估值：
    - Google Services：${results['services_valuation']/1e9:.1f}B ({results['services_percentage']:.1f}%)
    - Google Cloud：${results['cloud_valuation']/1e9:.1f}B ({results['cloud_percentage']:.1f}%)
    - Other Bets：${results['other_bets_valuation']/1e9:.1f}B ({results['other_bets_percentage']:.1f}%)
    
    💰 总估值：${results['total_valuation']/1e9:.1f}B
    - 净债务：${results['net_debt']/1e9:.1f}B
    
    数据来源：Alphabet 2023年10-K报告 + 统计预测模型 + Real Option模型
    """
    
    return results, report

def calculate_advanced_sotp_valuation(ticker="GOOG"):
    """
    计算高级SOTP估值的主函数
    """
    calculator = AdvancedSOTPCalculator()
    results = calculator.calculate_advanced_sotp_valuation(ticker)
    return results

if __name__ == "__main__":
    print("🔍 测试高级SOTP估值模型...")
    
    results = calculate_advanced_sotp_valuation()
    
    print(f"\n📊 高级SOTP估值结果：")
    print(f"当前股价：${results['current_price']:.2f}")
    print(f"目标股价：${results['target_price']:.2f}")
    print(f"估值溢价：{((results['target_price'] / results['current_price'] - 1) * 100):.1f}%")
    
    print(f"\n🏢 各业务线估值：")
    print(f"Google Services：${results['services_valuation']/1e9:.1f}B ({results['services_percentage']:.1f}%)")
    print(f"Google Cloud：${results['cloud_valuation']/1e9:.1f}B ({results['cloud_percentage']:.1f}%)")
    print(f"Other Bets：${results['other_bets_valuation']/1e9:.1f}B ({results['other_bets_percentage']:.1f}%)")
    
    print(f"\n💰 总估值：${results['total_valuation']/1e9:.1f}B")
    print(f"净债务：${results['net_debt']/1e9:.1f}B")
    
    if results.get('monte_carlo_results'):
        mc_results = results['monte_carlo_results']
        print(f"\n🎲 Monte Carlo模拟结果：")
        print(f"目标股价均值：${mc_results['target_price_mean']:.2f}")
        print(f"目标股价标准差：${mc_results['target_price_std']:.2f}")
        print(f"95%置信区间：${mc_results['confidence_interval'][0]:.2f} - ${mc_results['confidence_interval'][1]:.2f}")
    
    print("\n✅ 高级SOTP估值模型测试完成！")
