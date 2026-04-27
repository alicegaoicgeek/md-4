#!/usr/bin/env python3
"""Extract golden sentences from text using kimi-cli."""

import os
import sys
import subprocess
import re

# 读取prompt模板
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROMPT_FILE = os.path.join(SCRIPT_DIR, '..', 'scripts', 'prompt.txt')

def read_prompt():
    with open(PROMPT_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def split_text(content, max_chars=3000):
    """Simple text splitter by paragraphs."""
    paragraphs = content.split('\n\n')
    chunks = []
    current_chunk = []
    current_len = 0
    
    for para in paragraphs:
        para_len = len(para)
        if current_len + para_len > max_chars and current_chunk:
            chunks.append('\n\n'.join(current_chunk))
            current_chunk = [para]
            current_len = para_len
        else:
            current_chunk.append(para)
            current_len += para_len
    
    if current_chunk:
        chunks.append('\n\n'.join(current_chunk))
    
    return chunks

def call_kimi(text, prompt_template):
    """Call kimi-cli to analyze text."""
    full_prompt = prompt_template + text

    result = subprocess.run(
        ['kimi', '-p', full_prompt, '--print', '--final-message-only'],
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.stdout

def main():
    if len(sys.argv) < 3:
        print("Usage: extract.py <input_file> <work_dir>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    work_dir = sys.argv[2]
    
    # 读取输入文件
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 读取prompt模板
    prompt_template = read_prompt()
    
    # 切分文本
    chunks = split_text(content)
    
    # 创建工作目录
    os.makedirs(work_dir, exist_ok=True)
    
    # 处理每个chunk
    for i, chunk in enumerate(chunks, 1):
        output_file = os.path.join(work_dir, f'g{i}.txt')
        result = call_kimi(chunk, prompt_template)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Processed chunk {i}/{len(chunks)}")

if __name__ == '__main__':
    main()
