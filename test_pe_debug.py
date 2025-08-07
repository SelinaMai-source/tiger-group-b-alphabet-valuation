#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os

# 添加项目根目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = current_dir
sys.path.append(project_root)

# 添加PE模型路径
pe_model_path = os.path.join(project_root, 'valuation_models', 'pe_model')
sys.path.append(pe_model_path)

print(f"🔍 当前目录: {os.getcwd()}")
print(f"🔍 项目根目录: {project_root}")
print(f"🔍 PE模型路径: {pe_model_path}")

try:
    print("🔍 尝试导入PE模型...")
    from pe_visual import create_pe_valuation_dashboard
    print("✅ PE模型导入成功")
    
    print("🔍 尝试调用create_pe_valuation_dashboard...")
    results = create_pe_valuation_dashboard()
    print(f"🔍 返回结果类型: {type(results)}")
    print(f"🔍 返回结果内容: {results}")
    
    if isinstance(results, dict):
        print("✅ 返回结果是正确的字典类型")
        if 'eps_predictions' in results:
            print("✅ 包含eps_predictions键")
        else:
            print("❌ 不包含eps_predictions键")
    else:
        print(f"❌ 返回结果不是字典类型，而是: {type(results)}")
        
except ImportError as e:
    print(f"❌ PE模型导入失败: {e}")
except Exception as e:
    print(f"❌ PE模型调用失败: {e}")
    import traceback
    traceback.print_exc() 