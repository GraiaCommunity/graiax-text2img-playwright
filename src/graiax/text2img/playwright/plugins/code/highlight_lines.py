"""
移植自 https://github.com/vuepress/vuepress-next/blob/main/packages/markdown/src/plugins/codePlugin/resolveHighlightLines.ts

The MIT License (MIT)

Copyright (c) 2018-present, Yuxi (Evan) You

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
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
