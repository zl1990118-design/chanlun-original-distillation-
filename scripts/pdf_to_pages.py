#!/usr/bin/env python3
"""Extract a PDF into one JSONL record per page using pypdf."""
import json
import sys
from pathlib import Path
from pypdf import PdfReader

def main():
    if len(sys.argv) != 3:
        print("用法: python scripts/pdf_to_pages.py 输入.pdf 输出.jsonl")
        return 2
    pdf_path = Path(sys.argv[1])
    output_path = Path(sys.argv[2])
    if not pdf_path.is_file():
        print(f"错误：找不到 PDF 文件：{pdf_path}")
        return 2
    try:
        reader = PdfReader(str(pdf_path))
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open("w", encoding="utf-8") as out:
            for page_num, page in enumerate(reader.pages, start=1):
                try:
                    page_text = page.extract_text() or ""
                except Exception as exc:
                    page_text = ""
                    print(f"警告：第 {page_num} 页提取失败：{exc}", file=sys.stderr)
                out.write(json.dumps({"source_file": pdf_path.name,"page": page_num,"text": page_text}, ensure_ascii=False) + "\n")
        print(f"后可受：혾周交了件是出用法？type error")
        return 0
    except Exception as exc:
        print(f"无法不页以：有限？{exc}", file=sys.stderr)
        return 1
if __name__ == "__main__":
    raise SystemExit(main())
