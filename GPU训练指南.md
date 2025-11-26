# ALIGNN GPU 训练指南

## 🎯 GPU vs CPU 速度对比

### 训练速度（108,134 样本，100 epochs）

| 硬件配置 | 单个 Epoch 时间 | 总训练时间 (100 epochs) |
|---------|----------------|------------------------|
| **CPU only** (32核) | ~2-3 小时 | **200-300 小时** (8-12天) ❌ |
| **单GPU (V100)** | ~5-8 分钟 | **8-13 小时** ✅ |
| **单GPU (A100)** | ~3-5 分钟 | **5-8 小时** ⭐ |
| **单GPU (RTX 3090)** | ~6-10 分钟 | **10-16 小时** ✅ |
| **4x GPU (V100)** | ~2-3 分钟 | **3-5 小时** 🚀 |

**结论**: GPU 训练快 **50-100 倍**，CPU 训练不现实。

---

## ✅ 检查 GPU 是否可用

### 方法1: 使用 Python 检查

```bash
python << 'EOF'
import torch

print("=" * 60)
print("GPU 检查")
print("=" * 60)

# 检查 CUDA 是否可用
cuda_available = torch.cuda.is_available()
print(f"\nCUDA 可用: {cuda_available}")

if cuda_available:
    # GPU 数量
    gpu_count = torch.cuda.device_count()
    print(f"GPU 数量: {gpu_count}")

    # 每个 GPU 的信息
    for i in range(gpu_count):
        print(f"\nGPU {i}:")
        print(f"  名称: {torch.cuda.get_device_name(i)}")

        # 内存信息（GB）
        total_mem = torch.cuda.get_device_properties(i).total_memory / 1024**3
        print(f"  总内存: {total_mem:.1f} GB")

        # 当前显存使用
        allocated = torch.cuda.memory_allocated(i) / 1024**3
        reserved = torch.cuda.memory_reserved(i) / 1024**3
        print(f"  已分配: {allocated:.2f} GB")
        print(f"  已保留: {reserved:.2f} GB")

    print(f"\n✅ GPU 可用，ALIGNN 将自动使用 GPU 训练")
else:
    print("\n⚠️  警告: 没有检测到 GPU")
    print("   ALIGNN 将使用 CPU 训练（会非常慢）")
    print("\n建议:")
    print("  1. 检查 CUDA 是否正确安装")
    print("  2. 检查 PyTorch 是否为 GPU 版本")
    print("  3. 运行: nvidia-smi 查看 GPU 状态")

print("=" * 60)
EOF
```

### 方法2: 使用 nvidia-smi 检查

```bash
# 查看 GPU 状态
nvidia-smi

# 预期输出示例：
# +-----------------------------------------------------------------------------+
# | NVIDIA-SMI 470.57.02    Driver Version: 470.57.02    CUDA Version: 11.4     |
# |-------------------------------+----------------------+----------------------+
# | GPU  Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC |
# | Fan  Temp  Perf  Pwr:Usage/Cap|         Memory-Usage | GPU-Util  Compute M. |
# |===============================+======================+======================|
# |   0  Tesla V100-SXM2...  On   | 00000000:00:1E.0 Off |                    0 |
# | N/A   35C    P0    42W / 300W |      0MiB / 32510MiB |      0%      Default |
# +-------------------------------+----------------------+----------------------+
```

### 方法3: 检查 PyTorch GPU 版本

```bash
python -c "import torch; print(f'PyTorch 版本: {torch.__version__}'); print(f'CUDA 版本: {torch.version.cuda}')"

# 预期输出：
# PyTorch 版本: 2.0.1+cu118
# CUDA 版本: 11.8
```

---

## 🚀 GPU 训练配置

ALIGNN 会 **自动检测并使用 GPU**，无需额外配置。但您可以优化批次大小以充分利用 GPU。

### 根据 GPU 内存选择批次大小

```bash
# 查看 GPU 内存
nvidia-smi --query-gpu=name,memory.total --format=csv

# 推荐批次大小：
# - 6 GB (GTX 1060):  batch_size=16
# - 8 GB (RTX 2070):  batch_size=32
# - 11 GB (RTX 2080 Ti): batch_size=64
# - 16 GB (Tesla V100): batch_size=128
# - 24 GB (RTX 3090/4090): batch_size=256
# - 32 GB (Tesla V100 32GB): batch_size=256-512
# - 40 GB (A100): batch_size=512
# - 80 GB (A100 80GB): batch_size=1024
```

### 推荐配置（您的 108k 数据集）

