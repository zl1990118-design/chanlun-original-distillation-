import unittest
from src.segment_original import classify_block, split_page_text

class SegmentationTests(unittest.TestCase):
    def test_compiler_text_is_not_master_rule(self):
        label, confidence, evidence = classify_block("文集按内容分为五册，这是整理说明。")
        self.assertEqual(label, "EDITOR_OR_COMPILER")

    def test_course_title_alone_is_not_verified_authorship(self):
        label, confidence, evidence = classify_block("某段文字", title="教你炒股票 12：标题")
        self.assertEqual(label, "SPEAKER_UNVERIFIED")

    def test_first_person_phrase_is_not_proof(self):
        label, confidence, evidence = classify_block("本 ID 在市场里", timestamp="2006-06-07 18:08:15")
        self.assertEqual(label, "SPEAKER_UNVERIFIED")

    def test_split_keeps_page_number(self):
        segments = split_page_text("普通文字\n教你炒股票 1：标题\n2006-06-07 18:08:15\n正文\n2006-06-07 19:00:00\n另一个帖子", 11)
        self.assertTrue(segments)
        self.assertTrue(all(s.page == 11 for s in segments))

if __name__ == "__main__":
    unittest.main()
