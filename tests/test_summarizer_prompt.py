import tempfile
import unittest
from pathlib import Path

from src.ai.summarizer import load_system_prompt


class SummarizerPromptTests(unittest.TestCase):
    def test_default_prompt_is_external_markdown(self):
        prompt = load_system_prompt()
        self.assertIn("课程助教", prompt)
        self.assertIn("不确定性边界", prompt)
        self.assertIn("Markdown", prompt)

    def test_custom_prompt_file_is_loaded(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prompt.md"
            path.write_text("custom prompt", encoding="utf-8")
            self.assertEqual(load_system_prompt(path), "custom prompt")

    def test_empty_prompt_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "prompt.md"
            path.write_text("\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                load_system_prompt(path)


if __name__ == "__main__":
    unittest.main()
