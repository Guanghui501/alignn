#!/bin/bash

# ALIGNN 数据修复和训练一键脚本
# 自动检测数据位置，修复格式，然后开始训练

echo "======================================"
echo "ALIGNN 一键修复并训练"
echo "======================================"
echo ""

# ========== 配置参数 ==========
# 如果您的数据在其他位置，请修改这里
DATA_ROOT="./data"           # 数据根目录
THRESHOLD=0.5                # 分类阈值
BATCH_SIZE=128               # 批次大小
EPOCHS=100                   # 训练轮数
CONFIG_FILE="./config_large_dataset.json"  # 配置文件

# ========== 自动检测数据目录 ==========
echo "步骤1: 检测数据目录..."

# 查找 id_prop.csv
if [ -f "$DATA_ROOT/id_prop.csv" ]; then
    ID_PROP_DIR="$DATA_ROOT"
    echo "  ✓ 找到 id_prop.csv: $ID_PROP_DIR/id_prop.csv"
elif [ -f "$DATA_ROOT/cif/id_prop.csv" ]; then
    ID_PROP_DIR="$DATA_ROOT/cif"
    echo "  ✓ 找到 id_prop.csv: $ID_PROP_DIR/id_prop.csv"
else
    echo "  ❌ 错误: 找不到 id_prop.csv"
    echo "  请确保文件在 $DATA_ROOT 或 $DATA_ROOT/cif 目录下"
    exit 1
fi

# 查找 CIF 文件
CIF_COUNT=$(find "$DATA_ROOT" -name "*.cif" | wc -l)
echo "  ✓ 找到 $CIF_COUNT 个 CIF 文件"

if [ $CIF_COUNT -eq 0 ]; then
    echo "  ❌ 错误: 没有找到 CIF 文件"
    exit 1
fi

# 确定 CIF 文件的主要位置
if [ -d "$DATA_ROOT/cif" ]; then
    CIF_DIR="$DATA_ROOT/cif"
    CIF_IN_SUBDIR=$(ls "$CIF_DIR"/*.cif 2>/dev/null | wc -l)
    if [ $CIF_IN_SUBDIR -gt 0 ]; then
        echo "  ✓ CIF 文件在: $CIF_DIR"
        MAIN_DIR="$CIF_DIR"
    else
        MAIN_DIR="$DATA_ROOT"
        echo "  ✓ CIF 文件在: $MAIN_DIR"
    fi
else
    MAIN_DIR="$DATA_ROOT"
    echo "  ✓ CIF 文件在: $MAIN_DIR"
fi

echo ""

# ========== 修复数据格式 ==========
echo "步骤2: 修复数据格式..."
echo ""

# 如果 id_prop.csv 和 CIF 文件不在同一目录，移动 id_prop.csv
if [ "$ID_PROP_DIR" != "$MAIN_DIR" ]; then
    echo "  将 id_prop.csv 移动到 CIF 文件目录..."
    if [ -f "$ID_PROP_DIR/id_prop.csv" ]; then
        cp "$ID_PROP_DIR/id_prop.csv" "$MAIN_DIR/id_prop.csv"
        echo "  ✓ 已复制到: $MAIN_DIR/id_prop.csv"
    fi
fi

# 运行修复脚本
python fix_data_format.py "$MAIN_DIR"

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ 数据修复失败，请检查错误信息"
    exit 1
fi

echo ""

# ========== 开始训练 ==========
echo "======================================"
echo "步骤3: 开始训练"
echo "======================================"
echo "数据目录: $MAIN_DIR"
echo "分类阈值: $THRESHOLD"
echo "批次大小: $BATCH_SIZE"
echo "训练轮数: $EPOCHS"
echo "配置文件: $CONFIG_FILE"
echo "======================================"
echo ""

# 运行训练
train_alignn.py \
    --root_dir "$MAIN_DIR" \
    --config "$CONFIG_FILE" \
    --classification_threshold "$THRESHOLD" \
    --file_format cif \
    --batch_size "$BATCH_SIZE" \
    --epochs "$EPOCHS" \
    --output_dir "./classification_results"

# 检查训练结果
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ 训练完成！"
    echo "======================================"
    echo "结果保存在: ./classification_results"
    echo ""
    echo "查看结果:"
    echo "  cat ./classification_results/prediction_results_test_set.csv | head -20"
else
    echo ""
    echo "======================================"
    echo "❌ 训练失败，请查看错误信息"
    echo "======================================"
    exit 1
fi
