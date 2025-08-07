# 🐯 Tiger Group B - Alphabet估值分析系统

基于四种估值模型的综合财务分析平台，专门用于Alphabet (GOOG) 的估值分析。

## 📊 项目概述

本项目集成了四种主要的估值模型：
- **PE估值模型** - 基于市盈率的相对估值
- **DCF估值模型** - 基于自由现金流的绝对估值
- **EV估值模型** - 基于企业价值的相对估值
- **PS估值模型** - 基于市销率的相对估值

## 🏗️ 项目结构

```
tiger_group_final/
├── app/
│   └── dashboard_app.py          # 主仪表板应用
├── valuation_models/
│   ├── pe_model/                 # PE估值模型
│   ├── dcf_model/                # DCF估值模型
│   ├── ev_model/                 # EV估值模型
│   ├── ps_model/                 # PS估值模型
│   └── data/                     # 模型数据
├── config/                       # 配置文件
├── utils/                        # 工具函数
├── visualization/                # 可视化组件
├── requirements.txt              # 依赖包列表
└── README.md                     # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt
```

### 2. 运行仪表板

```bash
# 进入app目录
cd app

# 运行Streamlit应用
streamlit run dashboard_app.py --server.port 8501 --server.address 0.0.0.0
```

### 3. 访问仪表板

打开浏览器访问：`http://localhost:8501`

## 📈 功能特性

### 🏠 仪表板概览
- 四种估值模型的综合展示
- 实时股价和关键指标
- 股价走势图
- 模型置信度对比

### 📈 PE估值模型
- 三表建模预测
- ARIMA时间序列预测
- 可比公司回归分析
- 加权融合算法

### 💰 DCF估值模型
- 自由现金流计算
- 未来现金流预测
- 折现率计算
- 终值计算

### 🏢 EV估值模型
- 企业价值计算
- 可比公司分析
- 相对估值
- 敏感性分析

### 📊 PS估值模型
- 收入预测
- 可比公司分析
- 相对估值
- 多模型融合

### 🎯 综合对比分析
- 四种模型结果对比
- 置信度分析
- 投资建议
- 风险分析

## 🎨 界面特色

- **现代化设计** - 使用渐变色彩和卡片式布局
- **响应式布局** - 适配不同屏幕尺寸
- **实时数据** - 集成Yahoo Finance实时数据
- **交互式图表** - 使用Plotly创建交互式可视化
- **数据缓存** - 优化性能和用户体验

## 🔧 技术栈

- **前端框架** - Streamlit
- **数据处理** - Pandas, NumPy
- **可视化** - Plotly, Matplotlib, Seaborn
- **数据源** - Yahoo Finance API
- **机器学习** - Scikit-learn, Statsmodels

## 📊 数据来源

- **财务数据** - Yahoo Finance API
- **市场数据** - Financial Modeling Prep API
- **历史数据** - 公开财务报表

## 🎯 使用场景

- **投资分析** - 为投资决策提供数据支持
- **财务研究** - 学术研究和财务分析
- **风险管理** - 评估投资风险
- **估值建模** - 学习估值方法

## ⚠️ 注意事项

1. **数据准确性** - 所有数据仅供参考，投资决策请谨慎
2. **模型局限性** - 估值模型有其局限性，不应作为唯一决策依据
3. **市场风险** - 股市有风险，投资需谨慎
4. **数据更新** - 建议定期更新数据和模型

## 🤝 贡献指南

欢迎提交Issue和Pull Request来改进项目。

## 📄 许可证

本项目仅供学习和研究使用。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 邮箱：tiger.group@example.com
- GitHub：https://github.com/tiger-group

---

**免责声明**：本项目仅供学习和研究使用，不构成投资建议。投资有风险，入市需谨慎。
