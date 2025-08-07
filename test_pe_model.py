#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
pe_model_path = os.path.join(project_root, 'valuation_models', 'pe_model')
sys.path.append(pe_model_path)

def test_pe_model():
    """测试PE模型是否能正常工作"""
    try:
        print("🔍 测试PE模型导入...")
        
        # 测试导入
        from pe_visual import create_pe_valuation_dashboard
        print("✅ PE模型导入成功")
        
        # 测试函数调用
        print("🔍 测试PE模型函数调用...")
        results = create_pe_valuation_dashboard()
        
        print(f"✅ PE模型函数调用成功")
        print(f"📊 返回结果类型: {type(results)}")
        print(f"📊 返回结果内容: {results}")
        
        # 检查返回结果的结构
        if isinstance(results, dict):
            print("✅ 返回结果是字典类型")
            
            if 'eps_predictions' in results:
                print("✅ 包含eps_predictions键")
                print(f"📊 EPS预测: {results['eps_predictions']}")
            else:
                print("❌ 缺少eps_predictions键")
                print(f"📊 可用键: {list(results.keys())}")
        else:
            print(f"❌ 返回结果不是字典类型，实际类型: {type(results)}")
        
        return results
        
    except ImportError as e:
        print(f"❌ PE模型导入失败: {e}")
        return None
    except Exception as e:
        print(f"❌ PE模型测试失败: {e}")
        print(f"📊 错误类型: {type(e)}")
        return None

if __name__ == "__main__":
    print("🚀 开始测试PE模型...")
    results = test_pe_model()
    
    if results:
        print("✅ PE模型测试完成")
    else:
        print("❌ PE模型测试失败") 