"""
移植自 https://github.com/vuepress/vuepress-next/blob/main/packages/markdown/src/plugins/codePlugin/resolveHighlightLines.ts
"""

import re
from typing import List, Optional

HighlightLinesRange = List[List[int]]


def resolve_highlight_lines(info: str) -> Optional[HighlightLinesRange]:
    if re.match(r"{([\d,-]+)}", info) is None or not info.strip():
        return
    return list(map(lambda i: list(map(lambda j: int(j), i.split("-"))), info[1:-1].split(",")))


# Check if a line number is in ranges
def is_highlight_line(line_number: int, ranges: HighlightLinesRange) -> bool:
    return any(line_number >= range[0] and line_number <= range[1] for range in ranges)
