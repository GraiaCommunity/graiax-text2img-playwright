from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter
from pygments.styles import get_style_by_name

one_dark = get_style_by_name('one-dark')
formater = HtmlFormatter(style=one_dark)


def highlight_code(code: str, lang: str) -> str:
    try:
        lexer = lexers.get_lexer_by_name(lang)
    except ValueError:
        return code

    # remove the previous'<div class="highlight"><pre>'
    # and the last '</pre></div>'
    return highlight(code, lexer, formater).strip()[28:-12].rstrip()
