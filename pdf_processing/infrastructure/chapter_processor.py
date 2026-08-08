import re
from typing import Tuple, Optional

class ChapterProcessor:
    def __init__(self):
        self.chapter_pattern = r'^\s*(\d+)\s*$'

    def detect_chapter(self, text: str) -> Tuple[Optional[int], Optional[str]]:
        """Detect if text is a standalone number"""
        text = text.strip()
        match = re.match(self.chapter_pattern, text)
        if match:
            try:
                chapter_num = int(match.group(1))
                return chapter_num, ""
            except ValueError:
                pass
        return None, None
