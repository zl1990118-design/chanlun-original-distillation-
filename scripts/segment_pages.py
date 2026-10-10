"""Turn page JSONL into conservative segment candidates.
Usage: python scripts/segment_pages.py data/pdf_pages.jsonl data/segment_candidates.jsonl
"""
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.segment_original import split_page_text, write_jsonl

def main():
    if len(sys.argv) != 3:
        raise SystemExit("用法: python scripts/segment_pages.py 输入页文本.jsonl 输出分段.jsonl")
    segments = []
    with open(sys.argv[1], encoding="utf-8") as f:
        for line in f:
            page = json.loads(line)
            segments.extend(split_page_text(page.get("text", ""), int(page["page"])))
    write_jsonl(segments, sys.argv[2])
    print(f"生成 {len(segments)} 个分段候选。注意：自动分类未经人工核验。")

if __name__ == "__main__":
    main()
