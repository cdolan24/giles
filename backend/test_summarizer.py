import unittest
from summarizer import summarize_texts

class TestSummarizer(unittest.TestCase):
    def test_summarize_texts(self):
        texts = ["This is a long text. " * 30, "Another text."]
        summary = summarize_texts(texts)
        self.assertTrue(isinstance(summary, str))
        self.assertTrue(len(summary) <= 503)  # 500 + '...'
        self.assertIn("This is a long text.", summary)

if __name__ == "__main__":
    unittest.main()
