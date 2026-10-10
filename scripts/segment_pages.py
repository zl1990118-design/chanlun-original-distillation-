"""Turn page JSONL into conservative segment candidates.

Usage: python scripts/segment_pages.py data/pdf_pages.jsonl data/segment_candidates.jsonl
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.segment_original import coalesce_page_segments, merge_page_continuations, split_page_text, write_jsonl


def main():
    if len(sys.argv) != 3:
        raise SystemExit("用法: python scripts/segment_pages.py 输入页文本.jsonl 输出分段.jsonl")

    segments = []
    previous_page = 0
    with open(sys.argv[1], encoding="utf-8") as source:
        for line in source:
            if not line.strip():
                continue
            page_data = json.loads(line)
            page_number = int(page_data["page"])
            current = coalesce_page_segments(split_page_text(page_data.get("text", ""), page_number), page_number)
            if previous_page and page_number != previous_page + 1:
                # Do not stitch across missing/nonadjacent pages.
                current = current
            else:
                current = merge_page_continuations(current, segments, page_number)
            segments.extend(current)
            previous_page = page_number

    write_jsonl(segments, sys.argv[2])
    print(f"生成 {len(segments)} 个分段候选。注意：自动分类未经人工核验。")
    print("新增来源信息：source_pages；跨页合并会写入 evidence，仍需人工抽查。")


if __name__ == "__main__":
    main()
