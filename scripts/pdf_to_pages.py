"""Extract page-preserving text from a PDF into JSONL.

Requires: pip install pymupdf
Usage: python scripts/pdf_to_pages.py input.pdf data/pdf_pages.jsonl
"""
from __future__ import annotations
import json, sys
from pathlib import Path

def main():
    if len(sys.argv) != 3:
        raise SystemExit("用法: python scripts/pdf_to_pages.py 输入.pdf 输出.jsonl")
    try:
        import fitz
    except ImportError:
        raise SystemExit("缺少 PyMuPDF。先执行: pip install pymupdf")
    src, dst = Path(sys.argv[1]), Path(sys.argv[2])
    dst.parent.mkdir(parents=True, exist_ok=True)
    with fitz.open(src) as pdf, dst.open("w", encoding="utf-8") as out:
        total = len(pdf)
        for i, page in enumerate(pdf, start=1):
            record = {"source_file": src.name, "page": i, "text": page.get_text("text")}
            out.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"完成：{total} 页 -> {dst}")

if __name__ == "__main__":
    main()
