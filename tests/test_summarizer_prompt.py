import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock

from src.ai.summarizer import Summarizer, load_system_prompt


class SummarizerPromptTests(unittest.TestCase):
    def test_default_prompt_is_external_markdown(self):
        prompt = load_system_prompt()
        self.assertIn("课程助教", prompt)
        self.assertIn("沿教师实际讲授的推进顺序", prompt)
        self.assertIn("补充说明", prompt)
        self.assertIn("原始材料此处不清晰", prompt)
        self.assertIn("Markdown", prompt)
        self.assertIn("使用 `**...**` 克制地标记", prompt)
        self.assertIn("不加粗整句或整段", prompt)

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

    def test_model_request_uses_material_boundary_without_length_target(self):
        client = MagicMock()
        client.chat.completions.create.return_value = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content="### 第一部分\n\n笔记")
            )],
            usage=None,
        )
        summarizer = Summarizer.__new__(Summarizer)
        summarizer.system_prompt = "system prompt"

        result = summarizer._call_llm(client, "test-model", "课程 A", "原始内容")

        self.assertEqual(result, "### 第一部分\n\n笔记")
        kwargs = client.chat.completions.create.call_args.kwargs
        user_message = kwargs["messages"][1]["content"]
        self.assertIn("<course_material>\n原始内容\n</course_material>", user_message)
        self.assertNotIn("字符数", user_message)
        self.assertEqual(kwargs["temperature"], 0.2)


if __name__ == "__main__":
    unittest.main()
