# ALIGNN 二分类完整指南

## 🎯 这是什么？

这是一套完整的 ALIGNN 二分类训练工具和文档，帮助您快速开始训练自己的二分类模型。

## 📦 包含内容

### 📖 文档（必读）

1. **快速开始.md** ⭐
   - 最快上手指南
   - 三种训练方法
   - 根据数据集大小选择配置
   - 针对您的108K数据集的推荐

2. **二分类训练指南.md**
   - 详细的训练步骤
   - 数据准备要求
   - 完整的训练流程

3. **配置参数详解.md**
   - 所有参数的详细说明
   - 不同任务的配置示例
   - 调优建议

4. **问题修复指南.md**
   - 常见错误及解决方案
   - 依赖问题修复
   - 数据格式问题修复

### ⚙️ 配置文件

5. **config_binary_classification.json** （中等数据集，1K-10K样本）
   - batch_size: 32
   - epochs: 300
   - hidden_features: 256
   - layers: 4

6. **config_small_dataset.json** （小数据集，< 1K样本）
   - batch_size: 16
   - epochs: 500
   - hidden_features: 128
   - layers: 3
   - 防止过拟合

7. **config_large_dataset.json** ⭐（大数据集，> 10K样本，**推荐用于您的108K数据**）
   - batch_size: 128
   - epochs: 100
   - hidden_features: 512
   - layers: 6
   - 训练更快

### 🛠️ 工具脚本

8. **run_binary_classification.sh**
   - 一键启动训练
   - 自动检查数据
   - 显示训练进度

9. **train_binary_classification_example.py**
   - Python API 训练示例
   - 数据统计分析
   - 完整的工作流程

10. **check_and_fix_data.py** ⭐
    - 自动检查数据格式
    - 修复 id_prop.csv
    - 搜索 CIF 文件
    - 验证文件匹配
    - 提供阈值建议

11. **fix_dependencies.sh**
    - 修复 pydantic 依赖问题
    - 一键解决环境问题

## 🚀 5分钟快速开始

### 前提条件
✅ 数据格式已正确（108134 个 CIF 文件）
✅ id_prop.csv 格式正确

### 第1步：拉取最新代码

```bash
cd /path/to/alignn
git pull origin claude/alignn-binary-classification-01Gd3smtc3KBu4WsA7u8tEUy
```

### 第2步：选择训练方式

#### 方式A：使用Shell脚本（最简单）

```bash
# 1. 编辑脚本（只需改2行）
nano run_binary_classification.sh
# DATA_DIR="./data"           # 改为您的数据目录
# THRESHOLD=0.5               # 改为合适的阈值

# 2. 运行
./run_binary_classification.sh
```

#### 方式B：直接命令行（推荐，适合您的大数据集）

```bash
train_alignn.py \
    --root_dir ./data \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results_108k
```

#### 方式C：Python脚本（最灵活）

```bash
nano train_binary_classification_example.py
# 修改 ROOT_DIR 和 CLASSIFICATION_THRESHOLD
python train_binary_classification_example.py
```

### 第3步：等待训练完成

训练进度会实时显示：
```
Epoch 1/100
  Train Loss: 0.523 | Time: 125s
  Val Loss: 0.487 | Time: 12s
  ✓ Saving model
```

### 第4步：查看结果

```bash
# 查看测试集预测
head -20 ./results_108k/prediction_results_test_set.csv

# 查看训练历史
cat ./results_108k/history_val.json | python -m json.tool
```

## 📊 您的数据集

- **样本数**: 108,134
- **文件格式**: CIF ✅
- **id_prop.csv**: 格式正确 ✅
- **推荐配置**: `config_large_dataset.json`
- **推荐批次**: 128-256
- **推荐轮数**: 50-100

## 🎯 推荐配置（针对您的数据）

```bash
train_alignn.py \
    --root_dir ./data \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results

# 预计时间（取决于GPU）:
# V100: 10-20小时
# A100: 5-10小时
# RTX 3090: 15-30小时
```

## 🔧 常见问题

### Q1: 我应该使用哪个配置文件？

根据数据集大小：
- **< 1,000 样本**: `config_small_dataset.json`
- **1,000-10,000 样本**: `config_binary_classification.json`
- **> 10,000 样本**: `config_large_dataset.json` ⭐ **您的情况**

