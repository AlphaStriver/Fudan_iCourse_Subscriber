import unittest

from src.api.email_markdown import (
    build_attachment_filename,
    build_course_markdown,
)


class EmailMarkdownTests(unittest.TestCase):
    def test_builds_markdown_for_one_course(self):
        lectures = [
            {
                "sub_title": "2026-09-14第1-2节",
                "date": "2026-09-14",
                "summary": "## 要点\n\n内容",
            },
            {
                "sub_title": "2026-09-16第1-2节",
                "date": "2026-09-16",
                "summary": "第二次内容",
                "is_update": True,
            },
        ]
        rendered = build_course_markdown("课程 A", lectures)
        self.assertTrue(rendered.startswith("# 课程 A\n"))
        self.assertIn("2026-09-14第1-2节", rendered)
        self.assertIn("PPT 识别更新", rendered)
        self.assertIn("第二次内容", rendered)

    def test_filename_is_safe_and_date_qualified(self):
        lectures = [
            {"date": "2026-09-14"},
            {"date": "2026-09-16"},
        ]
        filename = build_attachment_filename("课程/A", lectures)
        self.assertEqual(
            filename,
            "课程_A_2026-09-14_to_2026-09-16.md",
        )


if __name__ == "__main__":
    unittest.main()
