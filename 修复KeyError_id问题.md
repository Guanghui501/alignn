# 修复 KeyError: 'id' 问题

## 🔴 错误信息

```
KeyError: 'id'
File "/alignn/data.py", line 285, in <listcomp>
    ids_train_val_test["id_train"] = [dat[i][id_tag] for i in id_train]
```

## 📋 问题原因

ALIGNN 无法找到 'id' 列，原因是 **id_prop.csv 缺少正确的 header 行**。

### 错误的格式

```csv
0.cif,1
1.cif,1
2.cif,0
3.cif,1
```

❌ 问题：
1. 没有 header 行（第一行应该是 `id,target`）
2. id 包含 `.cif` 后缀（应该去掉）

### 正确的格式

```csv
id,target
0,1
1,1
2,0
3,1
```

✅ 正确：
1. 第一行是 header: `id,target`
2. id 不包含 `.cif` 后缀
3. target 是数值

---

## ✅ 快速修复（一键解决）

```bash
# 拉取最新工具
git pull origin claude/alignn-binary-classification-01Gd3smtc3KBu4WsA7u8tEUy

# 设置权限
chmod +x fix_id_prop_csv.py

# 自动修复 id_prop.csv
python fix_id_prop_csv.py ./data/cif/id_prop.csv
```

**工具会自动：**
- ✅ 备份原文件
- ✅ 添加 header 行 (`id,target`)
- ✅ 移除 `.cif` 后缀
- ✅ 验证数据格式
- ✅ 显示修复结果

---

## 📊 运行示例

```bash
$ python fix_id_prop_csv.py ./data/cif/id_prop.csv

======================================================================
id_prop.csv 格式修复工具
======================================================================

文件路径: ./data/cif/id_prop.csv

✓ 已备份原文件到: ./data/cif/id_prop.csv.backup

步骤1: 读取原始文件...
原始文件前5行:
  1. 0.cif,1
  2. 1.cif,1
  3. 2.cif,1
  4. 3.cif,1
  5. 4.cif,0

⚠️  未检测到 header 行

步骤2: 解析数据...
  解析了 83669 行数据

步骤3: 创建标准格式...
  ✓ target 列成功转换为数值类型

步骤4: 保存修复后的文件...
  ✓ 已保存到: ./data/cif/id_prop.csv

======================================================================
修复结果
======================================================================
总行数: 83669

修复后的前10行:
    id  target
     0       1
     1       1
     2       1
     3       1
     4       0
     5       1
     6       0
     7       1
     8       0
     9       1

target 列统计:
count    83669.000000
mean         0.xxx
std          0.xxx
min          0.000
25%          0.000
50%          1.000
75%          1.000
max          1.000

======================================================================
格式验证
======================================================================
  ✓ 列名正确
  ✓ 有数据
  ✓ id列无空值
  ✓ target列无空值
  ✓ target列是数值
  ✓ id列无.cif后缀

✅ 格式验证通过！

现在可以开始训练:
  train_alignn.py --root_dir ./data/cif \
                  --config config_large_dataset.json \
                  --classification_threshold 0.5 \
                  --batch_size 128 --epochs 100
```

---

## 🎯 修复后立即训练

```bash
# 一条命令完成修复和训练
python fix_id_prop_csv.py ./data/cif/id_prop.csv && \
train_alignn.py \
    --root_dir ./data/cif \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results
```

---

## 🔍 手动检查方法

### 检查当前格式

```bash
# 查看前5行
head -5 ./data/cif/id_prop.csv
```

### 检查是否有 header

```python
import pandas as pd

# 读取文件
df = pd.read_csv('./data/cif/id_prop.csv')

# 检查列名
print("列名:", df.columns.tolist())
# 应该输出: ['id', 'target']

# 如果输出的是数字或其他，说明没有 header
```

---

## 🛠️ 手动修复方法（如果需要）

如果自动工具失败，可以手动修复：

### 方法1: 使用 Python

```python
import pandas as pd

# 读取（无 header）
df = pd.read_csv('./data/cif/id_prop.csv', header=None)

# 设置列名
df.columns = ['id', 'target']

# 移除 .cif 后缀
df['id'] = df['id'].str.replace('.cif', '')

# 转换 target 为数值
df['target'] = pd.to_numeric(df['target'])

# 保存
df.to_csv('./data/cif/id_prop.csv', index=False)

print("✓ 修复完成")
print(df.head())
```

### 方法2: 使用命令行

```bash
# 备份原文件
cp ./data/cif/id_prop.csv ./data/cif/id_prop.csv.backup

# 添加 header 并移除 .cif 后缀
(echo "id,target" && sed 's/.cif,/,/' ./data/cif/id_prop.csv.backup) > ./data/cif/id_prop.csv

# 验证
head -5 ./data/cif/id_prop.csv
```

---

## 📋 完整的修复流程

```bash
# 步骤1: 修复 id_prop.csv 格式
python fix_id_prop_csv.py ./data/cif/id_prop.csv

# 步骤2: 检查 CIF 文件（如果还没做）
python check_cif_files_fast.py ./data/cif --remove-bad --workers 32

# 步骤3: 开始训练
train_alignn.py \
    --root_dir ./data/cif \
    --config config_large_dataset.json \
    --classification_threshold 0.5 \
    --batch_size 128 \
    --epochs 100 \
    --output_dir ./results
```

---

## ⚠️ 常见问题

### Q1: 为什么我的 id_prop.csv 没有 header？

A: 可能是：
- 手动创建时忘记添加
- 从其他格式转换时丢失
- 使用脚本生成时没有写入 header

### Q2: 一定要去掉 .cif 后缀吗？

A: 是的！ALIGNN 的数据加载器会自动添加 `.cif` 后缀来查找文件。如果 id 已经包含 `.cif`，会导致查找 `xxx.cif.cif` 这样的文件。

### Q3: target 列可以是其他格式吗？

A: 对于二分类：
- 可以是任意数值，ALIGNN 会根据 `classification_threshold` 转换
- 例如：`0.5` 作为阈值，`> 0.5` 为类别1，`<= 0.5` 为类别0

### Q4: 修复后还是报错？

A: 检查：
```bash
# 查看文件编码
file ./data/cif/id_prop.csv

# 查看是否有隐藏字符
cat -A ./data/cif/id_prop.csv | head -5

# 重新生成文件
python fix_id_prop_csv.py ./data/cif/id_prop.csv
```

---

## ✅ 验证修复成功

```bash
# 快速验证
python << 'EOF'
import pandas as pd

df = pd.read_csv('./data/cif/id_prop.csv')

print("列名:", df.columns.tolist())
print("行数:", len(df))
print("\n前5行:")
print(df.head())

# 检查
assert 'id' in df.columns, "缺少 id 列"
assert 'target' in df.columns, "缺少 target 列"
assert not df['id'].astype(str).str.contains('.cif').any(), "id 包含 .cif"

print("\n✅ 格式正确！")
EOF
```

---

## 🚀 立即修复

```bash
# 一键修复（推荐）
git pull origin claude/alignn-binary-classification-01Gd3smtc3KBu4WsA7u8tEUy
chmod +x fix_id_prop_csv.py
python fix_id_prop_csv.py ./data/cif/id_prop.csv
```

修复后就可以正常训练了！🎉
