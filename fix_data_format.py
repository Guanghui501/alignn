#!/usr/bin/env python
"""
修复 ALIGNN 数据格式
自动修复 id_prop.csv 并验证 CIF 文件
"""
import os
import sys
import glob
import pandas as pd
from pathlib import Path
import shutil

def fix_id_prop_csv(data_dir):
    """修复 id_prop.csv 格式"""
    csv_path = os.path.join(data_dir, "id_prop.csv")

    print("=" * 60)
    print("修复 id_prop.csv")
    print("=" * 60)

    if not os.path.exists(csv_path):
        print(f"❌ 错误: 找不到 {csv_path}")
        return False

    # 备份原文件
    backup_path = csv_path + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy(csv_path, backup_path)
        print(f"✓ 已备份到: {backup_path}")

    # 读取原始文件
    print(f"\n读取原始文件...")
    with open(csv_path, 'r') as f:
        lines = f.readlines()

    print(f"原始文件前5行:")
    for i, line in enumerate(lines[:5], 1):
        print(f"  {i}. {line.strip()}")

    # 检查是否有header
    first_line = lines[0].strip()
    has_header = ('id' in first_line.lower() and 'target' in first_line.lower())

    # 解析数据
    data = []
    start_idx = 1 if has_header else 0

    for line in lines[start_idx:]:
        line = line.strip()
        if not line:
            continue

        parts = line.split(',')
        if len(parts) != 2:
            print(f"⚠️  跳过格式错误的行: {line}")
            continue

        # 去掉 .cif 后缀
        file_id = parts[0].replace('.cif', '').strip()
        target = parts[1].strip()

        data.append([file_id, target])

    # 创建DataFrame
    df = pd.DataFrame(data, columns=['id', 'target'])

    # 转换target为数值
    try:
        df['target'] = pd.to_numeric(df['target'])
    except Exception as e:
        print(f"❌ 错误: target列包含非数值: {e}")
        return False

    # 保存修复后的文件
    df.to_csv(csv_path, index=False)
    print(f"\n✓ 已修复 id_prop.csv")
    print(f"  总行数: {len(df)}")
    print(f"\n修复后的前5行:")
    print(df.head())

    return True, df


def check_cif_files(data_dir, df):
    """检查CIF文件并验证可读性"""
    print("\n" + "=" * 60)
    print("检查 CIF 文件")
    print("=" * 60)

    # 查找CIF文件
    cif_files = glob.glob(os.path.join(data_dir, "*.cif"))
    print(f"\n找到 {len(cif_files)} 个 CIF 文件")

    if len(cif_files) == 0:
        print(f"❌ 错误: 在 {data_dir} 中没有找到 CIF 文件")
        return False

    # 创建文件名映射
    cif_basenames = {os.path.splitext(os.path.basename(f))[0]: f for f in cif_files}

    # 检查匹配
    missing_files = []
    for file_id in df['id']:
        if str(file_id) not in cif_basenames:
            missing_files.append(file_id)

    if missing_files:
        print(f"\n⚠️  {len(missing_files)} 个ID找不到对应的CIF文件:")
        for fid in missing_files[:10]:
            print(f"  - {fid}.cif")
        if len(missing_files) > 10:
            print(f"  ... 还有 {len(missing_files)-10} 个")
    else:
        print(f"\n✓ 所有ID都有对应的CIF文件")

    # 测试读取CIF文件
    print(f"\n测试读取CIF文件...")
    test_files = list(cif_basenames.values())[:10]

    readable_count = 0
    unreadable_files = []

    for cif_file in test_files:
        try:
            # 尝试读取文件
            from jarvis.core.atoms import Atoms
            atoms = Atoms.from_cif(cif_file)
            readable_count += 1
        except Exception as e:
            unreadable_files.append((os.path.basename(cif_file), str(e)))

    print(f"  可读取: {readable_count}/{len(test_files)}")

    if unreadable_files:
        print(f"\n⚠️  以下文件无法读取:")
        for fname, error in unreadable_files:
            print(f"  - {fname}: {error[:80]}")

        print(f"\n这可能意味着:")
        print(f"  1. CIF文件格式不完整或损坏")
        print(f"  2. 缺少原子坐标信息")
        print(f"  3. 需要安装 cif2cell: conda install -c conda-forge cif2cell")

        # 询问是否移除无法读取的文件
        response = input(f"\n是否从 id_prop.csv 中移除无法读取的文件? (y/n): ")
        if response.lower() == 'y':
            # 提取无法读取的ID
            bad_ids = [fname.replace('.cif', '') for fname, _ in unreadable_files]

            # 从DataFrame中移除
            df_clean = df[~df['id'].astype(str).isin(bad_ids)]

            csv_path = os.path.join(data_dir, "id_prop.csv")
            df_clean.to_csv(csv_path, index=False)

            print(f"  ✓ 已移除 {len(df) - len(df_clean)} 条记录")
            print(f"  剩余: {len(df_clean)} 条记录")

            return True, df_clean
    else:
        print(f"  ✓ 所有测试文件都可以正常读取")

    return True, df


def main(data_dir):
    """主函数"""
    print("=" * 60)
    print("ALIGNN 数据格式自动修复工具")
    print("=" * 60)
    print(f"\n数据目录: {data_dir}\n")

    if not os.path.exists(data_dir):
        print(f"❌ 错误: 目录不存在: {data_dir}")
        return False

    # 修复 id_prop.csv
    result = fix_id_prop_csv(data_dir)
    if not result:
        return False

    success, df = result

    # 检查CIF文件
    result = check_cif_files(data_dir, df)
    if not result:
        return False

    success, df = result

    # 显示统计信息
    print("\n" + "=" * 60)
    print("数据统计")
    print("=" * 60)
    print(f"总样本数: {len(df)}")
    print(f"\n目标值统计:")
    print(df['target'].describe())

    # 分类阈值建议
    print(f"\n分类阈值建议:")
    median = df['target'].median()
    mean = df['target'].mean()

    for threshold in [0.5, median, mean]:
        class_0 = (df['target'] <= threshold).sum()
        class_1 = (df['target'] > threshold).sum()
        print(f"\n  阈值 {threshold:.4f}:")
        print(f"    类别0 (≤): {class_0} ({class_0/len(df)*100:.1f}%)")
        print(f"    类别1 (>):  {class_1} ({class_1/len(df)*100:.1f}%)")

    print("\n" + "=" * 60)
    print("✅ 数据修复完成！")
    print("=" * 60)
    print("\n现在可以开始训练:")
    print(f"  ./run_binary_classification.sh")

    return True


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        # 尝试查找数据目录
        if os.path.exists("./data/cif"):
            data_dir = "./data/cif"
        elif os.path.exists("./data"):
            data_dir = "./data"
        else:
            print("用法: python fix_data_format.py <data_directory>")
            sys.exit(1)

    success = main(data_dir)
    sys.exit(0 if success else 1)
