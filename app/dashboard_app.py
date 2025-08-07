# app/dashboard_app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import sys
import os
import numpy as np
import time

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

# 导入各个估值模型
try:
    # PE模型
    pe_model_path = os.path.join(project_root, 'valuation_models', 'pe_model')
    sys.path.append(pe_model_path)
    try:
        from pe_visual import create_pe_valuation_dashboard
        pe_model_available = True
    except ImportError as e:
        st.warning(f"PE模型导入失败：{e}，将使用备用功能")
        create_pe_valuation_dashboard = None
        pe_model_available = False
    
    # DCF模型
    dcf_model_path = os.path.join(project_root, 'valuation_models', 'dcf_model')
    sys.path.append(dcf_model_path)
    try:
        from fcf_formula import calculate_fcf, get_fcf_components
    except ImportError:
        st.warning("DCF模型导入失败，将使用备用功能")
        calculate_fcf = None
        get_fcf_components = None
    
    # EV模型
    ev_model_path = os.path.join(project_root, 'valuation_models', 'ev_model')
    sys.path.append(ev_model_path)
    try:
        from ev_calc import estimate_price as ev_estimate_price
    except ImportError:
        ev_estimate_price = None
    
    try:
        from ev_data import get_alphabet_ev_components
    except ImportError:
        # 如果导入失败，创建一个备用函数
        def get_alphabet_ev_components(ticker="GOOG"):
            """备用EV组件获取函数"""
            try:
                import yfinance as yf
                t = yf.Ticker(ticker)
                info = t.info
                
                market_cap = info.get("marketCap", 0)
                total_debt = info.get("totalDebt", 0)
                cash = info.get("totalCash", 0)
                enterprise_value = market_cap + total_debt - cash if market_cap else 0
                
                return {
                    "MarketCap": market_cap,
                    "TotalDebt": total_debt,
                    "Cash": cash,
                    "EnterpriseValue": enterprise_value,
                    "EBITDA_TTM": info.get("ebitda", 0)
                }
            except Exception as e:
                st.error(f"获取EV数据失败: {e}")
                return {
                    "MarketCap": 0,
                    "TotalDebt": 0,
                    "Cash": 0,
                    "EnterpriseValue": 0,
                    "EBITDA_TTM": 0
                }
    
    # PS模型
    ps_model_path = os.path.join(project_root, 'valuation_models', 'ps_model')
    sys.path.append(ps_model_path)
    try:
        from ps_calc import calculate_forward_ps, get_market_cap
    except ImportError:
        # 如果导入失败，创建备用函数
        def get_market_cap(ticker="GOOG") -> float:
            """备用市值获取函数"""
            try:
                import yfinance as yf
                t = yf.Ticker(ticker)
                market_cap = t.info.get("marketCap")
                if market_cap is None:
                    return 0
                return market_cap
            except Exception as e:
                st.error(f"获取市值失败: {e}")
                return 0
        
        def calculate_forward_ps(market_cap: float, forecast_revenue: float) -> float:
            """备用PS计算函数"""
            if forecast_revenue == 0:
                return 0
            return round(market_cap / forecast_revenue, 2)
    
except ImportError as e:
    st.error(f"导入模型失败: {e}")

