# sotp_model/real_option_model.py

import numpy as np
import pandas as pd
from scipy.stats import norm
from scipy.optimize import minimize
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class RealOptionModel:
    """
    复杂的Real Option估值模型
    基于Black-Scholes期权定价模型和Monte Carlo模拟
    """
    
    def __init__(self, risk_free_rate=0.045, market_risk_premium=0.065):
        self.risk_free_rate = risk_free_rate
        self.market_risk_premium = market_risk_premium
        
    def black_scholes_option_price(self, S, K, T, r, sigma, option_type='call'):
        """
        Black-Scholes期权定价模型
        
        Parameters:
        S: 当前资产价格
        K: 执行价格
        T: 到期时间（年）
        r: 无风险利率
        sigma: 波动率
        option_type: 期权类型 ('call' or 'put')
        """
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)
        
        if option_type == 'call':
            price = S*norm.cdf(d1) - K*np.exp(-r*T)*norm.cdf(d2)
        else:  # put
            price = K*np.exp(-r*T)*norm.cdf(-d2) - S*norm.cdf(-d1)
            
        return price
    
    def calculate_volatility(self, historical_returns, window=252):
        """
        计算历史波动率
        """
        if len(historical_returns) < window:
            return 0.3  # 默认波动率
        
        rolling_vol = historical_returns.rolling(window=window).std()
        return rolling_vol.iloc[-1] * np.sqrt(252)  # 年化波动率
    
    def monte_carlo_simulation(self, S0, T, r, sigma, n_simulations=10000, n_steps=252):
        """
        Monte Carlo模拟资产价格路径
        """
        dt = T / n_steps
        S = np.zeros((n_simulations, n_steps + 1))
        S[:, 0] = S0
        
        for i in range(n_steps):
            Z = np.random.standard_normal(n_simulations)
            S[:, i + 1] = S[:, i] * np.exp((r - 0.5 * sigma**2) * dt + sigma * np.sqrt(dt) * Z)
        
        return S
    
    def calculate_real_option_value(self, project_data):
        """
        计算Real Option价值
        
        Parameters:
        project_data: 项目数据字典
        """
        
        # 提取项目参数
        current_value = project_data.get('current_value', 0)
        investment_cost = project_data.get('investment_cost', 0)
        time_to_maturity = project_data.get('time_to_maturity', 5)
        success_probability = project_data.get('success_probability', 0.3)
        market_size = project_data.get('market_size', 0)
        competition_level = project_data.get('competition_level', 'medium')
        regulatory_risk = project_data.get('regulatory_risk', 'medium')
        technology_readiness = project_data.get('technology_readiness', 'intermediate')
        
        # 根据项目特征调整参数
        volatility = self._calculate_project_volatility(competition_level, regulatory_risk, technology_readiness)
        risk_adjusted_rate = self._calculate_risk_adjusted_rate(project_data)
        
        # 计算期权价值
        option_value = self.black_scholes_option_price(
            S=current_value,
            K=investment_cost,
            T=time_to_maturity,
            r=risk_adjusted_rate,
            sigma=volatility,
            option_type='call'
        )
        
        # 应用成功概率
        real_option_value = option_value * success_probability
        
        return {
            'option_value': option_value,
            'real_option_value': real_option_value,
            'volatility': volatility,
            'risk_adjusted_rate': risk_adjusted_rate,
            'success_probability': success_probability
        }
    
    def _calculate_project_volatility(self, competition_level, regulatory_risk, technology_readiness):
        """
        根据项目特征计算波动率
        """
        base_volatility = 0.3
        
        # 竞争水平调整
        competition_multipliers = {
            'low': 0.8,
            'medium': 1.0,
            'high': 1.3
        }
        
        # 监管风险调整
        regulatory_multipliers = {
            'low': 0.7,
            'medium': 1.0,
            'high': 1.4,
            'very_high': 1.6
        }
        
        # 技术成熟度调整
        technology_multipliers = {
            'early_stage': 1.5,
            'intermediate': 1.2,
            'advanced': 0.9,
            'mature': 0.7,
            'experimental': 1.8
        }
        
        volatility = base_volatility * \
                    competition_multipliers.get(competition_level, 1.0) * \
                    regulatory_multipliers.get(regulatory_risk, 1.0) * \
                    technology_multipliers.get(technology_readiness, 1.0)
        
        return min(max(volatility, 0.1), 0.8)  # 限制在0.1-0.8之间
    
    def _calculate_risk_adjusted_rate(self, project_data):
        """
        计算风险调整后的折现率
        """
        base_rate = self.risk_free_rate + self.market_risk_premium
        
        # 根据项目风险特征调整
        risk_adjustments = {
            'competition_level': {'low': 0.02, 'medium': 0.04, 'high': 0.06},
            'regulatory_risk': {'low': 0.01, 'medium': 0.03, 'high': 0.05, 'very_high': 0.07},
            'technology_readiness': {'early_stage': 0.08, 'intermediate': 0.05, 'advanced': 0.03, 'mature': 0.02, 'experimental': 0.10}
        }
        
        total_adjustment = 0
        for risk_factor, adjustment_dict in risk_adjustments.items():
            factor_value = project_data.get(risk_factor, 'medium')
            total_adjustment += adjustment_dict.get(factor_value, 0.03)
        
        return base_rate + total_adjustment
    
    def calculate_compound_option_value(self, project_data):
        """
        计算复合期权价值（适用于分阶段投资的项目）
        """
        stages = project_data.get('investment_stages', [])
        if not stages:
            return self.calculate_real_option_value(project_data)
        
        # 计算每个阶段的期权价值
        stage_values = []
        current_value = project_data.get('current_value', 0)
        
        for i, stage in enumerate(stages):
            stage_option = self.calculate_real_option_value({
                **project_data,
                'current_value': current_value,
                'investment_cost': stage['cost'],
                'time_to_maturity': stage['duration'],
                'success_probability': stage['success_probability']
            })
            
            stage_values.append(stage_option['real_option_value'])
            current_value = stage_option['real_option_value']  # 下一阶段的当前价值
        
        return {
            'compound_option_value': sum(stage_values),
            'stage_values': stage_values,
            'total_stages': len(stages)
        }
    
    def sensitivity_analysis(self, project_data, parameter_name, parameter_range):
        """
        敏感性分析
        """
        results = []
        
        for param_value in parameter_range:
            modified_data = project_data.copy()
            modified_data[parameter_name] = param_value
            
            option_value = self.calculate_real_option_value(modified_data)
            results.append({
                'parameter_value': param_value,
                'option_value': option_value['real_option_value']
            })
        
        return pd.DataFrame(results)
    
    def monte_carlo_real_option(self, project_data, n_simulations=10000):
        """
        使用Monte Carlo模拟计算Real Option价值
        """
        current_value = project_data.get('current_value', 0)
        investment_cost = project_data.get('investment_cost', 0)
        time_to_maturity = project_data.get('time_to_maturity', 5)
        success_probability = project_data.get('success_probability', 0.3)
        volatility = self._calculate_project_volatility(
            project_data.get('competition_level', 'medium'),
            project_data.get('regulatory_risk', 'medium'),
            project_data.get('technology_readiness', 'intermediate')
        )
        risk_adjusted_rate = self._calculate_risk_adjusted_rate(project_data)
        
        # 模拟资产价格路径
        price_paths = self.monte_carlo_simulation(
            S0=current_value,
            T=time_to_maturity,
            r=risk_adjusted_rate,
            sigma=volatility,
            n_simulations=n_simulations
        )
        
        # 计算期权收益
        final_prices = price_paths[:, -1]
        option_payoffs = np.maximum(final_prices - investment_cost, 0)
        
        # 计算期望价值
        expected_payoff = np.mean(option_payoffs)
        option_value = expected_payoff * np.exp(-risk_adjusted_rate * time_to_maturity)
        
        # 应用成功概率
        real_option_value = option_value * success_probability
        
        return {
            'monte_carlo_option_value': option_value,
            'monte_carlo_real_option_value': real_option_value,
            'expected_payoff': expected_payoff,
            'price_paths': price_paths,
            'final_prices': final_prices
        }