#### 配置 1: 单个 V100 16GB

```bash
train_alignn.py \
    --root_dir ./data/cif \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results

# 预计时间: 8-13 小时
```

#### 配置 2: 单个 A100 40GB

```bash
train_alignn.py \
    --root_dir ./data/cif \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 256 \
    --epochs 100 \
    --output_dir ./results

# 预计时间: 5-8 小时
```

#### 配置 3: RTX 3090 24GB

```bash
train_alignn.py \
    --root_dir ./data/cif \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 192 \
    --epochs 100 \
    --output_dir ./results

# 预计时间: 10-16 小时
```

#### 配置 4: 较小 GPU (< 16GB)

```bash
# 使用更小的批次大小
train_alignn.py \
    --root_dir ./data/cif \
    --config config_binary_classification.json \
    --classification_threshold 0.5 \
    --batch_size 32 \
    --epochs 100 \
    --output_dir ./results

# 预计时间: 20-30 小时
```

---

## 💡 GPU 优化技巧

### 1. 监控 GPU 使用

训练时在另一个终端运行：

```bash
# 实时监控 GPU 使用
watch -n 1 nvidia-smi

# 或使用 gpustat（更友好）
pip install gpustat
watch -n 1 gpustat -cp
```

### 2. 最大化 GPU 利用率

```bash
# 逐步增加批次大小，找到最大不 OOM 的值
for bs in 64 128 192 256; do
    echo "测试批次大小: $bs"
    train_alignn.py \
        --root_dir ./data/cif \
        --config config_large_dataset.json \
        --batch_size $bs \
        --epochs 1 \
        --output_dir ./test_bs_$bs

    # 如果成功，继续测试更大的批次
    if [ $? -eq 0 ]; then
        echo "批次 $bs 成功"
    else
        echo "批次 $bs 失败（OOM）"
        break
    fi
done
```

### 3. 混合精度训练（可选，更快）

虽然 ALIGNN 默认不启用，但可以修改代码使用混合精度：

```python
# 在训练脚本中添加
from torch.cuda.amp import autocast, GradScaler

scaler = GradScaler()

# 训练循环中
with autocast():
    output = model(input)
    loss = criterion(output, target)

scaler.scale(loss).backward()
scaler.step(optimizer)
scaler.update()
```

### 4. 多 GPU 训练

如果有多个 GPU：

```bash
# 使用 4 个 GPU
torchrun --nproc_per_node=4 train_alignn.py \
    --root_dir ./data/cif \
    --config config_large_dataset.json \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results

# 注意：总批次大小 = batch_size × GPU数量
# 例如：128 × 4 = 512（有效批次大小）
```

---

## ⚠️ 常见 GPU 问题

### 问题 1: CUDA out of memory (OOM)

**错误信息**:
```
RuntimeError: CUDA out of memory. Tried to allocate 2.00 GiB
```

**解决方案**:

```bash
# 方案 1: 减小批次大小
--batch_size 32  # 从 128 减到 32

# 方案 2: 减小模型大小
# 在配置文件中:
"hidden_features": 128  # 从 256 或 512 减小

# 方案 3: 清空 GPU 缓存
python -c "import torch; torch.cuda.empty_cache()"

# 方案 4: 重启训练前先清理
nvidia-smi --gpu-reset
```

### 问题 2: GPU 未被使用

**检查**:
```bash
# 训练时查看 GPU 使用率
nvidia-smi

# 如果 GPU-Util 为 0%，说明没有使用 GPU
```

**原因和解决**:
```bash
# 1. PyTorch 不是 GPU 版本
pip uninstall torch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# 2. CUDA 版本不匹配
# 查看 CUDA 版本
nvidia-smi | grep "CUDA Version"
# 安装匹配的 PyTorch 版本

# 3. DGL 不是 GPU 版本
pip install dgl-cu118  # 根据 CUDA 版本选择
```

### 问题 3: 训练速度慢

**可能原因**:
1. 批次大小太小 → 增加批次大小
2. 数据加载慢 → 增加 `num_workers`
3. GPU 利用率低 → 检查是否有瓶颈

**优化**:
```bash
# 在配置文件中增加
"num_workers": 8      # 增加数据加载线程
"pin_memory": true    # 加速数据传输
"use_lmdb": true      # 使用缓存
```

---

## 🔍 GPU 环境检查清单

运行此脚本检查 GPU 环境：

