#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 模拟网站的环境设置
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir  # 项目根目录就是当前目录
sys.path.append(project_root)

def test_pe_integration():
    """测试PE模型在网站环境中的集成"""
    try:
        print("🔍 测试PE模型集成...")
        
        # 模拟网站的路径设置
        pe_model_path = os.path.join(project_root, 'valuation_models', 'pe_model')
        sys.path.append(pe_model_path)
        
        print(f"📁 PE模型路径: {pe_model_path}")
        print(f"📁 当前工作目录: {os.getcwd()}")
        
        # 测试导入
        try:
            from pe_visual import create_pe_valuation_dashboard
            print("✅ PE模型导入成功")
        except ImportError as e:
            print(f"❌ PE模型导入失败: {e}")
            return None
        
        # 模拟网站的目录切换
        original_dir = os.getcwd()
        try:
            print(f"📁 切换到PE模型目录: {pe_model_path}")
            os.chdir(pe_model_path)
            print(f"📁 切换后工作目录: {os.getcwd()}")
            
            # 测试函数调用
            print("🔍 测试PE模型函数调用...")
            results = create_pe_valuation_dashboard()
            
            print(f"✅ PE模型函数调用成功")
            print(f"📊 返回结果类型: {type(results)}")
            
            # 检查返回结果的结构
            if isinstance(results, dict):
                print("✅ 返回结果是字典类型")
                
                if 'eps_predictions' in results:
                    print("✅ 包含eps_predictions键")
                    print(f"📊 EPS预测: {results['eps_predictions']}")
                    
                    # 检查所有必需的键
                    required_keys = ['three_statement', 'arima', 'comparable', 'blended']
                    missing_keys = [key for key in required_keys if key not in results['eps_predictions']]
                    
                    if missing_keys:
                        print(f"❌ 缺少EPS预测键: {missing_keys}")
                    else:
                        print("✅ 所有必需的EPS预测键都存在")
                else:
                    print("❌ 缺少eps_predictions键")
                    print(f"📊 可用键: {list(results.keys())}")
            else:
                print(f"❌ 返回结果不是字典类型，实际类型: {type(results)}")
            
            return results
            
        except Exception as e:
            print(f"❌ PE模型函数调用失败: {e}")
            print(f"📊 错误类型: {type(e)}")
            return None
        finally:
            # 切换回原目录
            try:
                os.chdir(original_dir)
                print(f"📁 切换回原目录: {os.getcwd()}")
            except Exception as e:
                print(f"⚠️ 切换回原目录失败: {e}")
        
    except Exception as e:
        print(f"❌ 集成测试失败: {e}")
        return None

if __name__ == "__main__":
    print("🚀 开始PE模型集成测试...")
    results = test_pe_integration()
    
    if results:
        print("✅ PE模型集成测试完成")
        print(f"📊 最终结果: {results}")
    else:
        print("❌ PE模型集成测试失败") 