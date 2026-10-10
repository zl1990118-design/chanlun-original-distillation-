"""Conservative segmentation helpers for extracted PDF text.

This module deliberately marks uncertain material rather than claiming verified authorship.
Input is plain text with page markers such as: <PAGE: 11>
"""
from __future__ import annotations
import re
from dataclasses import dataclass, asdict
from typing import Iterable
import json

COURSE_TITLE = re.compile(r"教你炒股票\s*\d+\s*[：:]", re.I)
TIMESTAMP = re.compile(r"(?<!\d)20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}")
COMPILER_CUES = (
    "整理说明", "整理者", "本册内容沿用", "市场学生", "文集按内容分为",
    "为了表达对患病缠师的敬意", "掌握缠师理论的二种方法",
)
READER_CUES = ("回复：", "引用：", "发表于", "楼主", "网友提问")
MASTER_CUES = ("本 ID", "本ID", "缠中说禅")

@dataclass
class Segment:
    segment_id: str
    page: int | None
    ordinal: int
    title: str | None
    timestamp: str | None
    speaker_type: str
    confidence: float
    status: str
    evidence: list[str]
    text: str

def classify_block(text: str, page: int | None = None, title: str | None = None,
                   timestamp: str | None = None, ordinal: int = 1) -> tuple[str, float, list[str]]:
    t = text.strip()
    evidence = []
    if not t:
        return "OTHER_MATERIAL", 0.99, ["empty_block"]
    if any(cue in t for cue in COMPILER_CUES):
        evidence.append("compiler_cue")
        return "EDITOR_OR_COMPILER", 0.90, evidence
    if any(cue in t for cue in READER_CUES):
        evidence.append("reader_or_forum_layout_cue")
        return "SPEAKER_UNVERIFIED", 0.45, evidence
    if title and COURSE_TITLE.search(title):
        if timestamp and any(cue in t for cue in MASTER_CUES):
            return "MASTER_MAIN_TEXT", 0.65, ["course_title", "timestamp", "first_person_cue"]
        return "SPEAKER_UNVERIFIED", 0.40, ["course_title_only_not_sufficient"]
    if any(cue in t for cue in MASTER_CUES) and timestamp:
        return "SPEAKER_UNVERIFIED", 0.40, ["first_person_cue_and_timestamp_not_proof"]
    return "SPEAKER_UNVERIFIED", 0.20, ["insufficient_authorship_evidence"]

def split_page_text(page_text: str, page: int) -> list[Segment]:
    """Split a page conservatively around course headings or timestamped post headings."""
    lines = page_text.splitlines()
    starts = [0]
    for i, line in enumerate(lines):
        if i and (COURSE_TITLE.search(line) or TIMESTAMP.search(line)):
            starts.append(i)
    starts = sorted(set(starts))
    out = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end]).strip()
        if not block:
            continue
        title = next((x.strip() for x in lines[start:min(end, start+5)]
                      if COURSE_TITLE.search(x)), None)
        ts = next((TIMESTAMP.search(x).group(0) for x in lines[start:min(end, start+8)]
                   if TIMESTAMP.search(x)), None)
        speaker, confidence, evidence = classify_block(block, page, title, ts, n+1)
        out.append(Segment(
            segment_id=f"pdf-p{page:03d}-s{n+1:03d}",
            page=page, ordinal=n+1, title=title, timestamp=ts,
            speaker_type=speaker, confidence=confidence,
            status="SPEAKER_UNVERIFIED" if speaker == "SPEAKER_UNVERIFIED" else "RAW_NOT_PROCESSED",
            evidence=evidence, text=block
        ))
    return out

def write_jsonl(segments: Iterable[Segment], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for segment in segments:
            f.write(json.dumps(asdict(segment), ensure_ascii=False) + "\n")