```bash
cat > check_gpu_env.sh << 'EOF'
#!/bin/bash

echo "======================================"
echo "GPU 环境检查"
echo "======================================"

# 1. NVIDIA 驱动
echo -e "\n1. NVIDIA 驱动:"
nvidia-smi --query-gpu=driver_version --format=csv,noheader || echo "❌ nvidia-smi 不可用"

# 2. CUDA 版本
echo -e "\n2. CUDA 版本:"
nvcc --version 2>/dev/null | grep "release" || echo "⚠️  nvcc 不可用（可能正常）"
nvidia-smi | grep "CUDA Version"

# 3. PyTorch GPU 支持
echo -e "\n3. PyTorch:"
python -c "import torch; print(f'  PyTorch 版本: {torch.__version__}'); print(f'  CUDA 可用: {torch.cuda.is_available()}'); print(f'  CUDA 版本: {torch.version.cuda}'); print(f'  GPU 数量: {torch.cuda.device_count()}')"

# 4. DGL GPU 支持
echo -e "\n4. DGL:"
python -c "import dgl; print(f'  DGL 版本: {dgl.__version__}')"

# 5. GPU 信息
echo -e "\n5. GPU 硬件:"
nvidia-smi --query-gpu=name,memory.total,compute_cap --format=csv

echo -e "\n======================================"
echo "检查完成"
echo "======================================"
EOF

chmod +x check_gpu_env.sh
./check_gpu_env.sh
```

---

## 📊 预期训练时间（108,134 样本）

| GPU | 批次大小 | Epoch 时间 | 100 Epochs | 推荐 |
|-----|---------|-----------|-----------|------|
| V100 16GB | 128 | ~6 分钟 | ~10 小时 | ✅ 推荐 |
| A100 40GB | 256 | ~4 分钟 | ~7 小时 | ⭐ 最佳 |
| RTX 3090 | 192 | ~8 分钟 | ~13 小时 | ✅ 良好 |
| RTX 2080 Ti | 64 | ~12 分钟 | ~20 小时 | ✅ 可用 |
| GTX 1080 | 32 | ~20 分钟 | ~33 小时 | ⚠️ 较慢 |
| CPU (32核) | 16 | ~2 小时 | ~200 小时 | ❌ 不推荐 |

---

## 🚀 开始 GPU 训练

### 步骤 1: 检查 GPU

```bash
python << 'EOF'
import torch
if torch.cuda.is_available():
    print(f"✅ GPU 可用: {torch.cuda.get_device_name(0)}")
    print(f"   显存: {torch.cuda.get_device_properties(0).total_memory/1024**3:.1f} GB")
else:
    print("❌ GPU 不可用，将使用 CPU（会很慢）")
EOF
```

### 步骤 2: 选择合适的批次大小

```bash
# 根据上面的表格选择批次大小
# 例如 V100 16GB → batch_size=128
```

### 步骤 3: 开始训练

```bash
# 使用 GPU 训练（自动检测）
python check_cif_files_fast.py ./data/cif --remove-bad --workers 32 && \
train_alignn.py \
    --root_dir ./data/cif \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results_gpu
```

---

## 💡 最佳实践

1. **使用 GPU**: 必须！CPU 训练时间太长
2. **批次大小**: 尽可能大，但不要 OOM
3. **监控**: 使用 `nvidia-smi` 或 `gpustat` 监控
4. **后台运行**: 使用 `screen` 或 `tmux`
5. **保存检查点**: ALIGNN 自动保存 `best_model.pt`

### 后台运行训练

```bash
# 使用 screen
screen -S alignn_train
python check_cif_files_fast.py ./data/cif --remove-bad --workers 32
train_alignn.py --root_dir ./data/cif --config config_large_dataset.json \
                --batch_size 128 --epochs 100 --output_dir ./results
# 按 Ctrl+A+D 离开，训练继续
# screen -r alignn_train  # 重新连接

# 使用 nohup
nohup train_alignn.py --root_dir ./data/cif \
                      --config config_large_dataset.json \
                      --batch_size 128 --epochs 100 \
                      --output_dir ./results > train.log 2>&1 &
# tail -f train.log  # 查看日志
```

---

## ✅ 总结

- ✅ **必须使用 GPU**: CPU 太慢（200+ 小时 vs 10 小时）
- ✅ **自动检测**: ALIGNN 自动使用 GPU，无需配置
- ✅ **批次大小**: 根据 GPU 内存调整（16GB → 128）
- ✅ **监控**: 使用 `nvidia-smi` 实时监控
- ✅ **优化**: 增加批次大小和 num_workers

**立即开始 GPU 训练** 🚀
