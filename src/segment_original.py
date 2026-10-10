"""Conservative segmentation of extracted Chanlun PDF text.

The splitter treats timestamps as the primary post-boundary signal. Course
headings are metadata, not independent segment boundaries. Ambiguous authorship
remains unverified.
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, asdict, field
from typing import Iterable

COURSE_TITLE = re.compile(r"教你炒股票\s*\d+\s*[：:]", re.I)
COURSE_NUMBER = re.compile(r"教你炒股票\s*(\d+)", re.I)
TIMESTAMP = re.compile(r"(?<!\d)20\d{2}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}")
COMPILER_CUES = (
    "整理说明", "整理者", "本册内容沿用", "市场 学生", "文集按内容分为",
    "为了表达对患病缠师的敬意", "掌握缠师理论的 二种方法",
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
    # Provenance for safely tracked cross-page continuations.
    source_pages: list[int] = field(default_factory=list)
    # Course number is context only; it is not proof of speaker identity.
    course_context: str | None = None


def classify_block(
    text: str,
    page: int | None = None,
    title: str | None = None,
    timestamp: str | None = None,
    ordinal: int = 1,
) -> tuple[str, float, list[str]]:
    t = text.strip()
    evidence: list[str] = []
    if not t:
        return "OTHER_MATERIAL", 0.99, ["empty_block"]
    if any(cue in t for cue in COMPILER_CUES):
        return "EDITOR_OR_COMPILER", 0.90, ["compiler_cue"]
    if any(cue in t for cue in READER_CUES):
        return "SPEAKER_UNVERIFIED", 0.45, ["reader_or_forum_layout_cue"]
    if title and COURSE_TITLE.search(title):
        if timestamp and any(cue in t for cue in MASTER_CUES):
            return "MASTER_MAIN_TEXT", 0.65, ["course_title", "timestamp", "first_person_cue"]
        return "SPEAKER_UNVERIFIED", 0.40, ["course_title_only_not_sufficient"]
    if any(cue in t for cue in MASTER_CUES) and timestamp:
        return "SPEAKER_UNVERIFIED", 0.40, ["first_person_cue_and_timestamp_not_proof"]
    return "SPEAKER_UNVERIFIED", 0.20, ["insufficient_authorship_evidence"]


def _page_course_metadata(lines: list[str]) -> tuple[str | None, str | None, int]:
    """Return a clean course heading, course number context, and distinct count.

    A page containing a table of contents for many lessons should not be
    assigned one lesson title merely because it contains many course headings.
    """
    found: list[tuple[str, str]] = []
    seen: set[str] = set()
    for line in lines:
        match = COURSE_NUMBER.search(line)
        if not match:
            continue
        number = match.group(1)
        if number not in seen:
            seen.add(number)
            heading = COURSE_TITLE.search(line)
            if heading:
                clean = line[heading.start():].strip()
                clean = re.split(r"\.{2,}|…{2,}", clean, maxsplit=1)[0].strip()
                found.append((number, clean))
    if len(seen) == 1 and found:
        return found[0][1] or None, found[0][0], 1
    return None, None, len(seen)


def _has_short_heading_preamble(text: str, course_context: str | None) -> bool:
    if not course_context or not COURSE_TITLE.search(text) or TIMESTAMP.search(text):
        return False
    # A short header/preamble can be carried into the first timestamped post.
    # Substantial text may be a continuation from the previous PDF page.
    return len(text.strip()) <= 160


def split_page_text(page_text: str, page: int) -> list[Segment]:
    """Return conservative page-local candidates.

    This keeps the established title/timestamp splitter API for compatibility.
    The output pipeline then coalesces heading-only fragments before writing the
    final candidate file. Course headings are metadata, not verified authorship.
    """
    lines = page_text.splitlines()
    if not lines:
        lines = [page_text]
    page_title, course_context, unique_courses = _page_course_metadata(lines[:80])

    starts = [0]
    for i, line in enumerate(lines):
        if i and (COURSE_TITLE.search(line) or TIMESTAMP.search(line)):
            starts.append(i)
    starts = sorted(set(starts))

    out: list[Segment] = []
    for n, start in enumerate(starts):
        end = starts[n + 1] if n + 1 < len(starts) else len(lines)
        block = "\n".join(lines[start:end]).strip()
        if not block:
            continue
        title = next(
            (x.strip() for x in lines[start:min(end, start + 5)] if COURSE_TITLE.search(x)),
            None,
        )
        if title:
            match = COURSE_TITLE.search(title)
            title = title[match.start():].strip() if match else title
            title = re.split(r"\.{2,}|…{2,}", title, maxsplit=1)[0].strip()
        timestamp_match = next(
            (TIMESTAMP.search(x) for x in lines[start:min(end, start + 8)] if TIMESTAMP.search(x)),
            None,
        )
        ts = timestamp_match.group(0) if timestamp_match else None
        speaker, confidence, evidence = classify_block(block, page, title, ts, n + 1)
        if course_context:
            evidence = list(evidence) + [f"course_context_{course_context}"]
        out.append(Segment(
            segment_id=f"pdf-p{page:03d}-s{n + 1:03d}",
            page=page,
            ordinal=n + 1,
            title=title,
            timestamp=ts,
            speaker_type=speaker,
            confidence=confidence,
            status="SPEAKER_UNVERIFIED" if speaker == "SPEAKER_UNVERIFIED" else "RAW_NOT_PROCESSED",
            evidence=evidence,
            text=block,
            source_pages=[page],
            course_context=course_context,
        ))
    return out


def coalesce_page_segments(page_segments: list[Segment], page: int) -> list[Segment]:
    """Join title-only fragments to the next dated block and collapse TOC pages.

    The original low-level splitter remains unchanged for compatibility, but the
    production JSONL pipeline uses this cleanup so headings are not emitted as
    separate apparent articles.
    """
    if not page_segments:
        return page_segments

    all_text = "\n".join(seg.text for seg in page_segments)
    course_numbers = {m.group(1) for m in COURSE_NUMBER.finditer(all_text)}
    has_timestamps = any(seg.timestamp for seg in page_segments)

    # A page listing several different lessons is a contents/material page, not
    # dozens of independent article candidates.
    if not has_timestamps and len(course_numbers) >= 4:
        first = page_segments[0]
        combined_text = "\n\n".join(seg.text for seg in page_segments)
        first.text = combined_text
        first.title = None
        first.timestamp = None
        first.speaker_type = "OTHER_MATERIAL"
        first.confidence = 0.95
        first.status = "RAW_NOT_PROCESSED"
        first.evidence = list(dict.fromkeys(first.evidence + ["multi_course_contents_page", "not_an_article_boundary"]))
        first.course_context = None
        first.source_pages = [page]
        first.ordinal = 1
        first.segment_id = f"pdf-p{page:03d}-s001"
        return [first]

    result: list[Segment] = []
    pending: list[Segment] = []
    for seg in page_segments:
        is_short_heading = (
            seg.timestamp is None
            and (seg.title is not None or seg.course_context is not None)
            and len(seg.text.strip()) <= 160
            and not any(cue in seg.text for cue in COMPILER_CUES)
        )
        if is_short_heading:
            pending.append(seg)
            continue

        if seg.timestamp and pending:
            lead_text = "\n".join(item.text for item in pending)
            seg.text = lead_text + "\n\n" + seg.text
            if not seg.title:
                seg.title = next((item.title for item in pending if item.title), None)
            seg.source_pages = sorted(set((seg.source_pages or [page]) + [page]))
            seg.evidence = list(dict.fromkeys(seg.evidence + ["heading_fragments_attached_to_timestamped_block"]))
            speaker, confidence, evidence = classify_block(seg.text, seg.page, seg.title, seg.timestamp, seg.ordinal)
            # Preserve course-context evidence in addition to classifier evidence.
            if seg.course_context:
                evidence.append(f"course_context_{seg.course_context}")
            seg.speaker_type, seg.confidence = speaker, confidence
            seg.status = "SPEAKER_UNVERIFIED" if speaker == "SPEAKER_UNVERIFIED" else "RAW_NOT_PROCESSED"
            seg.evidence = list(dict.fromkeys(evidence))
            pending = []
        elif pending:
            # Attach short page-header fragments to a following substantial
            # untimestamped lead-in as well; the caller may identify it as a
            # continuation from the preceding page.
            lead_text = "\n".join(item.text for item in pending)
            seg.text = lead_text + "\n\n" + seg.text
            if not seg.title:
                seg.title = next((item.title for item in pending if item.title), None)
            seg.evidence = list(dict.fromkeys(seg.evidence + ["heading_fragments_attached_to_untimestamped_leadin"]))
            pending = []
        result.append(seg)

    if pending:
        # Substantial text under a repeated lesson heading may be a continuation
        # from the previous page. Keep it intact for the cross-page check.
        result.extend(pending)

    # Normalize ordinal/IDs after coalescing; preserve page provenance.
    for i, seg in enumerate(result, 1):
        seg.ordinal = i
        seg.segment_id = f"pdf-p{page:03d}-s{i:03d}"
    return result

def _is_probably_truncated(text: str) -> bool:
    """Conservative heuristic used only to decide whether to join page tails."""
    t = text.strip()
    # Page footer material can follow a sentence fragment in extracted PDFs.
    t = re.split(r"blog\.sina\.com\.cn|缠中说禅博客", t, maxsplit=1)[0].rstrip()
    if not t:
        return False
    return t[-1] not in "。！？；.!?;：:」』）)]}"


def merge_page_continuations(page_segments: list[Segment], accumulated: list[Segment], page: int) -> list[Segment]:
    """Merge only strong same-course page continuations; otherwise retain evidence.

    A long, undated lead-in is joined to the prior page's final dated segment
    only when course context matches, page provenance is adjacent, and the prior
    text appears cut off. Ambiguous cases remain independent candidates.
    """
    if not page_segments:
        return page_segments
    lead = page_segments[0]
    has_prior_timestamp = bool(accumulated and accumulated[-1].timestamp)
    prior = accumulated[-1] if accumulated else None
    prior_page_end = max(prior.source_pages or ([prior.page] if prior and prior.page else [0])) if prior else 0
    merge_candidate = (
        prior is not None
        and lead.timestamp is None
        and len(lead.text.strip()) > 160
        and lead.course_context is not None
        and lead.course_context == prior.course_context
        and has_prior_timestamp
        and prior_page_end == page - 1
        and _is_probably_truncated(prior.text)
    )
    if merge_candidate:
        prior.text = prior.text.rstrip() + "\n\n" + lead.text.lstrip()
        prior.evidence = list(dict.fromkeys(prior.evidence + [f"continued_onto_page_{page}", "page_boundary_continuation_merged_by_same_course_and_truncation_cue"]))
        prior.source_pages = sorted(set((prior.source_pages or [prior.page]) + [page]))
        page_segments = page_segments[1:]
    elif lead.timestamp is None and len(lead.text.strip()) > 160 and lead.course_context:
        lead.evidence = list(dict.fromkeys(lead.evidence + ["possible_page_continuation_needs_review"]))
    return page_segments


def write_jsonl(segments: Iterable[Segment], path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        for segment in segments:
            f.write(json.dumps(asdict(segment), ensure_ascii=False) + "\n")
