#!/usr/bin/env python
"""
专门修复 id_prop.csv 格式问题
确保符合 ALIGNN 的要求
"""
import os
import sys
import pandas as pd
import shutil

def fix_id_prop_csv(csv_path):
    """
    修复 id_prop.csv 格式

    要求:
    1. 必须有 header: id,target
    2. id 列不能包含 .cif 后缀
    3. target 列必须是数值
    """

    print("=" * 70)
    print("id_prop.csv 格式修复工具")
    print("=" * 70)
    print(f"\n文件路径: {csv_path}\n")

    if not os.path.exists(csv_path):
        print(f"❌ 错误: 文件不存在: {csv_path}")
        return False

    # 备份原文件
    backup_path = csv_path + ".backup"
    if not os.path.exists(backup_path):
        shutil.copy(csv_path, backup_path)
        print(f"✓ 已备份原文件到: {backup_path}")

    # 读取原始文件
    print("\n步骤1: 读取原始文件...")
    with open(csv_path, 'r') as f:
        lines = f.readlines()

    print(f"原始文件前5行:")
    for i, line in enumerate(lines[:5], 1):
        print(f"  {i}. {line.strip()}")

    # 检查第一行是否是 header
    first_line = lines[0].strip().lower()
    has_header = 'id' in first_line and 'target' in first_line

    if has_header:
        print("\n✓ 检测到 header 行")
    else:
        print("\n⚠️  未检测到 header 行")

    # 解析数据
    print("\n步骤2: 解析数据...")
    data_rows = []

    start_line = 1 if has_header else 0

    for line_num, line in enumerate(lines[start_line:], start_line+1):
        line = line.strip()
        if not line:
            continue

        parts = line.split(',')

        if len(parts) != 2:
            print(f"  ⚠️  跳过格式错误的行 {line_num}: {line}")
            continue

        file_id = parts[0].strip()
        target_val = parts[1].strip()

        # 移除 .cif 后缀
        if file_id.endswith('.cif'):
            file_id = file_id[:-4]

        data_rows.append([file_id, target_val])

    print(f"  解析了 {len(data_rows)} 行数据")

    # 创建 DataFrame
    print("\n步骤3: 创建标准格式...")
    df = pd.DataFrame(data_rows, columns=['id', 'target'])

    # 转换 target 为数值
    try:
        df['target'] = pd.to_numeric(df['target'])
        print(f"  ✓ target 列成功转换为数值类型")
    except Exception as e:
        print(f"  ❌ 错误: target 列包含非数值: {e}")
        print(f"  前5个值: {df['target'].head().tolist()}")
        return False

    # 检查 id 列
    if df['id'].str.contains('.cif').any():
        print(f"  ⚠️  警告: 仍有 {df['id'].str.contains('.cif').sum()} 个 id 包含 .cif")

    # 保存修复后的文件
    print("\n步骤4: 保存修复后的文件...")
    df.to_csv(csv_path, index=False)
    print(f"  ✓ 已保存到: {csv_path}")

    # 显示结果
    print("\n" + "=" * 70)
    print("修复结果")
    print("=" * 70)
    print(f"总行数: {len(df)}")
    print(f"\n修复后的前10行:")
    print(df.head(10).to_string(index=False))

    # 统计信息
    print(f"\ntarget 列统计:")
    print(df['target'].describe())

    # 验证格式
    print("\n" + "=" * 70)
    print("格式验证")
    print("=" * 70)

    # 重新读取验证
    try:
        df_verify = pd.read_csv(csv_path)

        checks = []
        checks.append(('列名正确', set(df_verify.columns) == {'id', 'target'}))
        checks.append(('有数据', len(df_verify) > 0))
        checks.append(('id列无空值', not df_verify['id'].isna().any()))
        checks.append(('target列无空值', not df_verify['target'].isna().any()))
        checks.append(('target列是数值', pd.api.types.is_numeric_dtype(df_verify['target'])))
        checks.append(('id列无.cif后缀', not df_verify['id'].astype(str).str.contains('.cif').any()))

        all_pass = True
        for check_name, check_result in checks:
            status = "✓" if check_result else "✗"
            print(f"  {status} {check_name}")
            if not check_result:
                all_pass = False

        if all_pass:
            print("\n✅ 格式验证通过！")
            print("\n现在可以开始训练:")
            print(f"  train_alignn.py --root_dir {os.path.dirname(csv_path)} \\")
            print(f"                  --config config_large_dataset.json \\")
            print(f"                  --classification_threshold 0.5 \\")
            print(f"                  --batch_size 128 --epochs 100")
            return True
        else:
            print("\n⚠️  部分检查未通过，请手动检查文件")
            return False

    except Exception as e:
        print(f"\n❌ 验证失败: {e}")
        return False


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='修复 id_prop.csv 格式')
    parser.add_argument('csv_path', nargs='?', help='id_prop.csv 文件路径')

    args = parser.parse_args()

    # 确定文件路径
    if args.csv_path:
        csv_path = args.csv_path
    else:
        # 自动检测
        possible_paths = [
            './data/cif/id_prop.csv',
            './data/id_prop.csv',
            './id_prop.csv',
        ]

        csv_path = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_path = path
                break

        if not csv_path:
            print("错误: 找不到 id_prop.csv")
            print("请指定文件路径:")
            print("  python fix_id_prop_csv.py /path/to/id_prop.csv")
            print("\n或将文件放在以下位置之一:")
            for path in possible_paths:
                print(f"  - {path}")
            sys.exit(1)

    success = fix_id_prop_csv(csv_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
