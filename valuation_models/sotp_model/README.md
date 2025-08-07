# SOTP (Sum of the Parts) 估值模型

## 概述

SOTP估值模型将Alphabet的业务分为三个主要部分进行独立估值，然后汇总得到总估值。本模型包含三个版本：基础版、增强版和高级版。

## 模型版本

### 🚀 高级版SOTP模型（推荐）

**特点：**
- ✅ 收集更多历史数据（5年财务数据）
- ✅ 使用更复杂的统计模型
- ✅ 进行详细的可比公司分析
- ✅ 使用Monte Carlo模拟进行敏感性分析
- ✅ 基于历史数据调整估值倍数
- ✅ 提供95%置信区间

**包含功能：**
1. **历史数据收集**
   - 5年历史PE倍数分析
   - 5年历史EV/EBITDA倍数分析
   - 历史财务数据收集
   - 历史股价数据分析

2. **可比公司分析**
   - Google Services可比公司：META, AMZN, NFLX, TSLA
   - Google Cloud可比公司：MSFT, AMZN, ORCL, CRM
   - 自动获取可比公司财务指标
   - 计算可比公司平均倍数

3. **Monte Carlo模拟**
   - 10,000次模拟
   - 参数分布：PE倍数、EV/EBITDA倍数、收入增长率、利润率、成功概率
   - 提供目标股价均值、标准差、分位数
   - 95%置信区间分析

4. **高级统计模型**
   - 基于历史数据的倍数调整
   - 加权平均计算
   - 风险调整

### 🔬 增强版SOTP模型

**特点：**
- ✅ 基于真实财报数据（2021-2023年）
- ✅ 使用统计预测模型预测未来增长
- ✅ 复杂的Real Option模型计算Other Bets估值
- ✅ 考虑技术成熟度、竞争态势、监管风险等因素

**包含功能：**
1. **真实财报数据**
   - Alphabet 2023年10-K报告数据
   - 业务线拆分：Google Services (89.9%), Google Cloud (9.7%), Other Bets (0.4%)
   - 历史财务数据验证

2. **统计预测模型**
   - 收入增长预测
   - 利润率预测
   - 多模型融合

3. **Real Option模型**
   - 基于Black-Scholes期权定价模型
   - Monte Carlo模拟
   - 成功概率分析

### 📊 基础版SOTP模型

**特点：**
- ✅ 简化假设
- ✅ 快速计算
- ✅ 基础估值结果

## 业务线拆分

### 1. Google Services（主营搜索广告）
- **估值方法：** PE估值法
- **计算公式：** `services_value = services_net_income × services_pe_multiple`
- **业务范围：** Google搜索、YouTube、Google广告等核心业务
- **数据来源：** Alphabet 2023年财报（营收：$307.4B，营业利润：$101.2B）

### 2. Google Cloud（云服务）
- **估值方法：** EV估值法
- **计算公式：** `cloud_value = cloud_ebitda × ev_ebitda_multiple - cloud_net_debt`
- **业务范围：** 云计算、AI服务、企业解决方案
- **数据来源：** Alphabet 2023年财报（营收：$33.1B，营业利润：$0.9B）

### 3. Other Bets（其他创新项目）
- **估值方法：** Real Option估值法
- **计算公式：** `other_bets_value = Σ(option_value × success_probability)`
- **业务范围：** Waymo、Verily、Calico、X、Google Fiber等
- **详细拆分：** 基于每个项目的技术成熟度、市场大小、竞争水平、监管风险等因素

## 数据来源验证

- **数据来源：** Alphabet 2023年10-K报告
- **验证时间：** 2024-08-07
- **总营收：** $342.0B（2023年）
- **业务线占比：**
  - Google Services：89.9%（$307.4B）
  - Google Cloud：9.7%（$33.1B）
  - Other Bets：0.4%（$1.5B）
- **数据一致性：** 已验证，业务线营收之和等于总营收

## 使用方法

### 在Dashboard中使用

1. 选择"🎯 SOTP估值模型"
2. 选择模型版本：
   - 🚀 高级版SOTP模型（推荐）
   - 🔬 增强版SOTP模型
   - 📊 基础版SOTP模型
3. 点击"🚀 运行Alphabet SOTP估值分析"

### 直接调用

```python
# 高级版SOTP模型
from sotp_calc_enhanced import calculate_advanced_sotp_valuation
results = calculate_advanced_sotp_valuation("GOOG")

# 增强版SOTP模型
from sotp_calc_enhanced import calculate_enhanced_sotp_valuation
results, report = calculate_enhanced_sotp_valuation("GOOG")

# 基础版SOTP模型
from sotp_calc import calculate_sotp_valuation
results = calculate_sotp_valuation("GOOG")
```

## 输出结果

### 高级版输出
- 目标股价和估值溢价
- Monte Carlo模拟结果（均值、标准差、置信区间）
- 历史数据分析（PE倍数、EV/EBITDA倍数）
- 可比公司分析
- 详细业务线拆分
- 投资建议

### 增强版输出
- 目标股价和估值溢价
- 详细业务线拆分
- Real Option估值结果
- 投资建议

### 基础版输出
- 目标股价和估值溢价
- 基础业务线拆分
- 投资建议

## 技术实现

### 核心文件
- `sotp_calc_enhanced.py` - 高级版和增强版SOTP计算器
- `sotp_calc.py` - 基础版SOTP计算器
- `sotp_data_detailed.py` - 详细数据源
- `real_option_model.py` - Real Option模型
- `statistical_models.py` - 统计预测模型
- `sotp_visual.py` - 可视化功能

### 依赖库
- `numpy` - 数值计算
- `pandas` - 数据处理
- `yfinance` - 财务数据获取
- `scipy` - 统计计算
- `plotly` - 数据可视化
- `streamlit` - Web界面

## 注意事项

1. **数据来源：** 所有数据均基于公开信息和财报数据
2. **模型假设：** 包含主观判断，请谨慎使用
3. **风险提示：** 估值结果仅供参考，不构成投资建议
4. **更新频率：** 建议定期更新数据和模型参数

## 更新日志

### v3.0.0 (2024-08-07)
- 🚀 新增高级版SOTP模型
- 📊 添加历史数据收集功能
- 🔍 添加可比公司分析
- 🎲 添加Monte Carlo模拟
- 📈 改进统计模型
- 🎯 提高模型置信度

### v2.0.0 (2024-08-06)
- 🔬 新增增强版SOTP模型
- 📊 基于真实财报数据
- 🎯 添加Real Option模型
- 📈 改进统计预测

### v1.0.0 (2024-08-05)
- 📊 基础版SOTP模型
- 🎯 基础业务线拆分
- 📈 基础估值计算