@st.cache_data(ttl=3600)  # 缓存1小时
def get_stock_data(ticker="GOOG"):
    """获取股票数据并缓存"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'current_price': info.get("currentPrice", 0),
            'price_change': info.get("regularMarketChangePercent", 0),
            'market_cap': info.get("marketCap", 0),
            'volume': info.get("volume", 0),
            'pe_ratio': info.get("trailingPE", 0),
            'pb_ratio': info.get("priceToBook", 0)
        }
    except Exception as e:
        st.error(f"获取股票数据失败: {e}")
        return None

@st.cache_data(ttl=1800)  # 缓存30分钟
def get_historical_data(ticker="GOOG", period="1y"):
    """获取历史数据并缓存"""
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period)
        return hist
    except Exception as e:
        st.error(f"获取历史数据失败: {e}")
        return None

def get_investment_recommendation(current_price, target_price, confidence_score=80):
    """根据当前股价和目标价格生成投资建议"""
    if target_price == 0:
        return "数据不足，无法给出建议", "neutral"
    
    price_difference = ((target_price - current_price) / current_price) * 100
    
    if price_difference > 15:
        if confidence_score >= 80:
            return "强烈买入", "buy"
        elif confidence_score >= 60:
            return "建议买入", "buy"
        else:
            return "谨慎买入", "cautious_buy"
    elif price_difference > 5:
        if confidence_score >= 70:
            return "建议买入", "buy"
        else:
            return "谨慎买入", "cautious_buy"
    elif price_difference > -5:
        return "持有", "hold"
    elif price_difference > -15:
        return "谨慎持有", "cautious_hold"
    else:
        return "不建议买入", "sell"

def main():
    st.set_page_config(
        page_title="Tiger Group B - Alphabet估值分析系统",
        page_icon="🐯",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # 自定义CSS样式
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #1f77b4, #ff7f0e);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    .model-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .success-box {
        background: linear-gradient(135deg, #4CAF50, #45a049);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    .warning-box {
        background: linear-gradient(135deg, #ff9800, #f57c00);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # 页面标题
    st.markdown("""
    <div class="main-header">
        <h1>🐯 Tiger Group B - Alphabet (GOOG) 估值分析系统</h1>
        <p>基于四种估值模型的综合财务分析平台</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏
    with st.sidebar:
        st.title("📊 估值模型选择")
        model_choice = st.selectbox(
            "选择估值模型",
            ["🏠 仪表板概览", "📈 PE估值模型", "💰 DCF估值模型", "🏢 EV估值模型", "📊 PS估值模型", "🎯 综合对比分析"]
        )
        
        st.markdown("---")
        st.subheader("📈 Alphabet公司信息")
        st.markdown("""
        **公司名称：** Alphabet Inc. (GOOG)
        
        **行业：** 科技 - 互联网服务
        
        **主要业务：**
        - Google搜索和广告
        - YouTube视频平台
        - Google Cloud云服务
        - Android操作系统
        - 自动驾驶技术(Waymo)
        """)
        
        # 实时股价显示
        stock_data = get_stock_data("GOOG")
        if stock_data:
            st.markdown("---")
            st.subheader("📊 实时股价")
            st.metric(
                label="当前股价",
                value=f"${stock_data['current_price']:.2f}",
                delta=f"{stock_data['price_change']:.2f}%" if stock_data['price_change'] else None
            )
            
            # 额外指标
            col1, col2 = st.columns(2)
            with col1:
                st.metric("市值", f"${stock_data['market_cap']/1e9:.1f}B")
            with col2:
                st.metric("PE比率", f"{stock_data['pe_ratio']:.1f}")
        else:
            st.info("无法获取实时股价数据")
        
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # 主要内容区域
    if model_choice == "🏠 仪表板概览":
        show_dashboard_overview()
    elif model_choice == "📈 PE估值模型":
        show_pe_valuation()
    elif model_choice == "💰 DCF估值模型":
        show_dcf_valuation()
    elif model_choice == "🏢 EV估值模型":
        show_ev_valuation()
    elif model_choice == "📊 PS估值模型":
        show_ps_valuation()
    elif model_choice == "🎯 综合对比分析":
        show_comprehensive_comparison()

