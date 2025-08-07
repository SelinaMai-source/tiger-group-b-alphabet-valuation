#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加PE模型路径
sys.path.append('/root/tiger_group_final/valuation_models/pe_model')

try:
    from pe_visual import create_pe_valuation_dashboard
    
    print("🔍 检查PE估值模型结果...")
    results = create_pe_valuation_dashboard()
    
    print("\n📊 EPS预测结果:")
    print(f"   • 三表建模: ${results['eps_predictions']['three_statement']:.2f}")
    print(f"   • ARIMA: ${results['eps_predictions']['arima']:.2f}")
    print(f"   • 可比公司: ${results['eps_predictions']['comparable']:.2f}")
    print(f"   • 融合预测: ${results['eps_predictions']['blended']:.2f}")
    print(f"\n📈 Forward PE: {results['forward_pe']}")
    print(f"💰 当前股价: ${results['current_price']:.2f}")
    
    # 计算目标价格
    current_price = results['current_price']
    predicted_eps = results['eps_predictions']['blended']
    current_pe = results.get('forward_pe', 25.0)
    
    print(f"\n🎯 目标价格计算:")
    print(f"   • 预测EPS: ${predicted_eps:.2f}")
    print(f"   • Forward PE: {current_pe}")
    print(f"   • 目标价格 (PE × EPS): ${current_pe * predicted_eps:.2f}")
    
    # 检查是否合理
    target_price = current_pe * predicted_eps
    if target_price > current_price * 2:
        print(f"⚠️  警告: 目标价格 ${target_price:.2f} 过高，超过当前股价的2倍")
        print(f"   建议使用更保守的PE倍数")
    
except Exception as e:
    print(f"❌ 错误: {e}") 