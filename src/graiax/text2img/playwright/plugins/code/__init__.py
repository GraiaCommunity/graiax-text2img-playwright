"""
移植自：https://github.com/vuepress/vuepress-next/blob/main/packages/markdown/src/plugins/codePlugin/codePlugin.ts

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
from typing import List, MutableMapping

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml, unescapeAll
from markdown_it.renderer import RendererHTML
from markdown_it.token import Token
from markdown_it.utils import OptionsDict

from .highlight_lines import is_highlight_line, resolve_highlight_lines
from .language_resolver import resolve_language


def fence(md: RendererHTML, tokens: List[Token], idx: int, options: OptionsDict, env: MutableMapping):
    token: Token = tokens[idx]

    info = token.info if unescapeAll(token.info).strip() else ""
    language = resolve_language(info)
    language_class = f'{options["langPrefix"]}{language["name"].lower()}'
    code: str = (
        options["highlight"](code=token.content, lang=language["name"])
        if options["highlight"]
        else escapeHtml(token.content)
    )
    result = code if code.startswith("<pre") else f'<pre class="{language_class}"><code>{code}</code></pre>'
    lines = code.split("\n")[:-1]
    highlight_lines_ranges = resolve_highlight_lines(info)

    if highlight_lines_ranges is not None:
        highlight_lines_code = "".join(
            '<div class="highlight-line">&nbsp;</div>'
            if is_highlight_line(idx + 1, highlight_lines_ranges)
            else "<br/>"
            for idx, _ in enumerate(lines)
        )

        result = f'{result}<div class="highlight-lines">{highlight_lines_code}</div>'

    if use_line_numbers := not bool(re.search(":no-line-numbers\b", info)):
        line_numbers_code = "".join(['<div class="line-number"></div>'] * (len(lines) + 1))
        result = f'{result}<div class="line-numbers" aria-hidden="true">{line_numbers_code}</div>'

    result = (
        f'<div class="{language_class} ext-{language["ext"]}'
        f'{" line-numbers-mode" if use_line_numbers else ""}">{result}</div>'
    )

    return result


def code_plugin(md: MarkdownIt):
    md.add_render_rule("fence", fence)
