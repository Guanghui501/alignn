#!/usr/bin/env python
"""
ALIGNN 二分类训练示例脚本
使用Python API进行训练
"""

from alignn.config import TrainingConfig
from alignn.train import train_dgl

# ========== 配置参数 ==========

# 数据集配置
ROOT_DIR = "./your_dataset"  # 包含CIF文件和id_prop.csv的目录
CLASSIFICATION_THRESHOLD = 0.5  # 分类阈值

# 训练配置
config = TrainingConfig(
    # 数据集设置
    dataset="user_data",
    target="target",
    id_tag="id",

    # 分类设置
    classification_threshold=CLASSIFICATION_THRESHOLD,

    # 数据划分
    train_ratio=0.8,
    val_ratio=0.1,
    test_ratio=0.1,

    # 训练参数
    random_seed=123,
    epochs=300,
    batch_size=32,
    learning_rate=0.001,

    # 优化器和调度器
    optimizer="adamw",
    scheduler="onecycle",

    # 特征设置
    atom_features="cgcnn",
    neighbor_strategy="k-nearest",
    cutoff=8.0,
    max_neighbors=12,

    # 输出设置
    output_dir="./classification_results",
    write_predictions=True,

    # 性能设置
    num_workers=4,
    use_lmdb=True,

    # 模型配置
    model={
        "name": "alignn",
        "alignn_layers": 4,
        "gcn_layers": 4,
        "atom_input_features": 92,
        "edge_input_features": 80,
        "triplet_input_features": 40,
        "embedding_features": 64,
        "hidden_features": 256,
        "output_features": 2,  # 二分类
        "classification": True,
    }
)

# ========== 主函数 ==========

def main():
    """主训练函数"""
    import os

    print("=" * 50)
    print("ALIGNN 二分类训练")
    print("=" * 50)

    # 检查数据目录
    if not os.path.exists(ROOT_DIR):
        print(f"错误: 数据目录不存在: {ROOT_DIR}")
        print("请修改脚本中的 ROOT_DIR 变量")
        return

    # 检查id_prop.csv
    id_prop_path = os.path.join(ROOT_DIR, "id_prop.csv")
    if not os.path.exists(id_prop_path):
        print(f"错误: 找不到 id_prop.csv 文件")
        print(f"请确保 {ROOT_DIR} 目录下有 id_prop.csv 文件")
        return

    # 显示配置信息
    print(f"\n配置信息:")
    print(f"- 数据目录: {ROOT_DIR}")
    print(f"- 分类阈值: {CLASSIFICATION_THRESHOLD}")
    print(f"- 训练轮数: {config.epochs}")
    print(f"- 批次大小: {config.batch_size}")
    print(f"- 学习率: {config.learning_rate}")
    print(f"- 输出目录: {config.output_dir}")
    print(f"- 数据划分: 训练{config.train_ratio} / 验证{config.val_ratio} / 测试{config.test_ratio}")

    # 显示数据信息
    import pandas as pd
    try:
        df = pd.read_csv(id_prop_path)
        print(f"\n数据集信息:")
        print(f"- 总样本数: {len(df)}")
        print(f"- id_prop.csv 前5行:")
        print(df.head())

        # 统计阈值分布
        if 'target' in df.columns:
            class_0 = (df['target'] <= CLASSIFICATION_THRESHOLD).sum()
            class_1 = (df['target'] > CLASSIFICATION_THRESHOLD).sum()
            print(f"\n按阈值 {CLASSIFICATION_THRESHOLD} 分类后:")
            print(f"- 类别0 (≤ {CLASSIFICATION_THRESHOLD}): {class_0} 样本")
            print(f"- 类别1 (> {CLASSIFICATION_THRESHOLD}): {class_1} 样本")
    except Exception as e:
        print(f"警告: 无法读取id_prop.csv: {e}")

    print(f"\n{'=' * 50}")
    print("开始训练...")
    print("=" * 50)
    print()

    # 开始训练
    try:
        train_dgl(config)

        print("\n" + "=" * 50)
        print("训练完成！")
        print("=" * 50)
        print(f"结果保存在: {config.output_dir}")
        print("\n主要输出文件:")
        print("- best_model.pt: 最佳模型")
        print("- prediction_results_test_set.csv: 测试集预测结果")
        print("- history_train.json: 训练历史")
        print("- history_val.json: 验证历史")

        # 显示测试结果
        result_file = os.path.join(config.output_dir, "prediction_results_test_set.csv")
        if os.path.exists(result_file):
            print(f"\n测试集预测结果（前10行）:")
            result_df = pd.read_csv(result_file)
            print(result_df.head(10))

    except Exception as e:
        print("\n" + "=" * 50)
        print("训练失败！")
        print("=" * 50)
        print(f"错误信息: {e}")
        import traceback
        traceback.print_exc()


# ========== 使用示例 ==========

if __name__ == "__main__":
    """
    使用方法:

    1. 修改上面的 ROOT_DIR 变量，指向您的数据目录
    2. 修改 CLASSIFICATION_THRESHOLD 变量，设置分类阈值
    3. 根据需要调整其他参数（epochs、batch_size等）
    4. 运行脚本:
       python train_binary_classification_example.py

    注意事项:
    - 确保数据目录包含 id_prop.csv 文件和 CIF 文件
    - id_prop.csv 格式应为: id,target
    - 根据GPU内存调整 batch_size
    - 训练可能需要较长时间，建议使用GPU
    """

    # 提示用户修改配置
    import sys
    if ROOT_DIR == "./your_dataset":
        print("=" * 50)
        print("警告: 请先修改脚本中的配置参数！")
        print("=" * 50)
        print("\n需要修改的参数:")
        print("1. ROOT_DIR: 您的数据集目录")
        print("2. CLASSIFICATION_THRESHOLD: 分类阈值")
        print("\n其他可选参数:")
        print("- epochs: 训练轮数（默认300）")
        print("- batch_size: 批次大小（默认32）")
        print("- learning_rate: 学习率（默认0.001）")
        print("\n修改后再次运行此脚本")
        print("=" * 50)
        sys.exit(1)

    # 运行训练
    main()