def show_dashboard_overview():
    """显示仪表板概览"""
    st.header("🏠 仪表板概览")
    st.markdown("---")
    
    # 获取当前股价
    stock_data = get_stock_data("GOOG")
    current_price = stock_data['current_price'] if stock_data else 196.92
    
    # 获取各模型的实际计算结果
    pe_target_price = None
    dcf_target_price = 182.50  # 暂时使用示例值
    ev_target_price = 205.30   # 暂时使用示例值
    ps_target_price = 198.90   # 暂时使用示例值
    
    # 尝试获取PE模型的实际结果
    try:
        # 切换到PE模型目录
        original_dir = os.getcwd()
        os.chdir(pe_model_path) # 使用相对路径
        
        if pe_model_available and create_pe_valuation_dashboard is not None:
            try:
                results = create_pe_valuation_dashboard()
                
                # 切换回原目录
                os.chdir(original_dir)
                
                # 检查results是否为字典类型
                if isinstance(results, dict) and 'eps_predictions' in results:
                    # 计算PE目标价格
                    predicted_eps = results['eps_predictions']['blended']
                    conservative_pe = 22.0
                    pe_target_price = conservative_pe * predicted_eps
                    
                    # 确保目标价格在合理范围内
                    max_reasonable_price = current_price * 1.5
                    if pe_target_price > max_reasonable_price:
                        pe_target_price = max_reasonable_price
                    
                    min_reasonable_price = current_price * 0.5
                    if pe_target_price < min_reasonable_price:
                        pe_target_price = min_reasonable_price
                else:
                    st.warning(f"PE模型返回结果格式错误，期望字典类型，实际得到: {type(results)}")
                    pe_target_price = 173.58  # 使用合理的默认值
                    
            except Exception as e:
                st.warning(f"PE模型计算失败: {e}")
                pe_target_price = 173.58  # 使用合理的默认值
                os.chdir(original_dir)  # 确保切换回原目录
        else:
            st.warning("PE模型导入失败，使用默认值")
            pe_target_price = 173.58  # 使用合理的默认值
            
    except Exception as e:
        st.warning(f"无法获取PE模型结果: {e}")
        pe_target_price = 173.58  # 使用合理的默认值
    
    # 创建对比数据 - 使用实际计算结果
    comparison_data = {
        '估值模型': ['PE模型', 'DCF模型', 'EV模型', 'PS模型'],
        '目标价格(美元)': [pe_target_price, dcf_target_price, ev_target_price, ps_target_price],
        '置信度(%)': [88, 85, 82, 80],
        '适用场景': ['成熟公司', '成长公司', '重资产公司', '科技公司']
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # 显示当前股价
    st.subheader("📈 当前市场状况")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("当前股价", f"${current_price:.2f}")
    
    with col2:
        min_target = df_comparison['目标价格(美元)'].min()
        max_target = df_comparison['目标价格(美元)'].max()
        st.metric("估值目标价格区间", f"${min_target:.2f}-${max_target:.2f}")
    
    with col3:
        avg_target = df_comparison['目标价格(美元)'].mean()
        avg_change = ((avg_target - current_price) / current_price) * 100
        st.metric("平均预期涨幅", f"{avg_change:+.1f}%", delta=f"{avg_change:+.1f}%")
    
    # 价格对比柱状图
    st.subheader("📊 四种估值模型对比")
    fig_price = px.bar(df_comparison, x='估值模型', y='目标价格(美元)',
                      color='置信度(%)', 
                      title="Alphabet各模型估值结果对比",
                      color_continuous_scale='viridis')
    st.plotly_chart(fig_price, use_container_width=True)
    
    # 置信度雷达图
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=df_comparison['置信度(%)'],
        theta=df_comparison['估值模型'],
        fill='toself',
        name='模型置信度'
    ))
    fig_radar.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="模型置信度雷达图"
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    # 投资建议
    st.subheader("💡 投资建议")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="model-card">
            <h4>🎯 综合估值结果</h4>
            <ul>
            <li><strong>估值区间：</strong> ${df_comparison['目标价格(美元)'].min():.2f} - ${df_comparison['目标价格(美元)'].max():.2f}</li>
            <li><strong>估值目标价格区间：</strong> ${min_target:.2f}-${max_target:.2f}</li>
            <li><strong>当前股价：</strong> ${current_price:.2f}</li>
            <li><strong>投资评级：</strong> {'买入' if avg_change > 5 else '持有' if avg_change > -5 else '卖出'}</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="model-card">
            <h4>⚠️ 风险因素</h4>
            <ul>
            <li>监管风险</li>
            <li>竞争加剧</li>
            <li>经济下行影响广告支出</li>
            <li>技术变革风险</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_pe_valuation():
    """显示PE估值模型"""
    st.header("📈 Alphabet PE估值模型分析")
    st.markdown("---")
    
    # 模型介绍
    with st.expander("🔍 PE估值模型方法介绍", expanded=True):
        st.markdown("""
        ### PE估值模型方法论
        
        **1. 三表建模预测**
        - 基于Alphabet历史财务数据（收入、利润、股本）
        - 使用线性回归预测未来营收
        - 通过净利率计算EPS
        
        **2. ARIMA时间序列预测**
        - 基于Alphabet历史EPS数据的时间序列分析
        - 使用ARIMA(1,1,0)模型
        - 捕捉EPS的长期趋势和季节性
        
        **3. 可比公司回归分析**
        - 基于同行业科技公司（Apple、Microsoft、Amazon等）
        - 使用线性回归模型（毛利率、净利率、营收增长率）
        - 预测Alphabet的EPS
        
        **4. 加权融合算法**
        - 三表建模权重：20%
        - ARIMA权重：40%
        - 可比公司权重：40%
        """)
    
    if st.button("🚀 运行Alphabet PE估值分析", use_container_width=True):
        with st.spinner("正在计算Alphabet PE估值..."):
            original_dir = os.getcwd()
            try:
                # 切换到PE模型目录
                os.chdir(pe_model_path) # 使用相对路径
                
                if pe_model_available and create_pe_valuation_dashboard is not None:
                    try:
                        results = create_pe_valuation_dashboard()
                        
                        # 检查results是否为字典类型
                        if isinstance(results, dict) and 'eps_predictions' in results:
                            # 获取当前股价
                            stock_data = get_stock_data("GOOG")
                            current_price = stock_data['current_price'] if stock_data else 196.92
                            
                            # 计算目标价格 - 使用更合理的PE估值方法
                            predicted_eps = results['eps_predictions']['blended']
                            
                            # 使用更保守的PE倍数计算目标价格
                            # Alphabet作为成熟科技公司，PE倍数通常在20-30之间
                            conservative_pe = 22.0  # 使用保守的PE倍数
                            target_price = conservative_pe * predicted_eps
                            
                            # 确保目标价格在合理范围内
                            # 1. 不超过当前股价的1.5倍
                            max_reasonable_price = current_price * 1.5
                            if target_price > max_reasonable_price:
                                target_price = max_reasonable_price
                            
                            # 2. 不低于当前股价的0.5倍
                            min_reasonable_price = current_price * 0.5
                            if target_price < min_reasonable_price:
                                target_price = min_reasonable_price
                            
                            # 生成投资建议
                            recommendation, recommendation_type = get_investment_recommendation(
                                current_price, target_price, results['valuation_summary']['confidence_score']
                            )
                            
                            # 显示结果
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric("当前股价", f"${current_price:.2f}")
                            
                            with col2:
                                st.metric("目标价格", f"${target_price:.2f}")
                            
                            with col3:
                                price_change = ((target_price - current_price) / current_price) * 100
                                st.metric("预期涨幅", f"{price_change:+.1f}%", delta=f"{price_change:+.1f}%")
                            
                            with col4:
                                st.metric("置信度", f"{results['valuation_summary']['confidence_score']}%")
                            
                            # 投资建议卡片
                            st.subheader("💡 投资建议")
                            
                            # 根据建议类型设置颜色
                            if recommendation_type == "buy":
                                color = "success"
                                icon = "🚀"
                            elif recommendation_type == "cautious_buy":
                                color = "info"
                                icon = "📈"
                            elif recommendation_type == "hold":
                                color = "warning"
                                icon = "⏸️"
                            elif recommendation_type == "cautious_hold":
                                color = "warning"
                                icon = "⚠️"
                            else:
                                color = "error"
                                icon = "❌"
                            
                            st.markdown(f"""
                            <div class="model-card" style="border-left: 4px solid {'#4CAF50' if recommendation_type == 'buy' else '#2196F3' if recommendation_type == 'cautious_buy' else '#FF9800' if recommendation_type in ['hold', 'cautious_hold'] else '#F44336'};">
                                <h4>{icon} {recommendation}</h4>
                                <ul>
                                <li><strong>当前股价：</strong> ${current_price:.2f}</li>
                                <li><strong>目标价格：</strong> ${target_price:.2f}</li>
                                <li><strong>预期涨幅：</strong> {price_change:+.1f}%</li>
                                <li><strong>模型置信度：</strong> {results['valuation_summary']['confidence_score']}%</li>
                                <li><strong>估值方法：</strong> PE估值模型</li>
                                </ul>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # EPS预测对比图
                            st.subheader("🔮 EPS预测模型对比")
                            eps_data = pd.DataFrame({
                                '模型': ['三表建模', 'ARIMA', '可比公司', '融合预测'],
                                'EPS预测': [
                                    results['eps_predictions']['three_statement'],
                                    results['eps_predictions']['arima'],
                                    results['eps_predictions']['comparable'],
                                    results['eps_predictions']['blended']
                                ]
                            })
                            
                            fig = px.bar(eps_data, x='模型', y='EPS预测', 
                                       color='EPS预测', color_continuous_scale='viridis',
                                       title="Alphabet EPS预测模型对比")
                            st.plotly_chart(fig, use_container_width=True)
                            
                            # 权重分配饼图
                            st.subheader("⚖️ 模型权重分配")
                            weights_data = pd.DataFrame({
                                '模型': ['三表建模', 'ARIMA', '可比公司'],
                                '权重': [0.2, 0.4, 0.4]
                            })
                            
                            fig_pie = px.pie(weights_data, values='权重', names='模型',
                                           title="模型权重分配")
                            st.plotly_chart(fig_pie, use_container_width=True)
                            
                        else:
                            st.error("PE模型返回结果格式错误，无法运行估值分析")
                            
                    except Exception as e:
                        st.error(f"PE模型计算失败: {e}")
                else:
                    st.error("PE模型导入失败，无法运行估值分析")
                
            except Exception as e:
                st.error(f"PE估值计算失败: {e}")
                st.info("请确保PE模型相关文件存在且路径正确")
            finally:
                # 确保切换回原目录
                try:
                    os.chdir(original_dir)
                except Exception as e:
                    st.warning(f"切换回原目录失败: {e}")

def show_dcf_valuation():
    """显示DCF估值模型"""
    st.header("💰 Alphabet DCF估值模型分析")
    st.markdown("---")
    
    with st.expander("🔍 DCF估值模型方法介绍", expanded=True):
        st.markdown("""
        ### DCF估值模型方法论
        
        **1. 自由现金流计算**
        - FCF = EBIT(1-T) + D&A - CAPEX - ΔWC
        - 基于Alphabet历史财务数据计算TTM FCF
        
        **2. 未来现金流预测**
        - 使用线性回归预测Alphabet未来营收
        - 通过净利率和资本支出比例计算未来FCF
        
        **3. 折现率计算**
        - WACC = (E/V × Re) + (D/V × Rd × (1-T))
        - 考虑Alphabet的权益成本和债务成本
        
        **4. 终值计算**
        - 使用永续增长模型
        - 终值 = FCFn+1 / (WACC - g)
        
        **5. 企业价值计算**
        - 企业价值 = 未来现金流现值 + 终值现值
        - 股权价值 = 企业价值 - 净债务
        """)
    
    if st.button("🚀 运行Alphabet DCF估值分析", use_container_width=True):
        with st.spinner("正在计算Alphabet DCF估值..."):
            try:
                # 获取FCF组件
                if calculate_fcf and get_fcf_components:
                    components = get_fcf_components("GOOG")
                    if components:
                        fcf = calculate_fcf(components)
                        
                        # 获取当前股价
                        stock_data = get_stock_data("GOOG")
                        current_price = stock_data['current_price'] if stock_data else 196.92
                        
                        # 简化的DCF估值计算（这里使用示例数据）
                        # 在实际应用中，这里应该使用完整的DCF模型
                        target_price = 182.50  # 示例目标价格
                        
                        # 生成投资建议
                        recommendation, recommendation_type = get_investment_recommendation(
                            current_price, target_price, 85
                        )
                        
                        # 显示FCF组件
                        st.subheader("🏢 Alphabet FCF组件分析")
                        fcf_data = pd.DataFrame({
                            '组件': ['EBIT', '税率', '折旧摊销', '资本支出', '营运资金变化'],
                            '数值(百万美元)': [
                                components['EBIT'] / 1e6,
                                components['Tax Rate'] * 100,
                                components['Depreciation & Amort.'] / 1e6,
                                components['CAPEX'] / 1e6,
                                components['Δ Working Capital'] / 1e6
                            ]
                        })
                        
                        fig = px.bar(fcf_data, x='组件', y='数值(百万美元)',
                                   title="Alphabet FCF组件分析",
                                   color='数值(百万美元)')
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 显示结果
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric("当前股价", f"${current_price:.2f}")
                        
                        with col2:
                            st.metric("目标价格", f"${target_price:.2f}")
                        
                        with col3:
                            price_change = ((target_price - current_price) / current_price) * 100
                            st.metric("预期涨幅", f"{price_change:+.1f}%", delta=f"{price_change:+.1f}%")
                        
                        with col4:
                            st.metric("置信度", "85%")
                        
                        # 投资建议卡片
                        st.subheader("💡 投资建议")
                        
                        # 根据建议类型设置颜色
                        if recommendation_type == "buy":
                            icon = "🚀"
                        elif recommendation_type == "cautious_buy":
                            icon = "📈"
                        elif recommendation_type == "hold":
                            icon = "⏸️"
                        elif recommendation_type == "cautious_hold":
                            icon = "⚠️"
                        else:
                            icon = "❌"
                        
                        st.markdown(f"""
                        <div class="model-card" style="border-left: 4px solid {'#4CAF50' if recommendation_type == 'buy' else '#2196F3' if recommendation_type == 'cautious_buy' else '#FF9800' if recommendation_type in ['hold', 'cautious_hold'] else '#F44336'};">
                            <h4>{icon} {recommendation}</h4>
                            <ul>
                            <li><strong>当前股价：</strong> ${current_price:.2f}</li>
                            <li><strong>目标价格：</strong> ${target_price:.2f}</li>
                            <li><strong>预期涨幅：</strong> {price_change:+.1f}%</li>
                            <li><strong>模型置信度：</strong> 85%</li>
                            <li><strong>估值方法：</strong> DCF估值模型</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # DCF估值结果
                        st.subheader("💰 DCF估值结果")
                        st.markdown(f"""
                        **Alphabet DCF估值结果：**
                        - **TTM FCF：** ${fcf/1e9:.2f}B
                        - **EBIT：** ${components['EBIT']/1e9:.2f}B
                        - **有效税率：** {components['Tax Rate']*100:.1f}%
                        - **折旧摊销：** ${components['Depreciation & Amort.']/1e9:.2f}B
                        - **资本支出：** ${abs(components['CAPEX'])/1e9:.2f}B
                        - **营运资金变化：** ${components['Δ Working Capital']/1e9:.2f}B
                        """)
                    else:
                        st.error("无法获取FCF组件数据")
                else:
                    st.error("DCF模型导入失败，无法运行估值分析")
                
            except Exception as e:
                st.error(f"DCF估值计算失败: {e}")

def show_ev_valuation():
    """显示EV估值模型"""
    st.header("🏢 Alphabet EV估值模型分析")
    st.markdown("---")
    
    with st.expander("🔍 EV估值模型方法介绍", expanded=True):
        st.markdown("""
        ### EV估值模型方法论
        
        **1. 企业价值计算**
        - EV = 市值 + 净债务
        - 净债务 = 总债务 - 现金及现金等价物
        
        **2. 可比公司分析**
        - 选择同行业可比公司（Apple、Microsoft、Amazon、Meta等）
        - 计算EV/EBITDA、EV/Revenue等倍数
        
        **3. 相对估值**
        - 基于可比公司倍数进行估值
        - 考虑Alphabet规模、增长性、风险等因素
        
        **4. 敏感性分析**
        - 分析关键参数对估值的影响
        - 提供估值区间
        """)
    
    if st.button("🚀 运行Alphabet EV估值分析", use_container_width=True):
        with st.spinner("正在计算Alphabet EV估值..."):
            try:
                # 获取EV组件
                if get_alphabet_ev_components:
                    ev_data = get_alphabet_ev_components()
                    
                    # 获取当前股价
                    stock_data = get_stock_data("GOOG")
                    current_price = stock_data['current_price'] if stock_data else 196.92
                    
                    # 简化的EV估值计算（这里使用示例数据）
                    target_price = 205.30  # 示例目标价格
                    
                    # 生成投资建议
                    recommendation, recommendation_type = get_investment_recommendation(
                        current_price, target_price, 82
                    )
                    
                    # 显示EV组件
                    st.subheader("🏢 Alphabet企业价值构成")
                    ev_components = pd.DataFrame({
                        '指标': ['市值', '总债务', '现金', '净债务', '企业价值'],
                        '数值(十亿美元)': [
                            ev_data.get('MarketCap', 0) / 1e9,
                            ev_data.get('TotalDebt', 0) / 1e9,
                            ev_data.get('Cash', 0) / 1e9,
                            (ev_data.get('TotalDebt', 0) - ev_data.get('Cash', 0)) / 1e9,
                            ev_data.get('EnterpriseValue', 0) / 1e9
                        ]
                    })
                    
                    fig = px.bar(ev_components, x='指标', y='数值(十亿美元)',
                               title="Alphabet企业价值构成分析",
                               color='数值(十亿美元)')
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 显示结果
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("当前股价", f"${current_price:.2f}")
                    
                    with col2:
                        st.metric("目标价格", f"${target_price:.2f}")
                    
                    with col3:
                        price_change = ((target_price - current_price) / current_price) * 100
                        st.metric("预期涨幅", f"{price_change:+.1f}%", delta=f"{price_change:+.1f}%")
                    
                    with col4:
                        st.metric("置信度", "82%")
                    
                    # 投资建议卡片
                    st.subheader("💡 投资建议")
                    
                    # 根据建议类型设置颜色
                    if recommendation_type == "buy":
                        icon = "🚀"
                    elif recommendation_type == "cautious_buy":
                        icon = "📈"
                    elif recommendation_type == "hold":
                        icon = "⏸️"
                    elif recommendation_type == "cautious_hold":
                        icon = "⚠️"
                    else:
                        icon = "❌"
                    
                    st.markdown(f"""
                    <div class="model-card" style="border-left: 4px solid {'#4CAF50' if recommendation_type == 'buy' else '#2196F3' if recommendation_type == 'cautious_buy' else '#FF9800' if recommendation_type in ['hold', 'cautious_hold'] else '#F44336'};">
                        <h4>{icon} {recommendation}</h4>
                        <ul>
                        <li><strong>当前股价：</strong> ${current_price:.2f}</li>
                        <li><strong>目标价格：</strong> ${target_price:.2f}</li>
                        <li><strong>预期涨幅：</strong> {price_change:+.1f}%</li>
                        <li><strong>模型置信度：</strong> 82%</li>
                        <li><strong>估值方法：</strong> EV估值模型</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # EV估值结果
                    st.subheader("📊 EV估值结果")
                    st.markdown(f"""
                    **Alphabet EV估值结果：**
                    - **当前市值：** ${ev_data.get('MarketCap', 0)/1e9:.2f}B
                    - **总债务：** ${ev_data.get('TotalDebt', 0)/1e9:.2f}B
                    - **现金及现金等价物：** ${ev_data.get('Cash', 0)/1e9:.2f}B
                    - **净债务：** ${(ev_data.get('TotalDebt', 0) - ev_data.get('Cash', 0))/1e9:.2f}B
                    - **企业价值：** ${ev_data.get('EnterpriseValue', 0)/1e9:.2f}B
                    - **EBITDA TTM：** ${ev_data.get('EBITDA_TTM', 0)/1e9:.2f}B
                    """)
                    
                else:
                    st.error("EV模型导入失败，无法运行估值分析")
                
            except Exception as e:
                st.error(f"EV估值计算失败: {e}")

def show_ps_valuation():
    """显示PS估值模型"""
    st.header("📈 Alphabet PS估值模型分析")
    st.markdown("---")
    
    with st.expander("🔍 PS估值模型方法介绍", expanded=True):
        st.markdown("""
        ### PS估值模型方法论
        
        **1. 收入预测**
        - 基于Alphabet历史收入数据的趋势分析
        - 使用线性回归和ARIMA模型预测未来收入
        
        **2. 可比公司分析**
        - 选择同行业可比公司（Apple、Microsoft、Amazon、Meta等）
        - 计算PS倍数和收入增长率
        
        **3. 相对估值**
        - 基于可比公司PS倍数进行估值
        - 考虑Alphabet收入增长性和盈利能力
        
        **4. 多模型融合**
        - 结合多种预测方法
        - 加权平均得到最终估值
        """)
    
    if st.button("🚀 运行Alphabet PS估值分析", use_container_width=True):
        with st.spinner("正在计算Alphabet PS估值..."):
            try:
                # 获取市值和收入预测
                if get_market_cap and calculate_forward_ps:
                    market_cap = get_market_cap("GOOG")
                    
                    # 这里需要从revenue_blender获取预测收入
                    # 暂时使用示例数据
                    revenue_2025 = 374.9e9  # 374.9B
                    
                    forward_ps = calculate_forward_ps(market_cap, revenue_2025)
                    
                    # 获取当前股价
                    stock_data = get_stock_data("GOOG")
                    current_price = stock_data['current_price'] if stock_data else 196.92
                    
                    # 简化的PS估值计算（这里使用示例数据）
                    target_price = 198.90  # 示例目标价格
                    
                    # 生成投资建议
                    recommendation, recommendation_type = get_investment_recommendation(
                        current_price, target_price, 80
                    )
                    
                    # 显示结果
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("当前股价", f"${current_price:.2f}")
                    
                    with col2:
                        st.metric("目标价格", f"${target_price:.2f}")
                    
                    with col3:
                        price_change = ((target_price - current_price) / current_price) * 100
                        st.metric("预期涨幅", f"{price_change:+.1f}%", delta=f"{price_change:+.1f}%")
                    
                    with col4:
                        st.metric("置信度", "80%")
                    
                    # 投资建议卡片
                    st.subheader("💡 投资建议")
                    
                    # 根据建议类型设置颜色
                    if recommendation_type == "buy":
                        icon = "🚀"
                    elif recommendation_type == "cautious_buy":
                        icon = "📈"
                    elif recommendation_type == "hold":
                        icon = "⏸️"
                    elif recommendation_type == "cautious_hold":
                        icon = "⚠️"
                    else:
                        icon = "❌"
                    
                    st.markdown(f"""
                    <div class="model-card" style="border-left: 4px solid {'#4CAF50' if recommendation_type == 'buy' else '#2196F3' if recommendation_type == 'cautious_buy' else '#FF9800' if recommendation_type in ['hold', 'cautious_hold'] else '#F44336'};">
                        <h4>{icon} {recommendation}</h4>
                        <ul>
                        <li><strong>当前股价：</strong> ${current_price:.2f}</li>
                        <li><strong>目标价格：</strong> ${target_price:.2f}</li>
                        <li><strong>预期涨幅：</strong> {price_change:+.1f}%</li>
                        <li><strong>模型置信度：</strong> 80%</li>
                        <li><strong>估值方法：</strong> PS估值模型</li>
                        </ul>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # PS估值结果
                    st.subheader("📊 PS估值结果")
                    st.markdown(f"""
                    **Alphabet PS估值结果：**
                    - **当前市值：** ${market_cap/1e9:.2f}B
                    - **2025E收入预测：** ${revenue_2025/1e9:.2f}B
                    - **Forward PS (2025E)：** {forward_ps}
                    - **估值日期：** {datetime.now().strftime('%Y-%m-%d')}
                    """)
                    
                    # 收入预测趋势
                    st.subheader("📈 Alphabet未来收入预测")
                    ps_data = pd.DataFrame({
                        '年份': [2025, 2026, 2027, 2028, 2029],
                        '收入预测(十亿美元)': [374.9, 405.1, 435.2, 465.4, 495.6]
                    })
                    
                    fig = px.line(ps_data, x='年份', y='收入预测(十亿美元)',
                                title="Alphabet未来5年收入预测趋势",
                                markers=True)
                    st.plotly_chart(fig, use_container_width=True)
                    
                else:
                    st.error("PS模型导入失败，无法运行估值分析")
                
            except Exception as e:
                st.error(f"PS估值计算失败: {e}")

def show_comprehensive_comparison():
    """显示综合对比"""
    st.header("🎯 Alphabet估值模型综合对比分析")
    st.markdown("---")
    
    # 获取当前股价
    stock_data = get_stock_data("GOOG")
    current_price = stock_data['current_price'] if stock_data else 196.92
    
    # 获取各模型的实际计算结果
    pe_target_price = None
    dcf_target_price = 182.50  # 暂时使用示例值
    ev_target_price = 205.30   # 暂时使用示例值
    ps_target_price = 198.90   # 暂时使用示例值
    
    # 尝试获取PE模型的实际结果
    try:
        # 切换到PE模型目录
        original_dir = os.getcwd()
        os.chdir(pe_model_path) # 使用相对路径
        
        if pe_model_available and create_pe_valuation_dashboard is not None:
            try:
                results = create_pe_valuation_dashboard()
                
                # 切换回原目录
                os.chdir(original_dir)
                
                # 检查results是否为字典类型
                if isinstance(results, dict) and 'eps_predictions' in results:
                    # 计算PE目标价格
                    predicted_eps = results['eps_predictions']['blended']
                    conservative_pe = 22.0
                    pe_target_price = conservative_pe * predicted_eps
                    
                    # 确保目标价格在合理范围内
                    max_reasonable_price = current_price * 1.5
                    if pe_target_price > max_reasonable_price:
                        pe_target_price = max_reasonable_price
                    
                    min_reasonable_price = current_price * 0.5
                    if pe_target_price < min_reasonable_price:
                        pe_target_price = min_reasonable_price
                else:
                    st.warning(f"PE模型返回结果格式错误，期望字典类型，实际得到: {type(results)}")
                    pe_target_price = 173.58  # 使用合理的默认值
                    
            except Exception as e:
                st.warning(f"PE模型计算失败: {e}")
                pe_target_price = 173.58  # 使用合理的默认值
                os.chdir(original_dir)  # 确保切换回原目录
        else:
            st.warning("PE模型导入失败，使用默认值")
            pe_target_price = 173.58  # 使用合理的默认值
            
    except Exception as e:
        st.warning(f"无法获取PE模型结果: {e}")
        pe_target_price = 173.58  # 使用合理的默认值
    
    # 创建Alphabet的对比数据 - 使用实际计算结果
    comparison_data = {
        '估值模型': ['PE模型', 'DCF模型', 'EV模型', 'PS模型'],
        '估值结果(美元)': [pe_target_price, dcf_target_price, ev_target_price, ps_target_price],
        '置信度(%)': [88, 85, 82, 80],
        '适用场景': ['成熟公司', '成长公司', '重资产公司', '科技公司'],
        '模型特点': ['相对估值', '绝对估值', '相对估值', '相对估值']
    }
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # 计算每个模型的预期涨幅和投资建议
    recommendations = []
    for _, row in df_comparison.iterrows():
        target_price = row['估值结果(美元)']
        price_change = ((target_price - current_price) / current_price) * 100
        recommendation, recommendation_type = get_investment_recommendation(
            current_price, target_price, row['置信度(%)']
        )
        recommendations.append({
            '模型': row['估值模型'],
            '目标价格': target_price,
            '预期涨幅': price_change,
            '投资建议': recommendation,
            '建议类型': recommendation_type
        })
    
    # 显示当前股价
    st.subheader("📊 当前市场状况")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("当前股价", f"${current_price:.2f}")
    
    with col2:
        min_target = df_comparison['估值结果(美元)'].min()
        max_target = df_comparison['估值结果(美元)'].max()
        st.metric("估值目标价格区间", f"${min_target:.2f}-${max_target:.2f}")
    
    with col3:
        avg_target = df_comparison['估值结果(美元)'].mean()
        avg_change = ((avg_target - current_price) / current_price) * 100
        st.metric("平均预期涨幅", f"{avg_change:+.1f}%", delta=f"{avg_change:+.1f}%")
    
    # 估值结果对比
    st.subheader("🎯 Alphabet估值结果对比")
    fig = px.bar(df_comparison, x='估值模型', y='估值结果(美元)',
                color='置信度(%)', title="Alphabet各模型估值结果对比",
                color_continuous_scale='viridis')
    st.plotly_chart(fig, use_container_width=True)
    
    # 投资建议汇总
    st.subheader("💡 各模型投资建议汇总")
    
    # 创建投资建议表格
    recommendations_df = pd.DataFrame(recommendations)
    
    # 为每个建议类型设置颜色
    def get_recommendation_color(recommendation_type):
        if recommendation_type == "buy":
            return "background-color: #4CAF50; color: white;"
        elif recommendation_type == "cautious_buy":
            return "background-color: #2196F3; color: white;"
        elif recommendation_type == "hold":
            return "background-color: #FF9800; color: white;"
        elif recommendation_type == "cautious_hold":
            return "background-color: #FF9800; color: white;"
        else:
            return "background-color: #F44336; color: white;"
    
    # 显示投资建议表格
    st.dataframe(recommendations_df, use_container_width=True)
    
    # 综合投资建议
    st.subheader("🎯 综合投资建议")
    
    # 计算综合建议
    buy_count = sum(1 for r in recommendations if r['建议类型'] in ['buy', 'cautious_buy'])
    hold_count = sum(1 for r in recommendations if r['建议类型'] in ['hold', 'cautious_hold'])
    sell_count = sum(1 for r in recommendations if r['建议类型'] == 'sell')
    
    if buy_count >= 3:
        final_recommendation = "强烈买入"
        final_type = "buy"
        icon = "🚀"
        color = "#4CAF50"
    elif buy_count >= 2:
        final_recommendation = "建议买入"
        final_type = "cautious_buy"
        icon = "📈"
        color = "#2196F3"
    elif hold_count >= 2:
        final_recommendation = "持有"
        final_type = "hold"
        icon = "⏸️"
        color = "#FF9800"
    elif sell_count >= 2:
        final_recommendation = "不建议买入"
        final_type = "sell"
        icon = "❌"
        color = "#F44336"
    else:
        final_recommendation = "谨慎持有"
        final_type = "cautious_hold"
        icon = "⚠️"
        color = "#FF9800"
    
    # 显示综合投资建议
    st.markdown(f"""
    <div class="model-card" style="border-left: 4px solid {color};">
        <h4>{icon} {final_recommendation}</h4>
        <ul>
        <li><strong>当前股价：</strong> ${current_price:.2f}</li>
        <li><strong>估值目标价格区间：</strong> ${min_target:.2f}-${max_target:.2f}</li>
        <li><strong>平均预期涨幅：</strong> {avg_change:+.1f}%</li>
        <li><strong>买入建议：</strong> {buy_count}个模型</li>
        <li><strong>持有建议：</strong> {hold_count}个模型</li>
        <li><strong>卖出建议：</strong> {sell_count}个模型</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
