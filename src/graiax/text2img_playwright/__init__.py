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
from .types import ScreenshotParms
from .utils import text2html, update_screenshot_args

markdown_it = (
    MarkdownIt("gfm-like", {"highlight": highlight_code})
    .use(anchors_plugin)
    # .use(container_plugin, name="tip")  # TODO
    .use(footnote_plugin)
    .use(tasklists_plugin)
    .use(front_matter_plugin)
    .use(code_plugin)
    .enable("table")
)

index_css = Path(Path(__file__).parent / "css" / "index.css").read_text()


async def template2img(
    template: str,
    render_args: Dict[str, str],
    *,
    context_args: Optional[ContextParm] = None,
    screenshot_args: Optional[ScreenshotParms] = None,
) -> bytes:
    """Jinja2 模板转图片

    Args:
        template (str): Jinja2 模板
        render_args (Dict[str, str]): Jinja2.Template.render 的参数
        context_args (ContextParm, optional): Playwright 浏览器 new_context 方法的参数
        screenshot_args (ScreenshotParms, optional): Playwright 浏览器页面截图方法的参数
    """
    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    text = Template(template).render(**render_args)

    if context_args is None:
        context_args = {}
    if screenshot_args is None:
        screenshot_args = {}

    screenshot_args = update_screenshot_args(screenshot_args)

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
    disable_default_css: bool = False,
    extra_css: str = "",
    *,
    context_args: Optional[ContextParm] = None,
    screenshot_args: Optional[ScreenshotParms] = None,
) -> bytes:
    """纯文本转图片

    若使用 HTML 代码请在一行写完，换行会直接分段

    Args:
        text (str): 要转换为图片的文本
        disable_default_css (bool): 是否禁止使用内置 CSS
        extra_css (str): 除了内置 CSS 外需要在生成的页面中使用的 CSS
        context_args (ContextParm, optional): Playwright 浏览器 new_context 方法的参数
        screenshot_args (ScreenshotParms, optional): Playwright 浏览器页面截图方法的参数
    """
    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    text = text2html(text)
    text = (
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<style>{extra_css}{index_css if disable_default_css else ""}</style><div class="container">{text}</div>'
    )

    if context_args is None:
        context_args = {}
    if screenshot_args is None:
        screenshot_args = {}

    screenshot_args = update_screenshot_args(screenshot_args)

    async with browser.page(context=True, **context_args) as page:
        await page.set_content(text)
        return await page.screenshot(**screenshot_args)


async def md2img(
    md_text: str,
    disable_default_css: bool = False,
    extra_css: str = "",
    *,
    disable_onedark_css: bool = False,
    context_args: Optional[ContextParm] = None,
    screenshot_args: Optional[ScreenshotParms] = None,
) -> bytes:
    """Markdown 文本转图片

    Args:
        md_text (str): 要转换为图片的 Markdown 文本
        disable_default_css (bool): 是否禁止使用内置 CSS
        extra_css (str): 除了内置 CSS 外需要在生成的页面中使用的 CSS
        disable_onedark_css (bool): 是否禁用内置的用于代码块高亮的 OneDark 主题，
            可通过 extra_css 参数传入其他适用于 pygments 生成结果的 CSS
        context_args (ContextParm, optional): Playwright 浏览器 new_context 方法的参数
        screenshot_args (ScreenshotParms, optional): Playwright 浏览器页面截图方法的参数
    """
    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    if disable_default_css:
        github_css = ""
        onedark_css = ""
    else:
        github_css = Path(Path(__file__).parent / "css" / "github.css").read_text()
        onedark_css = "" if disable_onedark_css else Path(Path(__file__).parent / "css" / "one-dark.css").read_text()

    md_text = markdown_it.render(md_text)
    md_text = (
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<style>{onedark_css}{github_css}{extra_css}{"" if disable_default_css else index_css}</style>'
        f'<div class="markdown-body">{md_text}</div>'
    )

    if context_args is None:
        context_args = {}
    if screenshot_args is None:
        screenshot_args = {}

    screenshot_args = update_screenshot_args(screenshot_args)

    async with browser.page(context=True, **context_args) as page:
        await page.set_content(md_text)
        return await page.screenshot(**screenshot_args)
