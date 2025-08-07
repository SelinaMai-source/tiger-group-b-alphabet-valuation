# sotp_model/statistical_models.py

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, PolynomialFeatures
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score
import statsmodels.api as sm
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import adfuller
from scipy import stats
import warnings
warnings.filterwarnings('ignore')

class StatisticalPredictionModels:
    """
    复杂的统计预测模型集合
    用于预测SOTP模型中的关键变量
    """
    
    def __init__(self):
        self.models = {}
        self.scalers = {}
        
    def predict_revenue_growth(self, historical_data, forecast_periods=5):
        """
        预测收入增长
        使用ARIMA模型和机器学习模型
        """
        if len(historical_data) < 3:
            return 0.03  # 从5%调整为3%，更保守
        
        # 转换为时间序列
        revenue_series = pd.Series(historical_data)
        
        # 计算增长率
        growth_rates = revenue_series.pct_change().dropna()
        
        # 检查平稳性
        if len(growth_rates) > 2:
            adf_result = adfuller(growth_rates)
            is_stationary = adf_result[1] < 0.05
        else:
            is_stationary = False
        
        if is_stationary and len(growth_rates) >= 3:
            # 使用ARIMA模型
            try:
                model = ARIMA(growth_rates, order=(1, 0, 1))
                fitted_model = model.fit()
                forecast = fitted_model.forecast(steps=forecast_periods)
                predicted_growth = np.mean(forecast)
            except:
                predicted_growth = np.mean(growth_rates)
        else:
            # 使用简单平均
            predicted_growth = np.mean(growth_rates) if len(growth_rates) > 0 else 0.03
        
        # 使用机器学习模型进行补充预测
        ml_prediction = self._ml_revenue_prediction(historical_data)
        
        # 加权平均，更保守
        final_prediction = 0.6 * predicted_growth + 0.4 * ml_prediction
        
        # 更保守的限制
        return max(min(final_prediction, 0.25), -0.2)  # 限制在-20%到25%之间
    
    def _ml_revenue_prediction(self, historical_data):
        """
        使用机器学习模型预测收入
        """
        if len(historical_data) < 3:
            return 0.03  # 从5%调整为3%
        
        # 创建特征
        X = []
        y = []
        
        for i in range(2, len(historical_data)):
            X.append([historical_data[i-2], historical_data[i-1]])
            y.append(historical_data[i])
        
        if len(X) < 2:
            return 0.03
        
        X = np.array(X)
        y = np.array(y)
        
        # 标准化
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 训练多个模型
        models = {
            'ridge': Ridge(alpha=1.0),
            'lasso': Lasso(alpha=0.1),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'gradient_boosting': GradientBoostingRegressor(n_estimators=100, random_state=42)
        }
        
        predictions = []
        
        for name, model in models.items():
            try:
                model.fit(X_scaled, y)
                # 预测下一个值
                next_features = scaler.transform([[historical_data[-2], historical_data[-1]]])
                pred = model.predict(next_features)[0]
                predictions.append(pred)
            except:
                continue
        
        if predictions:
            return np.mean(predictions) / historical_data[-1] - 1  # 转换为增长率
        else:
            return 0.03  # 从5%调整为3%
    
    def predict_operating_margin(self, historical_margins, revenue_growth, industry_data=None):
        """
        预测营业利润率
        考虑规模效应、行业趋势等因素
        """
        if len(historical_margins) < 2:
            return 0.25  # 默认25%
        
        # 计算历史趋势
        margin_trend = np.polyfit(range(len(historical_margins)), historical_margins, 1)[0]
        
        # 规模效应调整（收入增长对利润率的影响）
        scale_effect = 0.1 * revenue_growth  # 假设10%的收入增长带来1%的利润率提升
        
        # 预测未来利润率
        current_margin = historical_margins[-1]
        predicted_margin = current_margin + margin_trend + scale_effect
        
        # 考虑行业数据
        if industry_data:
            industry_margin = np.mean(industry_data)
            # 加权平均
            predicted_margin = 0.7 * predicted_margin + 0.3 * industry_margin
        
        return max(min(predicted_margin, 0.5), 0.05)  # 限制在5%-50%之间
    
    def predict_market_share(self, current_share, historical_shares, competitor_data):
        """
        预测市场份额
        考虑竞争态势、技术优势等因素
        """
        if len(historical_shares) < 2:
            return current_share
        
        # 计算历史趋势
        share_trend = np.polyfit(range(len(historical_shares)), historical_shares, 1)[0]
        
        # 竞争分析
        competitor_strength = self._analyze_competition(competitor_data)
        
        # 预测市场份额
        predicted_share = current_share + share_trend + competitor_strength
        
        return max(min(predicted_share, 1.0), 0.0)  # 限制在0%-100%之间
    
    def _analyze_competition(self, competitor_data):
        """
        分析竞争态势
        """
        if not competitor_data:
            return 0
        
        # 计算竞争对手的平均增长率
        competitor_growth = np.mean([comp.get('growth_rate', 0) for comp in competitor_data])
        
        # 计算技术优势
        tech_advantage = np.mean([comp.get('tech_score', 0.5) for comp in competitor_data])
        
        # 综合评分
        competition_score = (competitor_growth + tech_advantage) / 2
        
        return competition_score * 0.01  # 转换为市场份额影响
    
    def predict_technology_readiness(self, current_readiness, investment_level, time_horizon):
        """
        预测技术成熟度
        基于投资水平、时间跨度等因素
        """
        # 技术成熟度评分（0-1）
        readiness_levels = {
            'early_stage': 0.2,
            'intermediate': 0.5,
            'advanced': 0.8,
            'mature': 0.95,
            'experimental': 0.1
        }
        
        current_score = readiness_levels.get(current_readiness, 0.5)
        
        # 投资效应
        investment_effect = min(investment_level / 1000000000, 0.3)  # 投资效应上限30%
        
        # 时间效应
        time_effect = min(time_horizon / 10, 0.2)  # 时间效应上限20%
        
        # 预测成熟度
        predicted_score = current_score + investment_effect + time_effect
        
        # 映射回成熟度等级
        if predicted_score >= 0.9:
            return 'mature'
        elif predicted_score >= 0.7:
            return 'advanced'
        elif predicted_score >= 0.4:
            return 'intermediate'
        elif predicted_score >= 0.2:
            return 'early_stage'
        else:
            return 'experimental'
    
    def predict_regulatory_risk(self, current_risk, industry_trends, political_factors):
        """
        预测监管风险
        基于行业趋势、政治因素等
        """
        risk_levels = {
            'low': 0.2,
            'medium': 0.5,
            'high': 0.8,
            'very_high': 0.95
        }
        
        current_score = risk_levels.get(current_risk, 0.5)
        
        # 行业趋势影响
        industry_effect = industry_trends.get('regulatory_trend', 0) * 0.1
        
        # 政治因素影响
        political_effect = political_factors.get('political_stability', 0) * 0.1
        
        # 预测风险
        predicted_score = current_score + industry_effect + political_effect
        
        # 映射回风险等级
        if predicted_score >= 0.8:
            return 'very_high'
        elif predicted_score >= 0.6:
            return 'high'
        elif predicted_score >= 0.4:
            return 'medium'
        else:
            return 'low'
    
    def predict_success_probability(self, project_data):
        """
        预测项目成功概率
        基于多个因素的复合模型
        """
        # 基础成功概率
        base_probability = 0.3
        
        # 技术成熟度影响
        tech_readiness = project_data.get('technology_readiness', 'intermediate')
        tech_scores = {
            'experimental': 0.1,
            'early_stage': 0.2,
            'intermediate': 0.4,
            'advanced': 0.6,
            'mature': 0.8
        }
        tech_effect = tech_scores.get(tech_readiness, 0.4)
        
        # 市场大小影响
        market_size = project_data.get('market_size', 0)
        market_effect = min(market_size / 1e12, 0.3)  # 市场效应上限30%
        
        # 竞争水平影响
        competition_level = project_data.get('competition_level', 'medium')
        competition_scores = {
            'low': 0.2,
            'medium': 0.0,
            'high': -0.2
        }
        competition_effect = competition_scores.get(competition_level, 0.0)
        
        # 监管风险影响
        regulatory_risk = project_data.get('regulatory_risk', 'medium')
        regulatory_scores = {
            'low': 0.1,
            'medium': 0.0,
            'high': -0.15,
            'very_high': -0.25
        }
        regulatory_effect = regulatory_scores.get(regulatory_risk, 0.0)
        
        # 计算最终成功概率
        success_probability = base_probability + tech_effect + market_effect + competition_effect + regulatory_effect
        
        return max(min(success_probability, 0.9), 0.05)  # 限制在5%-90%之间
    
    def predict_valuation_multiple(self, industry_data, company_financials, market_conditions):
        """
        预测估值倍数
        基于行业数据、公司财务、市场条件
        """
        # 基础倍数
        base_multiple = 20.0
        
        # 行业平均倍数
        industry_multiple = np.mean(industry_data.get('peer_multiples', [20.0]))
        
        # 财务质量调整
        financial_quality = self._assess_financial_quality(company_financials)
        
        # 市场条件调整
        market_condition = market_conditions.get('market_sentiment', 1.0)
        
        # 计算预测倍数
        predicted_multiple = base_multiple * financial_quality * market_condition
        
        # 与行业平均的加权
        final_multiple = 0.6 * predicted_multiple + 0.4 * industry_multiple
        
        return max(min(final_multiple, 50.0), 5.0)  # 限制在5-50倍之间
    
    def _assess_financial_quality(self, financials):
        """
        评估财务质量
        """
        # 计算各种财务比率
        revenue_growth = financials.get('revenue_growth', 0.1)
        profit_margin = financials.get('profit_margin', 0.2)
        debt_ratio = financials.get('debt_ratio', 0.3)
        
        # 综合评分
        quality_score = (revenue_growth * 0.4 + profit_margin * 0.4 + (1 - debt_ratio) * 0.2)
        
        return max(min(quality_score * 2, 1.5), 0.5)  # 限制在0.5-1.5之间
    
    def monte_carlo_simulation(self, predictions, n_simulations=10000):
        """
        Monte Carlo模拟预测结果
        """
        results = []
        
        for _ in range(n_simulations):
            # 为每个预测添加随机扰动
            simulated_result = {}
            for key, value in predictions.items():
                if isinstance(value, (int, float)):
                    # 添加正态分布扰动
                    noise = np.random.normal(0, value * 0.1)  # 10%的标准差
                    simulated_result[key] = max(value + noise, 0)
                else:
                    simulated_result[key] = value
            
            results.append(simulated_result)
        
        return results

