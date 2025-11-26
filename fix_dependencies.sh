#!/bin/bash

echo "======================================"
echo "修复 ALIGNN 依赖问题"
echo "======================================"
echo ""

# 修复pydantic依赖问题
echo "1. 卸载旧版本的pydantic和pydantic-settings..."
pip uninstall -y pydantic pydantic-settings

echo ""
echo "2. 重新安装兼容版本..."
pip install "pydantic>=2.0.0" "pydantic-settings>=2.0.0"

echo ""
echo "3. 验证安装..."
python -c "from pydantic_settings import BaseSettings; print('pydantic-settings 安装成功')"
python -c "from alignn.config import TrainingConfig; print('ALIGNN config 导入成功')"

echo ""
echo "======================================"
echo "依赖修复完成！"
echo "======================================"
