#!/usr/bin/env python
"""
多线程 CIF 文件检查工具
使用多线程大幅加速文件检查过程
"""
import os
import sys
import glob
import pandas as pd
from pathlib import Path
import shutil
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed
from multiprocessing import cpu_count
import argparse

def check_single_cif(cif_file):
    """
    检查单个 CIF 文件
    返回: (file_path, is_good, error_message)
    """
    try:
        from jarvis.core.atoms import Atoms
        atoms = Atoms.from_cif(cif_file)

        # 检查是否有原子
        if len(atoms.cart_coords) == 0:
            return (cif_file, False, "没有原子坐标")
        else:
            return (cif_file, True, None)
    except Exception as e:
        error_msg = str(e)[:100]
        return (cif_file, False, error_msg)


def check_cif_files_parallel(data_dir, num_workers=None, remove_bad=False):
    """
    并行检查所有 CIF 文件

    Args:
        data_dir: 数据目录
        num_workers: 线程数，默认为 CPU 核心数
        remove_bad: 是否自动移动问题文件
    """

    print("=" * 70)
    print("CIF 文件完整性检查工具（多线程加速版）")
    print("=" * 70)
    print(f"\n数据目录: {data_dir}")

    # 确定线程数
    if num_workers is None:
        num_workers = cpu_count()

    print(f"使用线程数: {num_workers}")
    print()

    # 查找所有 CIF 文件
    print("步骤1: 搜索 CIF 文件...")
    cif_files = glob.glob(os.path.join(data_dir, "*.cif"))

    if len(cif_files) == 0:
        print(f"❌ 错误: 在 {data_dir} 中没有找到 CIF 文件")
        return False

    print(f"✓ 找到 {len(cif_files)} 个 CIF 文件\n")

    # 多线程检查
    print("步骤2: 并行检查所有 CIF 文件...")
    print("这可能需要几分钟，请耐心等待...\n")

    good_files = []
    bad_files = []

    # 使用线程池并行处理
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        # 提交所有任务
        futures = {executor.submit(check_single_cif, f): f for f in cif_files}

        # 使用 tqdm 显示进度
        with tqdm(total=len(cif_files), desc="检查进度") as pbar:
            for future in as_completed(futures):
                file_path, is_good, error_msg = future.result()

                if is_good:
                    good_files.append(file_path)
                else:
                    bad_files.append((file_path, error_msg))

                pbar.update(1)

    # 显示结果
    print("\n" + "=" * 70)
    print("检查结果")
    print("=" * 70)
    total = len(cif_files)
    good_pct = len(good_files) / total * 100
    bad_pct = len(bad_files) / total * 100

    print(f"✓ 可读取的文件: {len(good_files)} ({good_pct:.1f}%)")
    print(f"✗ 无法读取的文件: {len(bad_files)} ({bad_pct:.1f}%)")

    if len(bad_files) > 0:
        print(f"\n无法读取的文件列表（前20个）:")
        print("-" * 70)
        for i, (fpath, error) in enumerate(sorted(bad_files)[:20], 1):
            fname = os.path.basename(fpath)
            print(f"{i:3d}. {fname:30s} | {error}")

        if len(bad_files) > 20:
            print(f"     ... 还有 {len(bad_files)-20} 个文件")

        # 保存完整的问题文件列表
        bad_list_file = os.path.join(data_dir, "bad_cif_files.txt")
        with open(bad_list_file, 'w') as f:
            f.write("# 无法读取的 CIF 文件列表\n")
            f.write(f"# 总计: {len(bad_files)} 个文件\n")
            f.write(f"# 检查时间: {pd.Timestamp.now()}\n\n")
            for fpath, error in sorted(bad_files):
                fname = os.path.basename(fpath)
                f.write(f"{fname}\t{error}\n")

        print(f"\n完整列表已保存到: {bad_list_file}")

        # 询问是否处理问题文件
        if remove_bad:
            action = 'move'
        else:
            print("\n" + "=" * 70)
            print("处理选项:")
            print("=" * 70)
            print("1. 移动到单独的目录 (推荐) - 保留文件但不参与训练")
            print("2. 删除这些文件 - 永久删除")
            print("3. 保留不处理 - 训练时可能会出错")
            print()
            choice = input("请选择 (1/2/3): ").strip()

            if choice == '1':
                action = 'move'
            elif choice == '2':
                action = 'delete'
            else:
                action = 'keep'
                print("\n⚠️  保留问题文件，训练时可能会遇到错误")

        if action == 'move':
            # 创建备份目录
            bad_dir = os.path.join(data_dir, "bad_cif_files")
            os.makedirs(bad_dir, exist_ok=True)

            print(f"\n移动问题文件到: {bad_dir}")
            for fpath, _ in tqdm(bad_files, desc="移动进度"):
                fname = os.path.basename(fpath)
                dest = os.path.join(bad_dir, fname)
                shutil.move(fpath, dest)

            print(f"✓ 已移动 {len(bad_files)} 个文件")

        elif action == 'delete':
            confirm = input(f"\n⚠️  确认删除 {len(bad_files)} 个文件? (yes/no): ").strip().lower()
            if confirm == 'yes':
                print("\n删除问题文件...")
                for fpath, _ in tqdm(bad_files, desc="删除进度"):
                    os.remove(fpath)
                print(f"✓ 已删除 {len(bad_files)} 个文件")
            else:
                print("取消删除")
                action = 'keep'

        # 如果移动或删除了文件，需要更新 id_prop.csv
        if action in ['move', 'delete']:
            print("\n步骤3: 更新 id_prop.csv...")

            # 读取 id_prop.csv
            csv_path = os.path.join(data_dir, "id_prop.csv")
            if os.path.exists(csv_path):
                # 备份
                backup_path = csv_path + ".backup_cif_check"
                if not os.path.exists(backup_path):
                    shutil.copy(csv_path, backup_path)
                    print(f"  ✓ 已备份到: {backup_path}")

                # 读取 CSV
                try:
                    # 尝试不同的读取方式
                    try:
                        df = pd.read_csv(csv_path)
                    except:
                        df = pd.read_csv(csv_path, header=None)
                        if len(df.columns) == 2:
                            df.columns = ['id', 'target']

                    # 获取要移除的文件ID
                    bad_ids = set()
                    for fpath, _ in bad_files:
                        fname = os.path.basename(fpath)
                        # 移除 .cif 后缀
                        file_id = fname.replace('.cif', '')
                        bad_ids.add(file_id)

                    # 过滤DataFrame
                    original_len = len(df)

                    # 处理id列，移除可能的 .cif 后缀
                    if 'id' in df.columns:
                        id_col = 'id'
                    else:
                        id_col = df.columns[0]

                    df[id_col] = df[id_col].astype(str).str.replace('.cif', '')
                    df_clean = df[~df[id_col].isin(bad_ids)]

                    # 保存
                    df_clean.to_csv(csv_path, index=False, header=True)

                    removed_count = original_len - len(df_clean)
                    print(f"  ✓ 已从 id_prop.csv 移除 {removed_count} 条记录")
                    print(f"  剩余: {len(df_clean)} 条记录")

                except Exception as e:
                    print(f"  ⚠️  警告: 无法自动更新 id_prop.csv: {e}")
                    print(f"  请手动移除这些ID")
            else:
                print(f"  ⚠️  未找到 id_prop.csv")

    else:
        print("\n🎉 所有 CIF 文件都可以正常读取！")

    # 最终统计
    remaining_cif = glob.glob(os.path.join(data_dir, "*.cif"))

    print("\n" + "=" * 70)
    print("最终统计")
    print("=" * 70)
    print(f"可用的 CIF 文件: {len(remaining_cif)}")
    print(f"数据目录: {data_dir}")

    if os.path.exists(os.path.join(data_dir, "id_prop.csv")):
        try:
            df = pd.read_csv(os.path.join(data_dir, "id_prop.csv"))
            print(f"id_prop.csv 记录数: {len(df)}")
        except:
            pass

    print("\n" + "=" * 70)
    print("✅ CIF 文件检查完成！")
    print("=" * 70)

    if len(bad_files) == 0 or action in ['move', 'delete']:
        print("\n现在可以开始训练:")
        print(f"  train_alignn.py --root_dir {data_dir} --config config_large_dataset.json \\")
        print(f"                  --classification_threshold 0.5 --batch_size 128 --epochs 100")

    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='多线程检查 CIF 文件可读性',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 使用默认线程数（CPU核心数）
  python check_cif_files_fast.py ./data/cif

  # 指定16个线程
  python check_cif_files_fast.py ./data/cif --workers 16

  # 自动模式（自动移动问题文件）
  python check_cif_files_fast.py ./data/cif --remove-bad --workers 32

  # 自动检测数据目录
  python check_cif_files_fast.py --remove-bad
        """
    )

    parser.add_argument('data_dir', nargs='?', default=None,
                       help='数据目录路径')
    parser.add_argument('--workers', '-w', type=int, default=None,
                       help=f'线程数 (默认: CPU核心数 = {cpu_count()})')
    parser.add_argument('--remove-bad', action='store_true',
                       help='自动移动无法读取的文件到单独目录')

    args = parser.parse_args()

    # 确定数据目录
    if args.data_dir:
        data_dir = args.data_dir
    else:
        # 自动检测
        if os.path.exists("./data/cif"):
            data_dir = "./data/cif"
        elif os.path.exists("./data"):
            data_dir = "./data"
        else:
            print("错误: 请指定数据目录")
            print("用法: python check_cif_files_fast.py <data_directory>")
            print("或将数据放在 ./data 或 ./data/cif 目录下")
            sys.exit(1)

    if not os.path.exists(data_dir):
        print(f"错误: 目录不存在: {data_dir}")
        sys.exit(1)

    # 显示性能提示
    num_workers = args.workers if args.workers else cpu_count()
    print(f"\n💡 性能提示:")
    print(f"   - CPU 核心数: {cpu_count()}")
    print(f"   - 使用线程数: {num_workers}")
    print(f"   - 预计速度提升: {num_workers}x (相比单线程)")
    print(f"   - 对于 100k+ 文件，预计耗时: {int(15 / num_workers * 10)} 分钟\n")

    success = check_cif_files_parallel(data_dir,
                                       num_workers=args.workers,
                                       remove_bad=args.remove_bad)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
