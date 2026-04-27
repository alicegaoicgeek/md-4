#!/bin/bash
# 一键提取4件套：痛点 / 金句 / 方法卡片 / 思维导图
# 用法: bash extract_all.sh [单个文件路径]
# 不传参数则处理仓库根目录下所有 .md 文件

set -e

REPO_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_DIR="$REPO_DIR/skills"
OUTPUT_DIR="$REPO_DIR/output"

# 确定目标文件列表
if [ -n "$1" ]; then
    FILES=("$1")
else
    FILES=()
    for f in "$REPO_DIR"/*.md; do
        [ -f "$f" ] && FILES+=("$f")
    done
fi

if [ ${#FILES[@]} -eq 0 ]; then
    echo "错误: 没有找到 .md 文件"
    exit 1
fi

# 检查 kimi CLI
if ! command -v kimi &>/dev/null; then
    echo "错误: kimi CLI 未安装。运行: pip install kimi-cli"
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "=========================================="
echo "四件套提取"
echo "文件数: ${#FILES[@]}"
echo "输出目录: $OUTPUT_DIR"
echo "=========================================="

for FILE in "${FILES[@]}"; do
    BASENAME=$(basename "$FILE" .md)
    echo ""
    echo ">>> 处理: $BASENAME"
    echo "-------------------------------------------"

    FILE_OUT="$OUTPUT_DIR/$BASENAME"
    mkdir -p "$FILE_OUT"

    # 1. 痛点
    echo "[1/4] 痛点提取..."
    WORKDIR=$(bash "$SKILLS_DIR/r2-painpoint/extract.sh" "$FILE")
    cat "$WORKDIR"/g*.txt > "$FILE_OUT/painpoints.txt"
    echo "  → $FILE_OUT/painpoints.txt"

    # 2. 金句
    echo "[2/4] 金句提取..."
    WORKDIR=$(bash "$SKILLS_DIR/r2-golden-sentence/extract.sh" "$FILE")
    cat "$WORKDIR"/g*.txt > "$FILE_OUT/golden_sentences.txt"
    echo "  → $FILE_OUT/golden_sentences.txt"

    # 3. 方法卡片
    echo "[3/4] 方法卡片提取..."
    WORKDIR=$(bash "$SKILLS_DIR/r2-methodx/extract.sh" "$FILE")
    cat "$WORKDIR"/g*.txt > "$FILE_OUT/methods.txt"
    echo "  → $FILE_OUT/methods.txt"

    # 4. 思维导图
    echo "[4/4] 思维导图提取..."
    WORKDIR=$(bash "$SKILLS_DIR/r2-mindmap/extract.sh" "$FILE")
    cat "$WORKDIR"/g*.txt > "$FILE_OUT/mindmap.txt"
    echo "  → $FILE_OUT/mindmap.txt"

    echo "<<< $BASENAME 完成"
done

echo ""
echo "=========================================="
echo "全部完成。结果在: $OUTPUT_DIR/"
ls -R "$OUTPUT_DIR/"
echo "=========================================="
