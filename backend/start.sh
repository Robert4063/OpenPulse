#!/bin/bash

echo "========================================"
echo "启动 OpenPulse 后端服务"
echo "========================================"
echo ""

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未找到Python，请先安装Python 3.8+"
    exit 1
fi

echo "[信息] 正在启动后端服务..."
echo "[信息] 服务地址: http://localhost:8000"
echo "[信息] API文档: http://localhost:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python3 main.py