def create_comprehensive_prediction_model():
    """
    创建综合预测模型
    """
    model = StatisticalPredictionModels()
    
    # 示例：预测Alphabet各业务线的关键变量
    predictions = {}
    
    # Google Services预测
    services_data = {
        'historical_revenue': [256.7, 279.8, 307.4],  # 2021-2023 (B)
        'historical_margins': [0.307, 0.321, 0.329],  # 2021-2023
        'market_share': 0.92,  # 92%市场份额
        'competitor_data': [
            {'growth_rate': 0.15, 'tech_score': 0.8},
            {'growth_rate': 0.12, 'tech_score': 0.7}
        ]
    }
    
    predictions['google_services'] = {
        'revenue_growth': model.predict_revenue_growth(services_data['historical_revenue']),
        'operating_margin': model.predict_operating_margin(services_data['historical_margins'], 0.1),
        'market_share': model.predict_market_share(services_data['market_share'], [0.90, 0.91, 0.92], services_data['competitor_data'])
    }
    
    # Google Cloud预测
    cloud_data = {
        'historical_revenue': [19.2, 26.3, 33.1],  # 2021-2023 (B)
        'historical_margins': [-0.161, -0.119, 0.026],  # 2021-2023
        'technology_readiness': 'advanced',
        'investment_level': 50000000000  # 50B投资
    }
    
    predictions['google_cloud'] = {
        'revenue_growth': model.predict_revenue_growth(cloud_data['historical_revenue']),
        'operating_margin': model.predict_operating_margin(cloud_data['historical_margins'], 0.25),
        'technology_readiness': model.predict_technology_readiness(
            cloud_data['technology_readiness'], 
            cloud_data['investment_level'], 
            3
        )
    }
    
    return predictions

if __name__ == "__main__":
    print("🔍 测试统计预测模型...")
    
    # 创建预测模型
    predictions = create_comprehensive_prediction_model()
    
    print("📊 预测结果：")
    for business, pred in predictions.items():
        print(f"\n{business}:")
        for key, value in pred.items():
            if isinstance(value, float):
                print(f"  {key}: {value:.3f}")
            else:
                print(f"  {key}: {value}")
    
    print("\n✅ 统计预测模型测试完成！")
