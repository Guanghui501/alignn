#!/bin/bash

# ALIGNN 二分类训练脚本
# 使用前请修改以下参数

# ========== 必须修改的参数 ==========
# 数据集目录（包含CIF文件和id_prop.csv）
DATA_DIR="./your_dataset"

# 分类阈值（大于该值为1类，小于等于为0类）
THRESHOLD=0.5

# ========== 可选参数 ==========
# 配置文件路径
CONFIG_FILE="./config_binary_classification.json"

# 输出目录
OUTPUT_DIR="./classification_results"

# 结构文件格式（cif/poscar/xyz/pdb）
FILE_FORMAT="cif"

# 批次大小（根据GPU内存调整，常用：16, 32, 64）
BATCH_SIZE=32

# 训练轮数
EPOCHS=300

# ========== 开始训练 ==========
echo "======================================"
echo "ALIGNN 二分类训练"
echo "======================================"
echo "数据目录: $DATA_DIR"
echo "分类阈值: $THRESHOLD"
echo "输出目录: $OUTPUT_DIR"
echo "批次大小: $BATCH_SIZE"
echo "训练轮数: $EPOCHS"
echo "======================================"
echo ""

# 检查数据目录是否存在
if [ ! -d "$DATA_DIR" ]; then
    echo "错误: 数据目录不存在: $DATA_DIR"
    echo "请修改脚本中的 DATA_DIR 变量"
    exit 1
fi

# 检查id_prop.csv是否存在
if [ ! -f "$DATA_DIR/id_prop.csv" ]; then
    echo "错误: 找不到 id_prop.csv 文件"
    echo "请确保 $DATA_DIR 目录下有 id_prop.csv 文件"
    exit 1
fi

# 显示数据文件信息
echo "数据文件检查:"
echo "- id_prop.csv 前5行:"
head -n 5 "$DATA_DIR/id_prop.csv"
echo ""
echo "- CIF文件数量:"
ls "$DATA_DIR"/*.cif 2>/dev/null | wc -l
echo ""

# 运行训练
echo "开始训练..."
echo ""

train_alignn.py \
    --root_dir "$DATA_DIR" \
    --config "$CONFIG_FILE" \
    --classification_threshold "$THRESHOLD" \
    --file_format "$FILE_FORMAT" \
    --batch_size "$BATCH_SIZE" \
    --epochs "$EPOCHS" \
    --output_dir "$OUTPUT_DIR"

# 检查训练是否成功
if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "训练完成！"
    echo "======================================"
    echo "结果保存在: $OUTPUT_DIR"
    echo ""
    echo "主要输出文件:"
    echo "- best_model.pt: 最佳模型"
    echo "- prediction_results_test_set.csv: 测试集预测结果"
    echo "- history_train.json: 训练历史"
    echo "- history_val.json: 验证历史"
    echo ""

    # 如果存在预测结果，显示前几行
    if [ -f "$OUTPUT_DIR/prediction_results_test_set.csv" ]; then
        echo "测试集预测结果（前10行）:"
        head -n 10 "$OUTPUT_DIR/prediction_results_test_set.csv"
    fi
else
    echo ""
    echo "======================================"
    echo "训练失败，请检查错误信息"
    echo "======================================"
    exit 1
fi
