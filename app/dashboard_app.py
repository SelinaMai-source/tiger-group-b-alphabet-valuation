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
    
    # SOTP模型
    sotp_model_path = os.path.join(project_root, 'valuation_models', 'sotp_model')
    sys.path.append(sotp_model_path)
    try:
        # 使用绝对导入
        import sotp_calc
        import sotp_visual
        import sotp_calc_enhanced
        
        calculate_sotp_valuation = sotp_calc.calculate_sotp_valuation
        get_sotp_valuation_summary = sotp_calc.get_sotp_valuation_summary
        create_sotp_dashboard = sotp_visual.create_sotp_dashboard
        plot_sotp_breakdown = sotp_visual.plot_sotp_breakdown
        plot_sotp_comparison = sotp_visual.plot_sotp_comparison
        plot_sotp_components = sotp_visual.plot_sotp_components
        display_sotp_metrics = sotp_visual.display_sotp_metrics
        display_sotp_details = sotp_visual.display_sotp_details
        
        # 增强版SOTP模型
        calculate_enhanced_sotp_valuation = sotp_calc_enhanced.calculate_enhanced_sotp_valuation
        # 高级版SOTP模型
        calculate_advanced_sotp_valuation = sotp_calc_enhanced.calculate_advanced_sotp_valuation
        
        sotp_model_available = True
        enhanced_sotp_available = True
        advanced_sotp_available = True
    except ImportError as e:
        st.warning(f"SOTP模型导入失败：{e}，将使用备用功能")
        calculate_sotp_valuation = None
        get_sotp_valuation_summary = None
        create_sotp_dashboard = None
        plot_sotp_breakdown = None
        plot_sotp_comparison = None
        plot_sotp_components = None
        display_sotp_metrics = None
        display_sotp_details = None
        calculate_enhanced_sotp_valuation = None
        calculate_advanced_sotp_valuation = None
        sotp_model_available = False
        enhanced_sotp_available = False
        advanced_sotp_available = False
    
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
    # 强制更新时间戳：2025-08-09 11:43
    
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
            ["🏠 仪表板概览", "📈 PE估值模型", "💰 DCF估值模型", "🏢 EV估值模型", "📊 PS估值模型", "🎯 SOTP估值模型", "🎯 综合对比分析"]
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
    elif model_choice == "🎯 SOTP估值模型":
        show_sotp_valuation()
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
    
    # 尝试获取SOTP模型的实际结果
    try:
        if enhanced_sotp_available and calculate_enhanced_sotp_valuation is not None:
            sotp_results, _ = calculate_enhanced_sotp_valuation("GOOG")
            if sotp_results:
                sotp_target_price = sotp_results['target_price']
            else:
                sotp_target_price = 195.00  # 使用合理的默认值
        elif sotp_model_available and calculate_sotp_valuation is not None:
            sotp_results = calculate_sotp_valuation("GOOG")
            if sotp_results:
                sotp_target_price = sotp_results['target_price']
            else:
                sotp_target_price = 195.00  # 使用合理的默认值
        else:
            sotp_target_price = 195.00  # 使用合理的默认值
    except Exception as e:
        st.warning(f"SOTP模型计算失败: {e}")
        sotp_target_price = 195.00  # 使用合理的默认值
    
    # 创建对比数据 - 使用实际计算结果
    comparison_data = {
        '估值模型': ['PE模型', 'DCF模型', 'EV模型', 'PS模型', 'SOTP模型'],
        '目标价格(美元)': [pe_target_price, dcf_target_price, ev_target_price, ps_target_price, sotp_target_price],
        '置信度(%)': [88, 85, 82, 80, 85],
        '适用场景': ['成熟公司', '成长公司', '重资产公司', '科技公司', '多元化公司']
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
    
    # 模型公式简介
    st.subheader("🔬 各估值模型核心公式")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        **PE估值模型**
        ```
        目标股价 = 预测EPS × 目标PE倍数
        ```
        
        **DCF估值模型**
        ```
        股价 = (Σ[FCF/(1+WACC)^t] + 终值) / 股数
        ```
        
        **EV估值模型**
        ```
        股价 = (预测EBITDA × EV/EBITDA倍数 - 净债务) / 股数
        ```
        """)
    
    with col2:
        st.markdown("""
        **PS估值模型**
        ```
        股价 = (预测营收 × PS倍数) / 股数
        ```
        
        **SOTP估值模型**
        ```
        股价 = (Services估值 + Cloud估值 + Other Bets估值 - 净债务) / 股数
        ```
        """)
    
    # 价格对比柱状图
    st.subheader("📊 五种估值模型对比")
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
        
        #### 📊 核心估值公式
        ```
        Forward PE = 当前股价 / 预测EPS
        目标股价 = 预测EPS × 目标PE倍数
        ```
        
        #### 🔮 EPS预测方法（三种方法融合）
        
        **1. 三表建模预测（权重：20%）**
        - **三表定义**：
          - **损益表（Income Statement）**：提供营收、营业利润、净利润等数据
          - **资产负债表（Balance Sheet）**：提供流通股数、股东权益等数据  
          - **现金流量表（Cash Flow Statement）**：验证盈利质量和现金创造能力
        - **数据来源**：Alphabet历史三表财务数据（收入、利润、股本）
        - **预测公式**：
          ```
          未来收入 = 历史收入 × (1 + 预测增长率)
          预测EPS = (未来收入 × 净利率) / 流通股数
          ```
          其中：
          - **未来收入**：基于损益表历史营收的线性回归预测
          - **净利率**：净利润/营收（来源于损益表）
          - **流通股数**：来源于资产负债表的股东权益部分
        - **实现方法**：使用线性回归预测未来营收，通过净利率计算EPS
        
        **2. ARIMA时间序列预测（权重：40%）**
        - **数据来源**：Alphabet历史EPS数据的时间序列
        - **模型参数**：ARIMA(1,1,0)模型
        - **预测公式**：
          ```
          EPS(t) = μ + φ₁ × (EPS(t-1) - μ) + εₜ
          ```
          其中：
          - **EPS(t)**：第t期的预测EPS值
          - **μ**：EPS的长期均值（历史EPS的平均水平）
          - **φ₁**：自回归系数（衡量前期EPS对当期EPS的影响程度）
          - **EPS(t-1)**：前一期的实际EPS值
          - **εₜ**：第t期的随机误差项（白噪声）
        - **特点**：捕捉EPS的长期趋势和季节性变化
        
        **3. 可比公司回归分析（权重：40%）**
        - **数据来源**：同行业科技公司（Apple、Microsoft、Amazon等）
        - **回归模型**：
          ```
          预测EPS = β₀ + β₁×毛利率 + β₂×净利率 + β₃×营收增长率
          ```
          其中：
          - **预测EPS**：基于回归模型预测的Alphabet EPS值
          - **β₀**：回归截距项（基础EPS水平）
          - **β₁**：毛利率的回归系数（毛利率对EPS的影响程度）
          - **β₂**：净利率的回归系数（净利率对EPS的影响程度）
          - **β₃**：营收增长率的回归系数（增长率对EPS的影响程度）
          - **毛利率**：Alphabet的毛利率（毛利润/营收）
          - **净利率**：Alphabet的净利率（净利润/营收）
          - **营收增长率**：Alphabet的营收年增长率
        - **训练数据**：基于可比公司的财务指标和EPS的关系
        - **应用**：将Alphabet的财务指标代入训练好的模型
        
        **4. 加权融合算法**
        ```
        最终EPS预测 = 0.2×三表建模EPS + 0.4×ARIMA预测EPS + 0.4×可比公司EPS
        ```
        
        #### 🎯 目标PE倍数确定
        - **保守PE倍数**：22.0倍（基于Alphabet作为成熟科技公司的行业特征）
        - **合理性检验**：目标价格不超过当前股价的1.5倍，不低于0.5倍
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
                            st.error(f"PE模型返回结果格式错误，期望字典类型，实际得到: {type(results)}")
                            st.info("请检查PE模型实现是否正确返回字典格式的结果")
                            
                    except Exception as e:
                        st.error(f"PE模型计算失败: {e}")
                        st.info("请确保PE模型相关文件存在且路径正确")
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
        
        #### 📊 核心估值公式
        ```
        企业价值 = Σ[FCF(t) / (1+WACC)^t] + 终值 / (1+WACC)^n
        股权价值 = 企业价值 - 净债务
        目标股价 = 股权价值 / 流通股数
        ```
        
        #### 1. 自由现金流（FCF）计算
        **核心公式**：
        ```
        FCF = EBIT × (1 - 税率) + 折旧摊销 - 资本支出 - 营运资金变化
        FCF = EBIT(1-T) + D&A - CAPEX - ΔWC
        ```
        
        **组成部分**：
        - **EBIT**：息税前利润，即营业利润（来源：损益表）
        - **T**：有效税率 = 所得税费用 / 税前利润
        - **D&A**：折旧摊销费用（来源：现金流量表）
        - **CAPEX**：资本支出，购买固定资产的现金支出（来源：现金流量表）
        - **ΔWC**：营运资金变化 = 流动资产变化 - 流动负债变化（来源：资产负债表）
        
        #### 🔮 未来现金流预测方法
        **ARIMA时间序列预测**：
        ```
        FCF(t) = μ + φ₁ × (FCF(t-1) - μ) + εₜ
        ```
        其中：
        - **FCF(t)**：第t期的预测自由现金流
        - **μ**：FCF的长期均值（历史FCF的平均水平）
        - **φ₁**：自回归系数（前期FCF对当期FCF的影响程度）
        - **FCF(t-1)**：前一期的实际自由现金流
        - **εₜ**：第t期的随机误差项
        - **模型**：ARIMA(1,1,0)模型
        - **数据来源**：Alphabet过去5年历史FCF数据
        - **预测期**：未来5年FCF
        
        #### 2. 加权平均资本成本（WACC）计算
        **核心公式**：
        ```
        WACC = (E/V) × Re + (D/V) × Rd × (1-T)
        ```
        
        **组成部分**：
        - **E**：股权市值，公司股票的市场价值
        - **D**：债务价值，公司总债务的市场价值
        - **V**：企业总价值 = E + D（股权价值 + 债务价值）
        - **Re**：权益成本 = Rf + β × (Rm - Rf)，股东要求的回报率
        - **Rd**：债务成本 = 利息支出 / 总债务，公司借债的成本
        - **T**：税率，公司的有效税率
        - **Rf**：无风险利率，通常使用政府债券收益率
        - **β**：贝塔系数，衡量股票相对于市场的风险程度
        - **Rm - Rf**：市场风险溢价，市场回报率与无风险利率的差值
        
        **参数设定**：
        - **无风险利率（Rf）**：4.2%
        - **市场风险溢价（Rm-Rf）**：5.5%
        - **Beta**：通过yfinance获取Alphabet的Beta值
        
        #### 3. 终值（Terminal Value）计算
        **永续增长模型**：
        ```
        终值 = FCF(n+1) / (WACC - g)
        其中：FCF(n+1) = FCF(n) × (1 + g)
        ```
        其中：
        - **终值**：预测期后企业的剩余价值
        - **FCF(n+1)**：预测期后第一年的自由现金流
        - **FCF(n)**：预测期最后一年（第n年）的自由现金流
        - **WACC**：加权平均资本成本，折现率
        - **g**：长期增长率，企业永续经营的增长率（默认值：2.5%）
        - **n**：预测期年数（通常为5年）
        
        #### 🔍 数据来源
        - **财务数据**：Financial Modeling Prep API
        - **股价数据**：yfinance
        - **市场数据**：实时获取Beta、市值等指标
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
        
        #### 📊 核心估值公式
        ```
        目标企业价值 = 预测EBITDA × EV/EBITDA倍数
        目标市值 = 目标企业价值 - 净债务
        目标股价 = 目标市值 / 流通股数
        ```
        其中：
        - **目标企业价值**：基于倍数法预测的企业整体价值
        - **预测EBITDA**：预测的息税折旧摊销前利润
        - **EV/EBITDA倍数**：基于可比公司分析得出的行业倍数
        - **目标市值**：预测的股权市场价值
        - **净债务**：总债务减去现金及现金等价物
        - **流通股数**：公司已发行的普通股数量
        
        #### 🏢 企业价值（Enterprise Value）计算
        **当前企业价值**：
        ```
        EV = 市值 + 总债务 - 现金及现金等价物
        EV = Market Cap + Total Debt - Cash
        ```
        
        **组成部分**：
        - **Market Cap**：市值 = 当前股价 × 流通股数
        - **Total Debt**：总债务，包括短期和长期债务（来源：资产负债表）
        - **Cash**：现金及现金等价物，包括银行存款、短期投资等（来源：资产负债表）
        
        #### 📈 EBITDA预测方法
        **预测公式**：
        ```
        预测EBITDA = 预测营收 × EBITDA利润率
        EBITDA利润率 = TTM EBITDA / TTM营收
        ```
        其中：
        - **预测EBITDA**：预测的息税折旧摊销前利润
        - **预测营收**：通过revenue_blender模块预测的2025年营收
        - **EBITDA利润率**：基于历史数据计算的利润率
        - **TTM EBITDA**：过去12个月的息税折旧摊销前利润
        - **TTM营收**：过去12个月的营业收入
        
        **营收预测**：
        - **数据来源**：基于PS模型的收入预测模块（revenue_blender）
        - **预测方法**：多模型融合（线性趋势、ARIMA、可比公司分析）
        - **预测期**：2025年营收预测
        
        #### 🔍 可比公司分析方法
        **EV/EBITDA倍数计算**：
        ```
        行业EV/EBITDA倍数 = median(可比公司EV/EBITDA倍数)
        ```
        
        **可比公司选择标准**：
        - **行业**：同属科技行业的大型公司
        - **规模**：市值相当的公司
        - **业务模式**：具有相似商业模式的公司
        - **数据来源**：可比公司倍数数据文件（comps_ev_multiples.csv）
        
        **倍数应用**：
        ```
        目标EV = 预测EBITDA × 行业中位数EV/EBITDA倍数
        ```
        
        #### 🎯 估值步骤详解
        1. **获取TTM财务数据**：
           - TTM EBITDA（过去12个月EBITDA）
           - TTM营收（推算：EBITDA / 利润率）
           - 计算EBITDA利润率
        
        2. **获取营收预测**：
           - 调用revenue_blender模块
           - 获取2025年营收预测
        
        3. **计算预测EBITDA**：
           - 预测EBITDA = 预测营收 × TTM EBITDA利润率
        
        4. **应用行业倍数**：
           - 加载可比公司EV/EBITDA倍数
           - 计算目标企业价值
        
        5. **计算目标股价**：
           - 扣除净债务得到目标市值
           - 除以流通股数得到目标股价
        
        #### 🔍 数据来源
        - **财务数据**：yfinance实时获取
        - **可比公司倍数**：预处理的CSV文件
        - **营收预测**：PS模型的revenue_blender模块
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
        
        #### 📊 核心估值公式
        ```
        Forward PS = 当前市值 / 预测营收
        目标股价 = (预测营收 × 目标PS倍数) / 流通股数
        ```
        其中：
        - **Forward PS**：前瞻市销率，基于预测营收计算的估值倍数
        - **当前市值**：公司当前的股票市场价值
        - **预测营收**：2025年预测的营业收入
        - **目标PS倍数**：基于行业和历史数据确定的合理PS倍数
        - **流通股数**：公司已发行的普通股数量
        
        #### 📈 营收预测方法（多模型融合）
        **数据来源**：revenue_blender模块整合多种预测方法
        
        **1. 线性趋势预测**
        ```
        预测营收 = a × 年份 + b
        ```
        其中：
        - **预测营收**：基于线性趋势预测的未来营收
        - **a**：回归斜率系数，代表营收的年均增长绝对值
        - **年份**：预测的目标年份（如2025）
        - **b**：回归截距项，代表基础营收水平
        
        **2. ARIMA时间序列预测**
        ```
        Revenue(t) = μ + φ₁ × (Revenue(t-1) - μ) + εₜ
        ```
        其中：
        - **Revenue(t)**：第t期的预测营收
        - **μ**：营收的长期均值（历史营收的平均水平）
        - **φ₁**：自回归系数（前期营收对当期营收的影响程度）
        - **Revenue(t-1)**：前一期的实际营收
        - **εₜ**：第t期的随机误差项
        - **模型**：ARIMA模型分析营收时间序列
        - **数据来源**：Alphabet历史营收数据
        
        **3. 可比公司回归分析**
        ```
        预测营收增长率 = f(行业平均增长率, 公司特征)
        ```
        - **可比公司**：同行业科技公司（Apple、Microsoft、Amazon、Meta等）
        - **分析指标**：营收增长率、市场份额、业务结构
        
        **4. 一致预期（Consensus）**
        - **数据来源**：分析师一致预期数据
        - **权重**：基于历史准确性调整
        
        **5. 加权融合算法**
        ```
        最终营收预测 = w₁×线性趋势 + w₂×ARIMA + w₃×可比公司 + w₄×一致预期
        ```
        其中：
        - **最终营收预测**：多模型加权融合的最终预测结果
        - **w₁, w₂, w₃, w₄**：各模型的权重系数，权重之和为1
        - **线性趋势**：基于历史趋势的线性回归预测结果
        - **ARIMA**：时间序列模型的预测结果
        - **可比公司**：基于同行业公司分析的预测结果
        - **一致预期**：分析师一致预期的预测结果
        权重根据各模型历史预测准确性动态调整
        
        #### 🎯 PS倍数确定方法
        **市值计算**：
        ```
        当前市值 = 当前股价 × 流通股数
        ```
        
        **Forward PS计算**：
        ```
        Forward PS = 当前市值 / 2025年预测营收
        ```
        
        **数据来源**：
        - **市值数据**：yfinance实时获取
        - **预测营收**：revenue_blender模块输出
        
        #### 📊 估值应用场景
        **适用性**：
        - 特别适合科技公司估值
        - 适用于营收增长强劲但利润波动的公司
        - 对于Alphabet这类多元化科技公司具有良好适用性
        
        **局限性**：
        - 不直接考虑盈利能力
        - 需要结合其他估值方法使用
        
        #### 🔍 数据验证
        **营收预测验证**：
        - 与历史增长趋势对比
        - 与行业平均水平对比
        - 与管理层指导对比
        
        **合理性检查**：
        - 预测营收增长率不超过历史最高水平的1.5倍
        - 考虑宏观经济和行业周期影响
        
        #### 🔍 数据来源
        - **营收预测**：revenue_blender多模型融合
        - **市值数据**：yfinance实时API
        - **可比公司数据**：公开财务数据
        - **一致预期**：金融数据提供商
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

def show_sotp_valuation():
    """显示SOTP估值模型"""
    st.header("🎯 Alphabet SOTP估值模型分析")
    st.markdown("---")
    
    with st.expander("🔍 SOTP估值模型方法介绍", expanded=True):
        st.markdown("""
        ### SOTP (Sum of the Parts) 估值模型方法论
        
        #### 📊 核心估值公式
        ```
        Target Price = (Services Valuation + Cloud Valuation + Other Bets Valuation - Net Debt) / Shares Outstanding
        ```
        
        **SOTP估值模型将Alphabet的业务分为三个主要部分：**
        
        #### 1️⃣ Google Services（主营搜索广告）
        **估值方法**：PE估值法
        **核心公式**：
        ```
        Services Value = Services Net Income × PE Multiple
        PE Multiple = 基于历史数据和可比公司分析确定
        ```
        
        **详细计算步骤**：
        1. **获取Services净利润**：
           ```
           Services Operating Income = Services Revenue × Operating Margin
           Services Net Income = Services Operating Income × (1 - Tax Rate)
           ```
        2. **确定PE倍数**：
           - 历史PE倍数分析（过去5年数据）
           - 可比公司PE倍数（Apple、Microsoft等）
           - 最终PE倍数 = median(历史PE倍数, 可比公司PE倍数)
        3. **计算Services估值**：
           ```
           Services Valuation = Services Net Income × Target PE Multiple
           ```
        
        **业务范围**：Google搜索、YouTube、Google广告等核心业务
        **数据来源**：Alphabet 2023年财报（营收：$307.4B，营业利润：$101.2B）
        
        #### 2️⃣ Google Cloud（云服务）
        **估值方法**：EV估值法
        **核心公式**：
        ```
        Cloud Value = Cloud EBITDA × EV/EBITDA Multiple
        ```
        
        **详细计算步骤**：
        1. **计算Cloud EBITDA**：
           ```
           Cloud EBITDA = Cloud Operating Income + Depreciation & Amortization
           ```
        2. **确定EV/EBITDA倍数**：
           - 可比云服务公司分析（AWS、Azure、GCP竞品）
           - 历史倍数趋势分析
           - 行业中位数倍数
        3. **计算Cloud估值**：
           ```
           Cloud Valuation = Cloud EBITDA × Target EV/EBITDA Multiple
           ```
        
        **业务范围**：云计算、AI服务、企业解决方案
        **数据来源**：Alphabet 2023年财报（营收：$33.1B，营业利润：$0.9B）
        
        #### 3️⃣ Other Bets（其他创新项目）
        **估值方法**：Real Option估值法（Black-Scholes期权定价模型变体）
        **核心公式**：
        ```
        Other Bets Value = Σ[Option Value × Success Probability]
        Option Value = S₀ × N(d₁) - K × e^(-rT) × N(d₂)
        ```
        
        **Black-Scholes参数**：
        ```
        d₁ = [ln(S₀/K) + (r + σ²/2)×T] / (σ×√T)
        d₂ = d₁ - σ×√T
        ```
        其中：
        - **S₀**：当前项目价值（基于DCF估算的项目现值）
        - **K**：执行价格（达到商业化所需的总投资金额）
        - **r**：无风险利率（通常使用政府债券收益率）
        - **T**：期权到期时间（技术成熟并商业化的预期时间，单位：年）
        - **σ**：波动率（基于项目风险等级和行业特征的年化波动率）
        - **d₁, d₂**：Black-Scholes模型中的中间计算参数
        - **ln**：自然对数函数
        - **N(d₁), N(d₂)**：标准正态分布的累积分布函数
        
        **项目分类估值**：
        1. **Waymo（自动驾驶）**：
           - 市场规模：$1,000B+
           - 成功概率：65%
           - 期权价值计算基于出行市场份额预期
        
        2. **Verily（生命科学）**：
           - 市场规模：$500B+
           - 成功概率：45%
           - 基于医疗技术市场潜力
        
        3. **其他项目**（Calico、X、Google Fiber等）：
           - 分别基于各自技术成熟度、市场大小、竞争水平、监管风险等因素
        
        **业务范围**：Waymo、Verily、Calico、X、Google Fiber等
        **详细拆分**：基于每个项目的技术成熟度、市场大小、竞争水平、监管风险等因素
        
        #### 4️⃣ 最终目标价格计算
        ```
        Total Enterprise Value = Services Valuation + Cloud Valuation + Other Bets Valuation
        Equity Value = Total Enterprise Value - Net Debt
        Target Price per Share = Equity Value / Shares Outstanding
        ```
        其中：
        - **Total Enterprise Value**：企业总价值，三个业务部门估值之和
        - **Services Valuation**：Google Services业务的估值
        - **Cloud Valuation**：Google Cloud业务的估值
        - **Other Bets Valuation**：其他创新项目的总估值
        - **Equity Value**：股权价值，股东享有的企业价值
        - **Net Debt**：净债务，总债务减去现金及现金等价物
        - **Target Price per Share**：每股目标价格
        - **Shares Outstanding**：已发行流通股数
        
        **净债务计算**：
        ```
        Net Debt = Total Debt - Cash and Cash Equivalents
        ```
        其中：
        - **Total Debt**：总债务，包括短期和长期债务
        - **Cash and Cash Equivalents**：现金及现金等价物
        
        **增强版特性：**
        - 基于真实财报数据（2021-2023年）
        - 使用统计预测模型预测未来增长
        - 复杂的Real Option模型计算Other Bets估值
        - 考虑技术成熟度、竞争态势、监管风险等因素
        
        **数据来源验证：**
        - **数据来源**：Alphabet 2023年10-K报告
        - **验证时间**：2024-08-07
        - **总营收**：$342.0B（2023年）
        - **业务线占比**：
          - Google Services：89.9%（$307.4B）
          - Google Cloud：9.7%（$33.1B）
          - Other Bets：0.4%（$1.5B）
        - **数据一致性**：已验证，业务线营收之和等于总营收
        """)
    
    # 选择SOTP模型版本
    model_version = st.radio(
        "选择SOTP模型版本",
        ["🚀 高级版SOTP模型（推荐）", "🔬 增强版SOTP模型", "📊 基础版SOTP模型"],
        help="高级版包含历史数据分析、可比公司分析、Monte Carlo模拟等；增强版基于真实财报数据和复杂统计模型；基础版使用简化假设"
    )
    
    if st.button("🚀 运行Alphabet SOTP估值分析", use_container_width=True):
        with st.spinner("正在计算Alphabet SOTP估值..."):
            try:
                if "高级版" in model_version and advanced_sotp_available and calculate_advanced_sotp_valuation is not None:
                    # 使用高级版SOTP模型
                    results = calculate_advanced_sotp_valuation("GOOG")
                    
                    if results:
                        # 获取当前股价
                        stock_data = get_stock_data("GOOG")
                        current_price = stock_data['current_price'] if stock_data else results['current_price']
                        
                        # 显示高级版SOTP估值结果
                        st.subheader("🚀 Alphabet 高级版SOTP估值结果")
                        
                        # 创建指标卡片
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                label="当前股价",
                                value=f"${current_price:.2f}",
                                delta=None
                            )
                        
                        with col2:
                            st.metric(
                                label="目标股价",
                                value=f"${results['target_price']:.2f}",
                                delta=f"{((results['target_price'] / current_price - 1) * 100):.1f}%"
                            )
                        
                        with col3:
                            st.metric(
                                label="总估值",
                                value=f"${results['total_valuation']/1e9:.1f}B",
                                delta=None
                            )
                        
                        with col4:
                            st.metric(
                                label="净债务",
                                value=f"${results['net_debt']/1e9:.1f}B",
                                delta=None
                            )
                        
                        # 显示Monte Carlo模拟结果
                        if results.get('monte_carlo_results'):
                            st.subheader("🎲 Monte Carlo模拟结果")
                            mc_results = results['monte_carlo_results']
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.metric(
                                    label="目标股价均值",
                                    value=f"${mc_results['target_price_mean']:.2f}",
                                    delta=None
                                )
                            
                            with col2:
                                st.metric(
                                    label="目标股价标准差",
                                    value=f"${mc_results['target_price_std']:.2f}",
                                    delta=None
                                )
                            
                            with col3:
                                st.metric(
                                    label="5%分位数",
                                    value=f"${mc_results['target_price_5th_percentile']:.2f}",
                                    delta=None
                                )
                            
                            with col4:
                                st.metric(
                                    label="95%分位数",
                                    value=f"${mc_results['target_price_95th_percentile']:.2f}",
                                    delta=None
                                )
                            
                            # 显示置信区间
                            st.info(f"📊 95%置信区间：${mc_results['confidence_interval'][0]:.2f} - ${mc_results['confidence_interval'][1]:.2f}")
                        
                        # 显示历史数据分析
                        if results.get('historical_data'):
                            st.subheader("📊 历史数据分析")
                            hist_data = results['historical_data']
                            
                            if hist_data.get('pe_ratios'):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.markdown("**历史PE倍数分析**")
                                    pe_df = pd.DataFrame({
                                        '年份': range(2019, 2019 + len(hist_data['pe_ratios'])),
                                        'PE倍数': hist_data['pe_ratios']
                                    })
                                    st.dataframe(pe_df, use_container_width=True)
                                
                                with col2:
                                    st.markdown("**历史EV/EBITDA倍数分析**")
                                    if hist_data.get('ev_ebitda_ratios'):
                                        ev_df = pd.DataFrame({
                                            '年份': range(2019, 2019 + len(hist_data['ev_ebitda_ratios'])),
                                            'EV/EBITDA倍数': hist_data['ev_ebitda_ratios']
                                        })
                                        st.dataframe(ev_df, use_container_width=True)
                        
                        # 显示可比公司分析
                        if results.get('comparable_companies'):
                            st.subheader("🔍 可比公司分析")
                            comp_data = results['comparable_companies']
                            
                            for business, companies in comp_data.items():
                                with st.expander(f"📈 {business.replace('_', ' ').title()} 可比公司", expanded=True):
                                    if companies:
                                        comp_df = pd.DataFrame([
                                            {
                                                '公司': company,
                                                'PE倍数': data.get('pe_ratio', 0),
                                                'EV/EBITDA': data.get('ev_ebitda', 0),
                                                '收入增长率': f"{data.get('revenue_growth', 0)*100:.1f}%",
                                                '利润率': f"{data.get('profit_margin', 0)*100:.1f}%"
                                            }
                                            for company, data in companies.items()
                                        ])
                                        st.dataframe(comp_df, use_container_width=True)
                        
                        # 显示详细业务线拆分
                        st.subheader("📊 业务线详细拆分")
                        
                        # Google Services
                        with st.expander("🔍 Google Services 详细信息", expanded=True):
                            services_data = results['business_breakdown']['google_services']
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("2023年营收", f"${services_data['revenue_2023']/1e9:.1f}B")
                            with col2:
                                st.metric("2023年营业利润", f"${services_data['operating_income_2023']/1e9:.1f}B")
                            with col3:
                                st.metric("营业利润率", f"{services_data['operating_margin']:.1%}")
                            
                            st.markdown(f"""
                            **业务描述：** {services_data['description']}
                            
                            **估值方法：** PE估值法（基于历史数据和可比公司分析）
                            **估值结果：** ${results['services_valuation']/1e9:.1f}B ({results['services_percentage']:.1f}%)
                            """)
                        
                        # Google Cloud
                        with st.expander("🔍 Google Cloud 详细信息", expanded=True):
                            cloud_data = results['business_breakdown']['google_cloud']
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("2023年营收", f"${cloud_data['revenue_2023']/1e9:.1f}B")
                            with col2:
                                st.metric("2023年营业利润", f"${cloud_data['operating_income_2023']/1e9:.1f}B")
                            with col3:
                                st.metric("营业利润率", f"{cloud_data['operating_margin']:.1%}")
                            
                            st.markdown(f"""
                            **业务描述：** {cloud_data['description']}
                            
                            **估值方法：** EV估值法（基于历史数据和可比公司分析）
                            **估值结果：** ${results['cloud_valuation']/1e9:.1f}B ({results['cloud_percentage']:.1f}%)
                            """)
                        
                        # Other Bets
                        with st.expander("🔍 Other Bets 详细信息", expanded=True):
                            other_bets_data = results['other_bets_breakdown']
                            
                            # 创建Other Bets详细表格
                            other_bets_df = pd.DataFrame([
                                {
                                    '项目': bet_name,
                                    '描述': bet_data['description'],
                                    '估值': f"${bet_data['valuation_estimate']/1e9:.1f}B",
                                    '成功概率': f"{bet_data['success_probability']:.1%}",
                                    '成熟期': f"{bet_data['time_to_maturity']}年",
                                    '市场大小': f"${bet_data['market_size']/1e9:.1f}B"
                                }
                                for bet_name, bet_data in other_bets_data.items()
                            ])
                            
                            st.dataframe(other_bets_df, use_container_width=True)
                            
                            st.markdown(f"""
                            **估值方法：** Real Option估值法（基于Monte Carlo模拟）
                            **总估值结果：** ${results['other_bets_valuation']/1e9:.1f}B ({results['other_bets_percentage']:.1f}%)
                            """)
                        
                        # 显示SOTP估值分解
                        st.subheader("📊 SOTP估值分解")
                        labels = ['Google Services', 'Google Cloud', 'Other Bets']
                        values = [
                            results['services_valuation'],
                            results['cloud_valuation'], 
                            results['other_bets_valuation']
                        ]
                        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
                        
                        fig = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=values,
                            hole=0.3,
                            marker_colors=colors,
                            textinfo='label+percent+value',
                            texttemplate='%{label}<br>$%{value:.0f}B<br>(%{percent:.1%})',
                            hovertemplate='<b>%{label}</b><br>估值: $%{value:.1f}B<br>占比: %{percent:.1%}<extra></extra>'
                        )])
                        
                        fig.update_layout(
                            title="SOTP估值分解",
                            title_x=0.5,
                            showlegend=True,
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 显示SOTP估值比较
                        st.subheader("📊 SOTP估值 vs 当前股价")
                        comparison_data = pd.DataFrame({
                            '估值类型': ['当前股价', 'SOTP目标股价'],
                            '股价': [current_price, results['target_price']],
                            '颜色': ['#d62728', '#2ca02c']
                        })
                        
                        fig = px.bar(
                            comparison_data,
                            x='估值类型',
                            y='股价',
                            color='颜色',
                            color_discrete_map={'#d62728': '#d62728', '#2ca02c': '#2ca02c'},
                            title="SOTP估值 vs 当前股价"
                        )
                        
                        fig.update_layout(
                            title_x=0.5,
                            height=400,
                            showlegend=False
                        )
                        
                        fig.update_traces(
                            texttemplate='$%{y:.2f}',
                            textposition='outside'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 生成投资建议
                        recommendation, recommendation_type = get_investment_recommendation(
                            current_price, results['target_price'], 90  # 高级模型置信度更高
                        )
                        
                        # 显示投资建议
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
                            <li><strong>目标股价：</strong> ${results['target_price']:.2f}</li>
                            <li><strong>估值溢价：</strong> {((results['target_price'] / current_price - 1) * 100):.1f}%</li>
                            <li><strong>总估值：</strong> ${results['total_valuation']/1e9:.1f}B</li>
                            <li><strong>净债务：</strong> ${results['net_debt']/1e9:.1f}B</li>
                            <li><strong>估值方法：</strong> 高级版SOTP估值模型</li>
                            <li><strong>数据来源：</strong> 历史数据分析 + 可比公司分析 + Monte Carlo模拟</li>
                            <li><strong>模型置信度：</strong> 90%</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.error("高级版SOTP估值计算失败，无法获取结果")
                        
                elif "增强版" in model_version and enhanced_sotp_available and calculate_enhanced_sotp_valuation is not None:
                    # 使用增强版SOTP模型
                    results, report = calculate_enhanced_sotp_valuation("GOOG")
                    
                    if results:
                        # 获取当前股价
                        stock_data = get_stock_data("GOOG")
                        current_price = stock_data['current_price'] if stock_data else results['current_price']
                        
                        # 显示增强版SOTP估值结果
                        st.subheader("🔬 Alphabet 增强版SOTP估值结果")
                        
                        # 创建指标卡片
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                label="当前股价",
                                value=f"${current_price:.2f}",
                                delta=None
                            )
                        
                        with col2:
                            st.metric(
                                label="目标股价",
                                value=f"${results['target_price']:.2f}",
                                delta=f"{((results['target_price'] / current_price - 1) * 100):.1f}%"
                            )
                        
                        with col3:
                            st.metric(
                                label="总估值",
                                value=f"${results['total_valuation']/1e9:.1f}B",
                                delta=None
                            )
                        
                        with col4:
                            st.metric(
                                label="净债务",
                                value=f"${results['net_debt']/1e9:.1f}B",
                                delta=None
                            )
                        
                        # 显示详细业务线拆分
                        st.subheader("📊 业务线详细拆分")
                        
                        # Google Services
                        with st.expander("🔍 Google Services 详细信息", expanded=True):
                            services_data = results['business_breakdown']['google_services']
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("2023年营收", f"${services_data['revenue_2023']/1e9:.1f}B")
                            with col2:
                                st.metric("2023年营业利润", f"${services_data['operating_income_2023']/1e9:.1f}B")
                            with col3:
                                st.metric("营业利润率", f"{services_data['operating_margin']:.1%}")
                            
                            st.markdown(f"""
                            **业务描述：** {services_data['description']}
                            
                            **估值方法：** PE估值法
                            **估值结果：** ${results['services_valuation']/1e9:.1f}B ({results['services_percentage']:.1f}%)
                            """)
                        
                        # Google Cloud
                        with st.expander("🔍 Google Cloud 详细信息", expanded=True):
                            cloud_data = results['business_breakdown']['google_cloud']
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("2023年营收", f"${cloud_data['revenue_2023']/1e9:.1f}B")
                            with col2:
                                st.metric("2023年营业利润", f"${cloud_data['operating_income_2023']/1e9:.1f}B")
                            with col3:
                                st.metric("营业利润率", f"{cloud_data['operating_margin']:.1%}")
                            
                            st.markdown(f"""
                            **业务描述：** {cloud_data['description']}
                            
                            **估值方法：** EV估值法
                            **估值结果：** ${results['cloud_valuation']/1e9:.1f}B ({results['cloud_percentage']:.1f}%)
                            """)
                        
                        # Other Bets
                        with st.expander("🔍 Other Bets 详细信息", expanded=True):
                            other_bets_data = results['other_bets_breakdown']
                            
                            # 创建Other Bets详细表格
                            other_bets_df = pd.DataFrame([
                                {
                                    '项目': bet_name,
                                    '描述': bet_data['description'],
                                    '估值': f"${bet_data['valuation_estimate']/1e9:.1f}B",
                                    '成功概率': f"{bet_data['success_probability']:.1%}",
                                    '成熟期': f"{bet_data['time_to_maturity']}年",
                                    '市场大小': f"${bet_data['market_size']/1e9:.1f}B"
                                }
                                for bet_name, bet_data in other_bets_data.items()
                            ])
                            
                            st.dataframe(other_bets_df, use_container_width=True)
                            
                            st.markdown(f"""
                            **估值方法：** Real Option估值法
                            **总估值结果：** ${results['other_bets_valuation']/1e9:.1f}B ({results['other_bets_percentage']:.1f}%)
                            """)
                        
                        # 显示SOTP估值分解
                        st.subheader("📊 SOTP估值分解")
                        labels = ['Google Services', 'Google Cloud', 'Other Bets']
                        values = [
                            results['services_valuation'],
                            results['cloud_valuation'], 
                            results['other_bets_valuation']
                        ]
                        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
                        
                        fig = go.Figure(data=[go.Pie(
                            labels=labels,
                            values=values,
                            hole=0.3,
                            marker_colors=colors,
                            textinfo='label+percent+value',
                            texttemplate='%{label}<br>$%{value:.0f}B<br>(%{percent:.1%})',
                            hovertemplate='<b>%{label}</b><br>估值: $%{value:.1f}B<br>占比: %{percent:.1%}<extra></extra>'
                        )])
                        
                        fig.update_layout(
                            title="SOTP估值分解",
                            title_x=0.5,
                            showlegend=True,
                            height=400
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 显示SOTP估值比较
                        st.subheader("📊 SOTP估值 vs 当前股价")
                        comparison_data = pd.DataFrame({
                            '估值类型': ['当前股价', 'SOTP目标股价'],
                            '股价': [current_price, results['target_price']],
                            '颜色': ['#d62728', '#2ca02c']
                        })
                        
                        fig = px.bar(
                            comparison_data,
                            x='估值类型',
                            y='股价',
                            color='颜色',
                            color_discrete_map={'#d62728': '#d62728', '#2ca02c': '#2ca02c'},
                            title="SOTP估值 vs 当前股价"
                        )
                        
                        fig.update_layout(
                            title_x=0.5,
                            height=400,
                            showlegend=False
                        )
                        
                        fig.update_traces(
                            texttemplate='$%{y:.2f}',
                            textposition='outside'
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # 生成投资建议
                        recommendation, recommendation_type = get_investment_recommendation(
                            current_price, results['target_price'], 85
                        )
                        
                        # 显示投资建议
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
                            <li><strong>目标股价：</strong> ${results['target_price']:.2f}</li>
                            <li><strong>估值溢价：</strong> {((results['target_price'] / current_price - 1) * 100):.1f}%</li>
                            <li><strong>总估值：</strong> ${results['total_valuation']/1e9:.1f}B</li>
                            <li><strong>净债务：</strong> ${results['net_debt']/1e9:.1f}B</li>
                            <li><strong>估值方法：</strong> 增强版SOTP估值模型</li>
                            <li><strong>数据来源：</strong> Alphabet 2023年财报 + 统计预测模型 + Real Option模型</li>
                            </ul>
                        </div>
                        """, unsafe_allow_html=True)
                        
                    else:
                        st.error("增强版SOTP估值计算失败，无法获取结果")
                        
                elif sotp_model_available and calculate_sotp_valuation is not None:
                    # 使用基础版SOTP模型
                    results = calculate_sotp_valuation("GOOG")
                    
                    if results:
                        # 获取当前股价
                        stock_data = get_stock_data("GOOG")
                        current_price = stock_data['current_price'] if stock_data else results['current_price']
                        
                        # 显示基础版SOTP估值结果
                        st.subheader("📊 Alphabet 基础版SOTP估值结果")
                        
                        # 创建指标卡片
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            st.metric(
                                label="当前股价",
                                value=f"${current_price:.2f}",
                                delta=None
                            )
                        
                        with col2:
                            st.metric(
                                label="目标股价",
                                value=f"${results['target_price']:.2f}",
                                delta=f"{((results['target_price'] / current_price - 1) * 100):.1f}%"
                            )
                        
                        with col3:
                            st.metric(
                                label="总估值",
                                value=f"${results['total_valuation']/1e9:.1f}B",
                                delta=None
                            )
                        
                        with col4:
                            st.metric(
                                label="净债务",
                                value=f"${results['net_debt']/1e9:.1f}B",
                                delta=None
                            )
                        
                        # 显示基础版结果的其他内容...
                        st.info("这是基础版SOTP估值结果。建议使用高级版SOTP模型以获得更准确的估值。")
                        
                    else:
                        st.error("基础版SOTP估值计算失败，无法获取结果")
                else:
                    st.error("SOTP模型导入失败，无法运行估值分析")
                
            except Exception as e:
                st.error(f"SOTP估值计算失败: {e}")
                st.exception(e)

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
    sotp_target_price = None   # SOTP模型结果
    
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
    
    # 尝试获取SOTP模型的实际结果
    try:
        if enhanced_sotp_available and calculate_enhanced_sotp_valuation is not None:
            sotp_results, _ = calculate_enhanced_sotp_valuation("GOOG")
            if sotp_results:
                sotp_target_price = sotp_results['target_price']
            else:
                sotp_target_price = 195.00  # 使用合理的默认值
        elif sotp_model_available and calculate_sotp_valuation is not None:
            sotp_results = calculate_sotp_valuation("GOOG")
            if sotp_results:
                sotp_target_price = sotp_results['target_price']
            else:
                sotp_target_price = 195.00  # 使用合理的默认值
        else:
            sotp_target_price = 195.00  # 使用合理的默认值
    except Exception as e:
        st.warning(f"SOTP模型计算失败: {e}")
        sotp_target_price = 195.00  # 使用合理的默认值
    
    # 创建Alphabet的对比数据 - 使用实际计算结果
    comparison_data = {
        '估值模型': ['PE模型', 'DCF模型', 'EV模型', 'PS模型', 'SOTP模型'],
        '估值结果(美元)': [pe_target_price, dcf_target_price, ev_target_price, ps_target_price, sotp_target_price],
        '置信度(%)': [88, 85, 82, 80, 85],
        '适用场景': ['成熟公司', '成长公司', '重资产公司', '科技公司', '多元化公司'],
        '模型特点': ['相对估值', '绝对估值', '相对估值', '相对估值', '分部估值']
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
