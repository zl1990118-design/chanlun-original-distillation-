"""Focused regression checks for the segmentation patch (standalone)."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from src.segment_original import coalesce_page_segments, merge_page_continuations, split_page_text


class SegmentationPatchTests(unittest.TestCase):
    def test_title_fragments_attach_to_first_timestamped_post(self):
        page = "\n".join([
            "缠中说禅技术论坛 www.chzhshch.net",
            "教你炒股票 1：不会赢钱的经济人，只是废人",
            "教你炒股票 1：不会赢钱的经济人，只是废人",
            "2006-06-07 18:08:15",
            "正文开始，本 ID 认为市场需要实践。",
        ])
        parts = coalesce_page_segments(split_page_text(page, 11), 11)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0].timestamp, "2006-06-07 18:08:15")
        self.assertIn("正文开始", parts[0].text)
        self.assertIn("教你炒股票 1", parts[0].text)
        self.assertNotEqual(parts[0].segment_id, "pdf-p011-s002")

    def test_contents_page_collapses_to_non_article_material(self):
        page = "\n".join([f"教你炒股票 {i}：课程标题" for i in range(1, 9)])
        parts = coalesce_page_segments(split_page_text(page, 8), 8)
        self.assertEqual(len(parts), 1)
        self.assertEqual(parts[0].speaker_type, "OTHER_MATERIAL")
        self.assertIn("multi_course_contents_page", parts[0].evidence)

    def test_same_course_truncated_page_tail_can_join_next_page(self):
        previous_page = split_page_text(
            "教你炒股票 4：什么是理性？\n2006-06-19 16:45:17\n前一页文章内容未完结市场就是一 blog.sina.com.cn/chzhshch",
            14,
        )
        previous_page = coalesce_page_segments(previous_page, 14)
        accumulated = previous_page[:]
        next_page = split_page_text(
            "教你炒股票 4：什么是理性？\n" + ("这是上一页文章的延续内容。" * 20) + "\n2006-06-20 11:51:24\n新文章正文。",
            15,
        )
        next_page = coalesce_page_segments(next_page, 15)
        result = merge_page_continuations(next_page, accumulated, 15)
        self.assertEqual(result[0].timestamp, "2006-06-20 11:51:24")
        self.assertIn(15, accumulated[-1].source_pages)
        self.assertIn("continued_onto_page_15", accumulated[-1].evidence)

    def test_distinct_course_context_does_not_join(self):
        previous = split_page_text("教你炒股票 1：标题\n2006-06-07 18:08:15\n正文没有结束", 11)
        previous = coalesce_page_segments(previous, 11)
        current = split_page_text("教你炒股票 2：标题\n" + ("另一课内容。" * 30) + "\n2006-06-07 22:41:27\n新正文", 12)
        current = coalesce_page_segments(current, 12)
        result = merge_page_continuations(current, previous[:], 12)
        self.assertEqual(len(result), len(current))
        self.assertNotIn(12, previous[-1].source_pages)


if __name__ == "__main__":
    unittest.main(verbosity=2)
