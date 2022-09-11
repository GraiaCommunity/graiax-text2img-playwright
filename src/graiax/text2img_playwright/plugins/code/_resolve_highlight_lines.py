import re
from typing import List, Optional, Tuple

HighlightLinesRange = Tuple[int, int]


def resolve_highlight_lines(info: str) -> Optional[List[HighlightLinesRange]]:
    # no highlight-lines mark, return `None`
    if re.match(r'{([\d,-]+)}', info) is None:
        return
    return [(int(i),) * 2 if len(d := i.split("-")) == 1 else tuple(map(int, d)) for i in info[1:-1].split(",")]


# def resolve_highlight_lines(info: str) -> Optional[List[HighlightLinesRange]]:
#     # no highlight-lines mark, return `None`
#     if (match := re.match(r'{([\d,-]+)}', info)) is None:
#         return

#     # resolve lines ranges from the highlight-lines mark
#     def fn(item: str) -> Tuple[int, int]:
#         ranges = item.split('-')
#         if len(ranges) == 1:
#             ranges += ranges[0]
#         return tuple(map(int, ranges))

#     return list(map(fn, match.groups()[0].split(',')))


# def resolve_highlight_lines(info: str) -> Optional[List[HighlightLinesRange]]:
#     if (result := re.match(r'{([\d,-]+)}', info)) is None:
#         return

#     def fn(item: str) -> Tuple[int, int]:
#         if not (match := re.match(r'(?P<start>\d+)(-)?(?P<stop>\d+)?', item)):
#             raise
#         res = match.groupdict()
#         return (int(start := res['start']), int(res.get('stop') or start))

#     return list(map(fn, result.groups()[0].split(',')))


# Check if a line number is in ranges
def is_highlight_line(line_number: int, ranges: List[HighlightLinesRange]) -> bool:
    return any(line_number >= range[0] and line_number <= range[1] for range in ranges)
