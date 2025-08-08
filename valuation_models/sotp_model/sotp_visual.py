# sotp_model/sotp_visual.py

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
try:
    from .sotp_calc import calculate_sotp_valuation, get_sotp_valuation_summary
except ImportError:
    # 如果相对导入失败，尝试绝对导入
    from sotp_calc import calculate_sotp_valuation, get_sotp_valuation_summary

def create_sotp_dashboard():
    """
    创建SOTP估值dashboard
    
    Returns:
        dict: 包含SOTP估值结果的字典
    """
    try:
        # 计算SOTP估值
        results = calculate_sotp_valuation()
        summary = get_sotp_valuation_summary()
        
        return {
            "results": results,
            "summary": summary,
            "success": True
        }
    except Exception as e:
        st.error(f"SOTP估值计算失败：{e}")
        return {
            "results": None,
            "summary": None,
            "success": False
        }

def plot_sotp_breakdown(results):
    """
    绘制SOTP估值分解图
    
    Args:
        results (dict): SOTP估值结果
    """
    if not results:
        return
    
    # 创建饼图数据
    labels = ['Google Services', 'Google Cloud', 'Other Bets']
    values = [
        results['services_valuation'],
        results['cloud_valuation'], 
        results['other_bets_valuation']
    ]
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    # 创建饼图
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

def plot_sotp_comparison(results):
    """
    绘制SOTP估值与当前股价对比图
    
    Args:
        results (dict): SOTP估值结果
    """
    if not results:
        return
    
    # 创建对比数据
    comparison_data = pd.DataFrame({
        '估值类型': ['当前股价', 'SOTP目标股价'],
        '股价': [results['current_price'], results['target_price']],
        '颜色': ['#d62728', '#2ca02c']
    })
    
    # 创建柱状图
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
    
    # 添加数值标签
    fig.update_traces(
        texttemplate='$%{y:.2f}',
        textposition='outside'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def plot_sotp_components(results):
    """
    绘制SOTP各组件详细分析图
    
    Args:
        results (dict): SOTP估值结果
    """
    if not results:
        return
    
    # 创建子图
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Google Services (PE估值)', 'Google Cloud (EV估值)', 
                       'Other Bets (Real Option)', '估值汇总'),
        specs=[[{"type": "bar"}, {"type": "bar"}],
               [{"type": "bar"}, {"type": "indicator"}]]
    )
    
    # Google Services
    fig.add_trace(
        go.Bar(
            x=['Services估值'],
            y=[results['services_valuation']/1e9],
            name='Google Services',
            marker_color='#1f77b4',
            text=[f"${results['services_valuation']/1e9:.1f}B"],
            textposition='outside'
        ),
        row=1, col=1
    )
    
    # Google Cloud
    fig.add_trace(
        go.Bar(
            x=['Cloud估值'],
            y=[results['cloud_valuation']/1e9],
            name='Google Cloud',
            marker_color='#ff7f0e',
            text=[f"${results['cloud_valuation']/1e9:.1f}B"],
            textposition='outside'
        ),
        row=1, col=2
    )
    
    # Other Bets
    fig.add_trace(
        go.Bar(
            x=['Other Bets估值'],
            y=[results['other_bets_valuation']/1e9],
            name='Other Bets',
            marker_color='#2ca02c',
            text=[f"${results['other_bets_valuation']/1e9:.1f}B"],
            textposition='outside'
        ),
        row=2, col=1
    )
    
    # 估值汇总指标
    fig.add_trace(
        go.Indicator(
            mode="gauge+number+delta",
            value=results['target_price'],
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "目标股价"},
            delta={'reference': results['current_price']},
            gauge={
                'axis': {'range': [None, results['target_price']*1.2]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, results['current_price']], 'color': "lightgray"},
                    {'range': [results['current_price'], results['target_price']], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': results['target_price']
                }
            }
        ),
        row=2, col=2
    )
    
    fig.update_layout(
        title="SOTP估值组件分析",
        title_x=0.5,
        height=600,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)

def display_sotp_metrics(results):
    """
    显示SOTP估值关键指标
    
    Args:
        results (dict): SOTP估值结果
    """
    if not results:
        return
    
    # 创建指标卡片
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="当前股价",
            value=f"${results['current_price']:.2f}",
            delta=None
        )
    
    with col2:
        st.metric(
            label="目标股价",
            value=f"${results['target_price']:.2f}",
            delta=f"{((results['target_price'] / results['current_price'] - 1) * 100):.1f}%"
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

def display_sotp_details(results):
    """
    显示SOTP估值详细信息
    
    Args:
        results (dict): SOTP估值结果
    """
    if not results:
        return
    
    st.subheader("📊 SOTP估值详细信息")
    
    # 创建详细信息表格
    details_data = {
        '业务线': ['Google Services', 'Google Cloud', 'Other Bets'],
        '估值方法': ['PE估值法', 'EV估值法', 'Real Option估值法'],
        '估值金额': [
            f"${results['services_valuation']/1e9:.1f}B",
            f"${results['cloud_valuation']/1e9:.1f}B",
            f"${results['other_bets_valuation']/1e9:.1f}B"
        ],
        '占比': [
            f"{results['services_percentage']:.1f}%",
            f"{results['cloud_percentage']:.1f}%",
            f"{results['other_bets_percentage']:.1f}%"
        ],
        '关键参数': [
            f"PE倍数: {results['services_pe_multiple']:.1f}",
            f"EV/EBITDA倍数: {results['cloud_ev_ebitda_multiple']:.1f}",
            f"成功概率: {results['other_bets_success_probability']:.1%}"
        ]
    }
    
    df = pd.DataFrame(details_data)
    st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    # 测试可视化功能
    results = calculate_sotp_valuation()
    if results:
        print("✅ SOTP可视化模块测试成功")
        print(f"目标股价：${results['target_price']:.2f}")
    else:
        print("❌ SOTP可视化模块测试失败")
