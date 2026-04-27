#!/usr/bin/env python3
"""mdsplit - Split Markdown files using LangChain text splitters.

Uses MarkdownHeaderTextSplitter for heading-based splitting with metadata,
and RecursiveCharacterTextSplitter for size-based splitting with chunk_overlap.
"""

import argparse
import os
import re
import sys

from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


def sanitize_filename(title, max_len=60):
    """Convert heading text to a safe filename component."""
    s = re.sub(r'[<>:"/\\|?*\x00-\x1f]', '', title)
    s = re.sub(r'\s+', '_', s.strip())
    s = re.sub(r'[_]+', '_', s)
    return s[:max_len] if s else 'untitled'


def build_headers_to_split_on(level):
    """Build headers_to_split_on list up to the given level."""
    return [("#" * i, f"Header {i}") for i in range(1, level + 1)]


def get_chunk_title(doc):
    """Extract the best title from a Document's metadata."""
    # Try from deepest heading level upward
    for i in range(6, 0, -1):
        key = f"Header {i}"
        if key in doc.metadata:
            return doc.metadata[key]
    return None


def split_markdown(content, level=2, max_size=0, chunk_overlap=200):
    """Split markdown content using LangChain splitters.

    Args:
        content: Raw markdown text
        level: Heading level to split at (1-6)
        max_size: Max chars per chunk. 0 = heading-only split
        chunk_overlap: Overlap between chunks when using size-based splitting

    Returns:
        List of (title, text, metadata) tuples
    """
    headers = build_headers_to_split_on(level)

    # Step 1: Split by headings (preserves structure + metadata)
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers,
        strip_headers=False,
    )
    docs = header_splitter.split_text(content)

    # Step 2: If max_size specified, further split large chunks
    if max_size > 0:
        size_splitter = RecursiveCharacterTextSplitter(
            chunk_size=max_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""],
        )
        docs = size_splitter.split_documents(docs)

    # Convert to output tuples
    results = []
    for doc in docs:
        title = get_chunk_title(doc)
        results.append((title, doc.page_content, doc.metadata))

    return results


def write_chunks(chunks, output_dir, base_name, naming):
    """Write chunks to files. Returns list of output paths."""
    os.makedirs(output_dir, exist_ok=True)
    paths = []

    for i, (title, text, metadata) in enumerate(chunks, 1):
        if naming == 'title':
            safe_title = sanitize_filename(title) if title else f'part_{i:02d}'
            filename = f'{i:02d}_{safe_title}.md'
        else:
            filename = f'{base_name}_chunk_{i:02d}.md'

        path = os.path.join(output_dir, filename)
        with open(path, 'w', encoding='utf-8') as f:
            # Write metadata as YAML frontmatter
            if metadata:
                f.write('---\n')
                for k, v in metadata.items():
                    f.write(f'{k}: {v}\n')
                f.write('---\n\n')
            f.write(text)
        paths.append(path)

    return paths


def main():
    p = argparse.ArgumentParser(
        description='Split Markdown files using LangChain text splitters.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''examples:
  %(prog)s doc.md -o out/ --level 2              # split at H1+H2 headings
  %(prog)s doc.md -o out/ --max-size 4000        # heading split + size limit
  %(prog)s doc.md -o out/ --max-size 4000 --chunk-overlap 500
  %(prog)s doc.md -o out/ --naming chunk         # use chunk naming
''')
    p.add_argument('input', help='Input Markdown file')
    p.add_argument('-o', '--output', default=None, help='Output directory (default: <input>_split/)')
    p.add_argument('--level', type=int, default=2, help='Heading level to split at (default: 2)')
    p.add_argument('--max-size', type=int, default=0, help='Max chars per chunk (0=heading split only)')
    p.add_argument('--chunk-overlap', type=int, default=200, help='Overlap between size-split chunks (default: 200)')
    p.add_argument('--naming', choices=['title', 'chunk'], default='title',
                   help='Naming: "title" = 01_HeadingText.md, "chunk" = file_chunk_01.md')

    args = p.parse_args()

    if not os.path.isfile(args.input):
        print(f'Error: {args.input} not found', file=sys.stderr)
        sys.exit(1)

    with open(args.input, 'r', encoding='utf-8') as f:
        content = f.read()

    base_name = os.path.splitext(os.path.basename(args.input))[0]
    output_dir = args.output or f'{args.input}_split'

    chunks = split_markdown(content, args.level, args.max_size, args.chunk_overlap)

    if not chunks:
        print('No chunks produced.', file=sys.stderr)
        sys.exit(1)

    paths = write_chunks(chunks, output_dir, base_name, args.naming)
    print(f'Split into {len(paths)} files in {output_dir}/')
    for path in paths:
        size = os.path.getsize(path)
        print(f'  {os.path.basename(path)} ({size} bytes)')


if __name__ == '__main__':
    main()
