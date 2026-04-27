#!/bin/bash
# 金句提取脚本
# 用法: bash extract.sh <file_path>

set -e

# 参数检查
if [ -z "$1" ]; then
    echo "用法: bash extract.sh <file_path>"
    exit 1
fi

FILE="$1"
if [ ! -f "$FILE" ]; then
    echo "错误: 文件不存在: $FILE"
    exit 1
fi

# 定位脚本目录（所有依赖从这里取）
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROMPT_FILE="$SCRIPT_DIR/prompt.txt"
MDSPLIT="$SCRIPT_DIR/mdsplit.py"

if [ ! -f "$PROMPT_FILE" ]; then
    echo "错误: prompt.txt 不存在: $PROMPT_FILE" >&2
    exit 1
fi

if [ ! -f "$MDSPLIT" ]; then
    echo "错误: mdsplit.py 不存在: $MDSPLIT" >&2
    exit 1
fi

# 自动检测并安装 pip 依赖
if ! python3 -c "import langchain_text_splitters" &>/dev/null; then
    echo "安装依赖: langchain-text-splitters ..." >&2
    pip3 install langchain-text-splitters -q >&2
fi

# 创建临时工作目录（兼容 macOS 和 Linux）
if command -v md5 &>/dev/null; then
    HASH=$(echo "$FILE" | md5 | cut -c1-8)
elif command -v md5sum &>/dev/null; then
    HASH=$(echo "$FILE" | md5sum | cut -c1-8)
else
    HASH=$(date +%s | cut -c-8)
fi
WORKDIR="/tmp/r2gs_$HASH"
rm -rf "$WORKDIR"
mkdir -p "$WORKDIR"

# Step 1: 使用 mdsplit 按标题边界智能切分（每块约 4000 字符）
echo "文件: $FILE" >&2
python3 "$MDSPLIT" "$FILE" -o "$WORKDIR/chunks" --max-size 4000 --naming chunk >&2

# 重命名为 c1.txt, c2.txt 格式
i=1
for chunk in "$WORKDIR/chunks"/*.md; do
    [ -f "$chunk" ] && mv "$chunk" "$WORKDIR/c$i.txt"
    i=$((i + 1))
done
rmdir "$WORKDIR/chunks" 2>/dev/null || true

CHUNKS=$((i - 1))
echo "切分为 $CHUNKS 块" >&2

# Step 2: 串行提取
echo "调用 kimi 提取金句..." >&2
for i in $(seq 1 $CHUNKS); do
    echo "  处理 chunk $i/$CHUNKS..." >&2
    cat "$PROMPT_FILE" "$WORKDIR/c$i.txt" | kimi --quiet --print > "$WORKDIR/g$i.txt" 2>&1
done
echo "提取完成" >&2

# Step 3: 输出工作目录路径（由 Claude Code 处理结果）
echo "$WORKDIR"
