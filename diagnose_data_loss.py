#!/usr/bin/env python
"""
数据丢失诊断工具
检查为什么数据从 83k+ 降到只有几个样本
"""
import os
import sys
import glob
import pandas as pd
from pathlib import Path

def diagnose_data_loss(data_dir):
    """诊断数据丢失问题"""

    print("=" * 70)
    print("数据丢失诊断工具")
    print("=" * 70)
    print(f"\n数据目录: {data_dir}\n")

    # 1. 检查 id_prop.csv
    print("1️⃣  检查 id_prop.csv")
    print("-" * 70)

    csv_path = os.path.join(data_dir, "id_prop.csv")

    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            print(f"  当前记录数: {len(df)}")
            print(f"  列名: {list(df.columns)}")

            if len(df) < 20:
                print(f"\n  完整内容:")
                print(df.to_string(index=False))
        except Exception as e:
            print(f"  ❌ 读取错误: {e}")
    else:
        print(f"  ❌ 文件不存在: {csv_path}")

    # 2. 检查所有备份文件
    print(f"\n2️⃣  检查备份文件")
    print("-" * 70)

    backup_patterns = [
        "id_prop.csv.backup*",
        "id_prop.csv.bak*",
        "*.backup",
    ]

    all_backups = []
    for pattern in backup_patterns:
        backups = glob.glob(os.path.join(data_dir, pattern))
        all_backups.extend(backups)

    if all_backups:
        print(f"  找到 {len(all_backups)} 个备份文件:\n")
        for backup in sorted(all_backups):
            fname = os.path.basename(backup)
            size = os.path.getsize(backup)

            # 尝试读取行数
            try:
                if 'csv' in fname:
                    with open(backup, 'r') as f:
                        lines = sum(1 for _ in f)
                    print(f"  📄 {fname:40s} | {size:>10,} bytes | {lines:>7,} 行")
                else:
                    print(f"  📄 {fname:40s} | {size:>10,} bytes")
            except:
                print(f"  📄 {fname:40s} | {size:>10,} bytes")
    else:
        print("  ⚠️  没有找到备份文件")

    # 3. 检查 CIF 文件
    print(f"\n3️⃣  检查 CIF 文件")
    print("-" * 70)

    cif_files = glob.glob(os.path.join(data_dir, "*.cif"))
    print(f"  当前目录 CIF 文件数: {len(cif_files)}")

    if len(cif_files) < 20:
        print(f"\n  文件列表:")
        for f in sorted(cif_files):
            print(f"    - {os.path.basename(f)}")

    # 4. 检查 bad_cif_files 目录
    print(f"\n4️⃣  检查 bad_cif_files 目录")
    print("-" * 70)

    bad_dir = os.path.join(data_dir, "bad_cif_files")
    if os.path.exists(bad_dir):
        bad_files = glob.glob(os.path.join(bad_dir, "*.cif"))
        print(f"  移动的文件数: {len(bad_files)}")

        if len(bad_files) > 0:
            print(f"  ⚠️  警告: {len(bad_files)} 个文件被移动到此目录")

            # 检查 bad_cif_files.txt
            txt_file = os.path.join(data_dir, "bad_cif_files.txt")
            if os.path.exists(txt_file):
                print(f"\n  问题文件列表: {txt_file}")
                with open(txt_file, 'r') as f:
                    lines = f.readlines()[:10]
                    for line in lines:
                        if not line.startswith('#'):
                            print(f"    {line.strip()}")
    else:
        print(f"  目录不存在")

    # 5. 搜索其他可能的位置
    print(f"\n5️⃣  搜索其他位置的 CIF 文件")
    print("-" * 70)

    parent_dir = os.path.dirname(data_dir)
    all_cif = glob.glob(os.path.join(parent_dir, "**/*.cif"), recursive=True)

    # 按目录统计
    dir_counts = {}
    for f in all_cif:
        d = os.path.dirname(f)
        dir_counts[d] = dir_counts.get(d, 0) + 1

    if dir_counts:
        print(f"  找到的 CIF 文件分布:\n")
        for d, count in sorted(dir_counts.items(), key=lambda x: -x[1]):
            rel_path = os.path.relpath(d, parent_dir)
            print(f"    {rel_path:50s} : {count:>7,} 文件")

    # 6. 建议
    print(f"\n" + "=" * 70)
    print("💡 诊断结果和建议")
    print("=" * 70)

    current_csv_lines = 0
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            current_csv_lines = len(df)
        except:
            pass

    current_cif_count = len(cif_files)
    bad_cif_count = len(glob.glob(os.path.join(bad_dir, "*.cif"))) if os.path.exists(bad_dir) else 0

    # 找到最大的备份
    largest_backup = None
    largest_backup_lines = 0

    for backup in all_backups:
        if 'csv' in os.path.basename(backup):
            try:
                with open(backup, 'r') as f:
                    lines = sum(1 for _ in f)
                if lines > largest_backup_lines:
                    largest_backup_lines = lines
                    largest_backup = backup
            except:
                pass

    print(f"\n当前状态:")
    print(f"  - id_prop.csv: {current_csv_lines} 行")
    print(f"  - CIF 文件: {current_cif_count} 个")
    print(f"  - bad_cif_files: {bad_cif_count} 个")

    if largest_backup:
        print(f"\n最大的备份:")
        print(f"  - 文件: {os.path.basename(largest_backup)}")
        print(f"  - 行数: {largest_backup_lines}")
        print(f"  - 丢失: {largest_backup_lines - current_csv_lines} 行")

    # 提供恢复建议
    print(f"\n🔧 恢复建议:")

    if largest_backup and largest_backup_lines > current_csv_lines * 10:
        print(f"\n✅ 方案1: 恢复最大的备份（推荐）")
        print(f"   cp {largest_backup} {csv_path}")
        print(f"   python fix_id_prop_csv.py {csv_path}")
        print(f"   # 预计恢复 {largest_backup_lines} 行数据")

    if bad_cif_count > current_cif_count:
        print(f"\n✅ 方案2: 恢复 bad_cif_files 中的文件")
        print(f"   mv {bad_dir}/*.cif {data_dir}/")
        print(f"   # 恢复 {bad_cif_count} 个 CIF 文件")

    # 查找其他可能的数据源
    other_large_dirs = [d for d, c in dir_counts.items()
                       if c > current_cif_count and d != data_dir]

    if other_large_dirs:
        print(f"\n✅ 方案3: 从其他目录复制")
        for d in other_large_dirs[:3]:
            count = dir_counts[d]
            rel_path = os.path.relpath(d, parent_dir)
            print(f"   # {rel_path} 有 {count} 个文件")
            print(f"   # cp {d}/*.cif {data_dir}/")

    print(f"\n" + "=" * 70)

    return current_csv_lines, current_cif_count


def main():
    import argparse

    parser = argparse.ArgumentParser(description='诊断数据丢失问题')
    parser.add_argument('data_dir', nargs='?', help='数据目录')

    args = parser.parse_args()

    if args.data_dir:
        data_dir = args.data_dir
    else:
        # 自动检测
        if os.path.exists('./data/cif'):
            data_dir = './data/cif'
        elif os.path.exists('./data'):
            data_dir = './data'
        else:
            print("请指定数据目录")
            sys.exit(1)

    csv_lines, cif_count = diagnose_data_loss(data_dir)

    if csv_lines < 100 and cif_count < 100:
        print("\n⚠️  警告: 数据严重丢失！")
        print("    请按照上述建议恢复数据")
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()
