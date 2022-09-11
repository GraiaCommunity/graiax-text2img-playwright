"""
https://mdit-py-plugins.readthedocs.io/en/latest/
mdit-py-plugins 的 自带可用插件列表：
  - mdit_py_plugins.amsmath: （数学公式？）markdown-it-amsmath
  - mdit_py_plugins.anchors: 标题锚点 markdown-it-anchors
  - mdit_py_plugins.container: markdown-it-container
  - mdit_py_plugins.deflist: markdown-it-deflist
  - mdit_py_plugins.dollarmath: （数学公式？）markdown-it-dollarmath
  - mdit_py_plugins.footnote: 脚注 markdown-it-footnote
  - mdit_py_plugins.front_matter: markdown-it-front-matter
  - mdit_py_plugins.myst_blocks: ???
  - mdit_py_plugins.myst_role: ???
  - mdit_py_plugins.tasklists: 任务清单 markdown-it-task-lists
  - mdit_py_plugins.texmath: （数学公式？）markdown-it-texmath
  - mdit_py_plugins.wordcount: ???
"""


from pathlib import Path
from typing import Dict, Optional

from graiax.playwright import PlaywrightBrowser
from graiax.playwright.pager import Parameters as ContextParm
from jinja2 import Template
from launart import Launart
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors.index import anchors_plugin
from mdit_py_plugins.container.index import container_plugin
from mdit_py_plugins.footnote.index import footnote_plugin
from mdit_py_plugins.front_matter.index import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from .plugins.code import code_plugin
from .plugins.code.highlight import highlight_code
from .types import ScreenshotParm

md = (
    MarkdownIt("gfm-like", {'highlight': highlight_code})
    .use(anchors_plugin)
    .use(container_plugin, name='tip')
    .use(footnote_plugin)
    .use(tasklists_plugin)
    .use(front_matter_plugin)
    .use(code_plugin)
    .enable('table')
)

index_css = Path(Path(__file__).parent / "css" / "index.css").read_text()


def _update_screenshot_args(screenshot_args: ScreenshotParm) -> ScreenshotParm:
    if 'full_page' not in screenshot_args:
        screenshot_args['full_page'] = True
    if 'type' not in screenshot_args:
        screenshot_args['type'] = 'jpeg'
    return screenshot_args


async def template2img(
    template: str,
    template_args: Dict[str, str],
    *,
    context_args: Optional[ContextParm] = None,
    screenshot_args: Optional[ScreenshotParm] = None,
) -> bytes:
    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    text = Template(template).render(**template_args)

    if context_args is None:
        context_args = {}
    if screenshot_args is None:
        screenshot_args = {}

    screenshot_args = _update_screenshot_args(screenshot_args)

    _context = await browser.new_context(**context_args)
    _page = await _context.new_page()

    try:
        await _page.set_content(text)
        return await _page.screenshot(**screenshot_args)
    finally:
        await _page.close()
        await _context.close()


async def text2img(
    text: str,
    css: str = '',
    *,
    context_args: Optional[ContextParm] = None,
    screenshot_args: Optional[ScreenshotParm] = None,
) -> bytes:
    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    text = text.replace("\r", "").replace("\n", "<br/>\n")
    text = (
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<style>{css}{index_css}</style><div class="container">{text}</div>'
    )

    if context_args is None:
        context_args = {}
    if screenshot_args is None:
        screenshot_args = {}

    screenshot_args = _update_screenshot_args(screenshot_args)

    async with browser.page(context=True, **context_args) as page:
        await page.set_content(text)
        return await page.screenshot(**screenshot_args)


async def md2img(
    md_text: str,
    extra_css: str = "",
    *,
    hightlight: bool = False,
    github_style: bool = True,
    context_args: Optional[ContextParm] = None,
    screenshot_args: Optional[ScreenshotParm] = None,
) -> bytes:
    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    onedark_css = Path(Path(__file__).parent / "css" / "one-dark.css").read_text() if hightlight else ''
    github_css = Path(Path(__file__).parent / "css" / "github.css").read_text() if github_style else ''

    md_text = md.render(md_text)
    md_text = (
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<style>{onedark_css}{github_css}{extra_css}{index_css}</style><div class="markdown-body">{md_text}</div>'
    )

    if context_args is None:
        context_args = {}
    if screenshot_args is None:
        screenshot_args = {}

    screenshot_args = _update_screenshot_args(screenshot_args)

    async with browser.page(context=True, **context_args) as page:
        await page.set_content(md_text)
        return await page.screenshot(**screenshot_args)
