import re
from typing import Optional, Type, overload

from pygments import highlight as pgm_highlight
from pygments import lexers
from pygments.formatter import Formatter
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name


class Highlight:
    def __init__(self, *, theme: str = "one-dark", formatter: Optional[Type[Formatter]] = None, **formatter_params):
        if formatter is None:
            self.formatter = HtmlFormatter(style=get_style_by_name(theme), **formatter_params)
        else:
            self.formatter = formatter(**formatter_params)

    @overload
    def render(self, code: str, lang: str) -> str:
        ...

    @overload
    def render(self, code: str, lang: str) -> str:
        ...

    def render(self, code: str, lang: str):
        try:
            lexer = lexers.get_lexer_by_name(lang)
        except ValueError:
            return code

        result = pgm_highlight(code, lexer, self.formatter).strip()
        # remove the previous '<div class="highlight"><pre>' and the last '</pre></div>'
        re_result = re.search(r'^<div class="highlight"><pre>([.\s\S]*)</pre></div>$', result)
        return re_result.groups()[0].strip() if re_result is not None else result
