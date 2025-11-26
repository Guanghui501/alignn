#!/bin/bash
# 一键修复并启动训练

DATA_DIR="./data/cif-2"

echo "======================================"
echo "一键修复并启动 ALIGNN 训练"
echo "======================================"
echo ""

# 1. 修复 id_prop.csv
echo "步骤1: 修复 id_prop.csv 格式..."

python << 'PYTHON_EOF'
import os
import glob

data_dir = './data/cif-2'

# 获取所有 CIF 文件
cif_files = sorted(glob.glob(os.path.join(data_dir, '*.cif')))

if len(cif_files) == 0:
    print("❌ 错误: 没有找到 CIF 文件")
    exit(1)

print(f"找到 {len(cif_files)} 个 CIF 文件")

# 生成 id_prop.csv
csv_path = os.path.join(data_dir, 'id_prop.csv')

with open(csv_path, 'w') as f:
    # 写入 header
    f.write('id,target\n')

    # 为每个 CIF 文件写入一行
    for cif_file in cif_files:
        # 获取文件名（不含扩展名）
        basename = os.path.basename(cif_file)
        file_id = os.path.splitext(basename)[0]

        # 默认 target 为 1（您可以修改）
        target = 1

        f.write(f'{file_id},{target}\n')

print(f"✓ 已创建 {csv_path}")
print(f"  总行数: {len(cif_files) + 1} (含 header)")

# 显示内容
print("\n前5行:")
with open(csv_path, 'r') as f:
    for i, line in enumerate(f):
        if i < 5:
            print(f"  {line.strip()}")

print("\n✓ id_prop.csv 格式正确！")
PYTHON_EOF

if [ $? -ne 0 ]; then
    echo "修复失败"
    exit 1
fi

# 2. 验证
echo ""
echo "步骤2: 验证数据..."
head -3 $DATA_DIR/id_prop.csv

# 3. 开始训练
echo ""
echo "======================================"
echo "步骤3: 开始训练"
echo "======================================"
echo ""

train_alignn.py \
    --root_dir "$DATA_DIR" \
    --config config_test_10samples.json \
    --output_dir ./test_results

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================"
    echo "✅ 训练完成！"
    echo "======================================"
    echo "结果保存在: ./test_results"
else
    echo ""
    echo "======================================"
    echo "❌ 训练失败"
    echo "======================================"
fi