def calculate_other_bets_real_option_valuation(other_bets_data):
    """
    计算Other Bets的Real Option估值
    """
    model = RealOptionModel()
    results = {}
    
    for bet_name, bet_data in other_bets_data.items():
        print(f"🔍 计算 {bet_name} 的Real Option估值...")
        
        # 准备项目数据
        project_data = {
            'current_value': bet_data['valuation_estimate'],
            'investment_cost': bet_data['valuation_estimate'] * 0.3,  # 假设投资成本为估值的30%
            'time_to_maturity': bet_data['time_to_maturity'],
            'success_probability': bet_data['success_probability'],
            'market_size': bet_data['market_size'],
            'competition_level': bet_data['competition_level'],
            'regulatory_risk': bet_data['regulatory_risk'],
            'technology_readiness': bet_data['technology_readiness']
        }
        
        # 计算Real Option价值
        option_result = model.calculate_real_option_value(project_data)
        
        # Monte Carlo模拟
        mc_result = model.monte_carlo_real_option(project_data)
        
        results[bet_name] = {
            'project_data': project_data,
            'option_result': option_result,
            'monte_carlo_result': mc_result,
            'final_valuation': option_result['real_option_value']
        }
        
        print(f"✅ {bet_name}: ${option_result['real_option_value']/1e9:.2f}B")
    
    return results

if __name__ == "__main__":
    # 测试Real Option模型
    print("🔍 测试Real Option模型...")
    
    # 创建测试项目数据
    test_project = {
        'current_value': 10_000_000_000,  # 10B
        'investment_cost': 3_000_000_000,  # 3B
        'time_to_maturity': 5,
        'success_probability': 0.35,
        'market_size': 1_000_000_000_000,  # 1T
        'competition_level': 'high',
        'regulatory_risk': 'medium',
        'technology_readiness': 'advanced'
    }
    
    model = RealOptionModel()
    result = model.calculate_real_option_value(test_project)
    
    print(f"📊 Real Option估值结果：")
    print(f"期权价值：${result['option_value']/1e9:.2f}B")
    print(f"Real Option价值：${result['real_option_value']/1e9:.2f}B")
    print(f"波动率：{result['volatility']:.2%}")
    print(f"风险调整利率：{result['risk_adjusted_rate']:.2%}")
    print(f"成功概率：{result['success_probability']:.1%}")
