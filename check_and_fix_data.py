#!/usr/bin/env python
"""
检查和修复ALIGNN数据格式
"""
import os
import sys
import glob
import pandas as pd
from pathlib import Path

def check_and_fix_data(data_dir):
    """检查并修复数据格式"""

    print("=" * 60)
    print("ALIGNN 数据格式检查和修复工具")
    print("=" * 60)
    print(f"\n数据目录: {data_dir}\n")

    # 检查目录是否存在
    if not os.path.exists(data_dir):
        print(f"❌ 错误: 目录不存在: {data_dir}")
        return False

    # 检查id_prop.csv
    csv_path = os.path.join(data_dir, "id_prop.csv")
    if not os.path.exists(csv_path):
        print(f"❌ 错误: 找不到 id_prop.csv")
        return False

    print("📄 检查 id_prop.csv...")

    # 读取CSV
    try:
        # 先看看原始内容
        with open(csv_path, 'r') as f:
            first_lines = [f.readline().strip() for _ in range(5)]

        print(f"\n当前文件前5行:")
        for i, line in enumerate(first_lines, 1):
            print(f"  {i}. {line}")

        # 尝试读取
        df = pd.read_csv(csv_path, header=None)

        # 检查格式
        has_header = False
        if df.iloc[0, 0] == 'id' or 'id' in str(df.iloc[0, 0]).lower():
            has_header = True
            df = pd.read_csv(csv_path)
        else:
            # 没有header，添加列名
            if df.shape[1] == 2:
                df.columns = ['id', 'target']
            else:
                print(f"❌ 错误: CSV文件应该有2列，但有{df.shape[1]}列")
                return False

        print(f"\n✓ CSV文件包含 {len(df)} 行数据")
        print(f"✓ 列名: {list(df.columns)}")

        # 检查id列是否包含.cif后缀
        needs_fixing = False
        if df.iloc[0, 0].endswith('.cif'):
            print("\n⚠️  警告: ID列包含 .cif 后缀")
            needs_fixing = True

        # 检查是否有header
        if not has_header:
            print("⚠️  警告: 缺少列名header")
            needs_fixing = True

        if needs_fixing:
            print("\n🔧 修复 id_prop.csv...")

            # 备份原文件
            backup_path = csv_path + ".backup"
            import shutil
            shutil.copy(csv_path, backup_path)
            print(f"   备份原文件到: {backup_path}")

            # 修复ID列（去掉.cif后缀）
            if df.columns[0] in ['id', '0'] or 'id' in str(df.columns[0]).lower():
                id_col = df.columns[0]
                df[id_col] = df[id_col].apply(lambda x: str(x).replace('.cif', ''))

            # 确保有正确的列名
            df.columns = ['id', 'target']

            # 保存修复后的文件
            df.to_csv(csv_path, index=False)
            print(f"   ✓ 已修复 id_prop.csv")

            # 显示修复后的内容
            print(f"\n修复后的前5行:")
            print(df.head())
        else:
            print("\n✓ id_prop.csv 格式正确")
            print(f"\n前5行数据:")
            print(df.head())

    except Exception as e:
        print(f"❌ 读取CSV文件出错: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 检查CIF文件
    print(f"\n📁 检查CIF文件...")

    cif_files = glob.glob(os.path.join(data_dir, "*.cif"))
    print(f"   找到 {len(cif_files)} 个 .cif 文件")

    if len(cif_files) == 0:
        print("\n⚠️  警告: 没有找到CIF文件！")
        print(f"   请确保CIF文件在目录: {data_dir}")
        print(f"\n   正在搜索子目录...")

        # 搜索子目录
        all_cif = glob.glob(os.path.join(data_dir, "**/*.cif"), recursive=True)
        if len(all_cif) > 0:
            print(f"\n   在子目录中找到 {len(all_cif)} 个CIF文件:")
            # 统计每个子目录的文件数
            subdirs = {}
            for f in all_cif[:10]:  # 只显示前10个
                subdir = os.path.dirname(f)
                subdirs[subdir] = subdirs.get(subdir, 0) + 1
                print(f"     - {f}")

            if len(all_cif) > 10:
                print(f"     ... 还有 {len(all_cif) - 10} 个文件")

            print(f"\n   💡 建议: 将所有CIF文件移动到 {data_dir} 目录")

            # 询问是否移动文件
            response = input("\n是否将CIF文件移动到数据目录? (y/n): ")
            if response.lower() == 'y':
                import shutil
                for cif_file in all_cif:
                    filename = os.path.basename(cif_file)
                    dest = os.path.join(data_dir, filename)
                    if not os.path.exists(dest):
                        shutil.copy(cif_file, dest)
                        print(f"   复制: {filename}")

                cif_files = glob.glob(os.path.join(data_dir, "*.cif"))
                print(f"\n   ✓ 已复制 {len(cif_files)} 个文件")
        else:
            print(f"\n   ❌ 在整个目录树中都没有找到CIF文件")
            return False
    else:
        print(f"   ✓ CIF文件示例:")
        for f in cif_files[:5]:
            print(f"     - {os.path.basename(f)}")
        if len(cif_files) > 5:
            print(f"     ... 还有 {len(cif_files) - 5} 个文件")

    # 检查id_prop.csv中的ID是否都有对应的CIF文件
    print(f"\n🔍 检查数据完整性...")

    cif_basenames = {os.path.splitext(os.path.basename(f))[0] for f in cif_files}

    missing_files = []
    for idx, row in df.iterrows():
        file_id = str(row['id'])
        if file_id not in cif_basenames:
            missing_files.append(file_id)

    if missing_files:
        print(f"\n⚠️  警告: {len(missing_files)} 个ID在id_prop.csv中但找不到对应的CIF文件:")
        for fid in missing_files[:10]:
            print(f"     - {fid}.cif (缺失)")
        if len(missing_files) > 10:
            print(f"     ... 还有 {len(missing_files) - 10} 个缺失")
    else:
        print(f"   ✓ 所有ID都有对应的CIF文件")

    # 统计信息
    print(f"\n" + "=" * 60)
    print("📊 数据集统计:")
    print("=" * 60)
    print(f"总样本数: {len(df)}")
    print(f"CIF文件数: {len(cif_files)}")
    print(f"缺失文件: {len(missing_files)}")
    print(f"\n目标值统计:")
    print(df['target'].describe())

    # 分类阈值建议
    print(f"\n💡 分类阈值建议:")
    median = df['target'].median()
    mean = df['target'].mean()
    print(f"   - 中位数: {median:.4f}")
    print(f"   - 平均值: {mean:.4f}")

    for threshold in [0.5, median, mean]:
        class_0 = (df['target'] <= threshold).sum()
        class_1 = (df['target'] > threshold).sum()
        print(f"\n   阈值 {threshold:.4f}:")
        print(f"     类别0 (≤ {threshold:.4f}): {class_0} ({class_0/len(df)*100:.1f}%)")
        print(f"     类别1 (> {threshold:.4f}): {class_1} ({class_1/len(df)*100:.1f}%)")

    print(f"\n" + "=" * 60)
    print("✅ 数据检查完成！")
    print("=" * 60)

    if len(missing_files) == 0 and len(cif_files) > 0:
        print("\n🎉 数据格式正确，可以开始训练！")
        return True
    else:
        print("\n⚠️  请修复上述问题后再开始训练")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        data_dir = sys.argv[1]
    else:
        data_dir = "./data"

    success = check_and_fix_data(data_dir)

    if success:
        print("\n下一步: 运行训练脚本")
        print("  ./run_binary_classification.sh")

    sys.exit(0 if success else 1)
