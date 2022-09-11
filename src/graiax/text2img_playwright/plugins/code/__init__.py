import re

from markdown_it import MarkdownIt
from markdown_it.common.utils import escapeHtml, unescapeAll
from markdown_it.token import Token

from ._resolve_highlight_lines import is_highlight_line, resolve_highlight_lines
from ._resolve_language import resolve_language


def fence(self, tokens, idx, options, env):
    token: Token = tokens[idx]

    info = token.info if unescapeAll(token.info).strip() else ''
    language = resolve_language(info)
    language_class = f'{options["langPrefix"]}{language["name"].lower()}'
    code: str = (
        options['highlight'](token.content, language["name"]) if options['highlight'] else escapeHtml(token.content)
    )
    result = code if code.startswith('<pre') else f'<pre class="{language_class}"><code>{code}</code></pre>'
    lines = code.split('\n')[:-1]
    highlight_lines_ranges = resolve_highlight_lines(info)

    if highlight_lines_ranges is not None:
        highlight_lines_code = ''.join(
            '<div class="highlight-line">&nbsp;</div>'
            if is_highlight_line(idx + 1, highlight_lines_ranges)
            else '<br/>'
            for idx, _ in enumerate(lines)
        )

        result = f'{result}<div class="highlight-lines">{highlight_lines_code}</div>'

    if use_line_bumbers := not bool(re.search(':no-line-numbers\b', info)):
        line_numbers_code = ''.join(['<div class="line-number"></div>'] * (len(lines) + 1))
        result = f'{result}<div class="line-numbers" aria-hidden="true">{line_numbers_code}</div>'

    result = f'<div class="{language_class} ext-{language["ext"]}{" line-numbers-mode" if use_line_bumbers else ""}">{result}</div>'

    return result


def code_plugin(md: MarkdownIt):
    md.add_render_rule('fence', fence)
