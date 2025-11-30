"""
Contextual Answer Generator using simple summarization
"""
from typing import List

def summarize_texts(texts: List[str]) -> str:
    # Simple summarization: concatenate and truncate
    summary = ' '.join(texts)
    return summary[:500] + ('...' if len(summary) > 500 else '')

# Example usage:
# summary = summarize_texts(["Text from book 1", "Text from book 2"])