### Q2: 如何选择分类阈值？

```python
# 运行数据分析
python check_and_fix_data.py ./data

# 会显示不同阈值的类别分布，选择平衡的阈值
```

### Q3: GPU内存不足怎么办？

```bash
# 减小批次大小
--batch_size 64  # 或 32, 16

# 或使用小模型
--config config_binary_classification.json
```

### Q4: 训练太慢怎么办？

```bash
# 增加批次大小
--batch_size 256

# 增加数据加载线程
# 在配置文件中设置: "num_workers": 8
```

### Q5: 如何继续上次的训练？

```bash
train_alignn.py \
    --root_dir ./data \
    --config config_large_dataset.json \
    --restart_model_path ./results/best_model.pt \
    --output_dir ./results_continue
```

## 📈 监控和优化

### 查看训练曲线

```python
import json
import matplotlib.pyplot as plt

# 读取训练历史
with open('./results/history_train.json') as f:
    train_hist = json.load(f)
with open('./results/history_val.json') as f:
    val_hist = json.load(f)

# 绘制损失曲线
train_loss = [x[0] for x in train_hist]
val_loss = [x[0] for x in val_hist]

plt.plot(train_loss, label='Train')
plt.plot(val_loss, label='Validation')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.savefig('training_curve.png')
```

### 分析预测结果

```python
import pandas as pd
from sklearn.metrics import classification_report, confusion_matrix

# 读取预测结果
df = pd.read_csv('./results/prediction_results_test_set.csv')

# 分类报告
print(classification_report(df['target'], df['prediction']))

# 混淆矩阵
print(confusion_matrix(df['target'], df['prediction']))
```

## 🛠️ 故障排除

如果遇到问题，按以下顺序排查：

1. **检查数据**: `python check_and_fix_data.py ./data`
2. **修复依赖**: `./fix_dependencies.sh`
3. **查看详细文档**: 阅读 `问题修复指南.md`
4. **测试运行**: 先用 `--epochs 5` 快速测试

## 📚 学习路径

1. 阅读 **快速开始.md** （5分钟）
2. 运行 `check_and_fix_data.py` 检查数据
3. 选择合适的配置文件
4. 先用少量轮数测试（--epochs 10）
5. 正式训练
6. 分析结果，调优参数
7. 阅读 **配置参数详解.md** 深入了解

## 🎊 已修复的问题

- ✅ pydantic 依赖错误
- ✅ id_prop.csv 格式问题（.cif后缀，缺少header）
- ✅ 配置文件参数错误（num_heads, attention_heads）
- ✅ CIF 文件搜索和定位

## 💡 最佳实践

1. **数据准备**
   - 先运行 `check_and_fix_data.py` 验证数据
   - 确保类别平衡（或使用适当的阈值）

2. **训练策略**
   - 先小规模测试（--epochs 10）
   - 确认能运行后再长时间训练
   - 监控验证损失，防止过拟合

3. **超参数调优**
   - 先用默认配置
   - 根据结果调整学习率和批次大小
   - 最后优化模型结构

4. **结果分析**
   - 查看混淆矩阵
   - 分析错误预测的样本
   - 根据业务需求调整阈值

## 🆘 获取帮助

如果文档无法解决您的问题：

1. 查看 **问题修复指南.md**
2. 运行诊断命令获取详细信息
3. 检查 ALIGNN GitHub issues
4. 提供完整的错误日志

## 🎯 下一步

现在您可以：

```bash
# 1. 拉取最新代码
git pull origin claude/alignn-binary-classification-01Gd3smtc3KBu4WsA7u8tEUy

# 2. 开始训练（推荐命令）
train_alignn.py \
    --root_dir ./data \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results_108k
```

**祝训练顺利！** 🚀

---

## 📁 文件清单

- ✅ 快速开始.md
- ✅ 二分类训练指南.md
- ✅ 配置参数详解.md
- ✅ 问题修复指南.md
- ✅ config_binary_classification.json
- ✅ config_small_dataset.json
- ✅ config_large_dataset.json ⭐
- ✅ run_binary_classification.sh
- ✅ train_binary_classification_example.py
- ✅ check_and_fix_data.py ⭐
- ✅ fix_dependencies.sh

所有文件都已推送到分支 `claude/alignn-binary-classification-01Gd3smtc3KBu4WsA7u8tEUy`
