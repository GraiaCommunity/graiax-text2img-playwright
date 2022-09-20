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
from typing import Awaitable, Callable, Dict, List, Literal, Optional, Union, overload

from jinja2 import Template
from markdown_it import MarkdownIt
from mdit_py_plugins.anchors.index import anchors_plugin

# from mdit_py_plugins.container.index import container_plugin
from mdit_py_plugins.footnote.index import footnote_plugin
from mdit_py_plugins.front_matter.index import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin
from playwright.async_api import Page

from .api import html2img
from .plugins.code import code_plugin
from .plugins.code.highlight import highlight_code
from .types import PageParms, ScreenshotParms
from .utils import text2html

index_css = Path(Path(__file__).parent / "css" / "index.css").read_text()

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


@overload
async def template2img(
    template: str,
    render_parms: Dict[str, str],
    *,
    return_html: Literal[False] = False,
    page_parms: Optional[PageParms] = None,
    screenshot_parms: Optional[ScreenshotParms] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> bytes:
    ...


@overload
async def template2img(
    template: str,
    render_parms: Dict[str, str],
    *,
    return_html: Literal[True] = True,
) -> str:
    ...


async def template2img(
    template: str,
    render_parms: Dict[str, str],
    *,
    return_html: bool = False,
    page_parms: Optional[PageParms] = None,
    screenshot_parms: Optional[ScreenshotParms] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> Union[str, bytes]:
    """Jinja2 模板转图片

    Args:
        template (str): Jinja2 模板
        render_parms (Dict[str, str]): Jinja2.Template.render 的参数
        return_html (bool): 返回生成的 HTML 代码而不是图片生成结果的 bytes
        page_parms (PageParms, optional): Playwright 浏览器 new_page 方法的参数
        screenshot_parms (ScreenshotParms, optional): Playwright 浏览器页面截图方法的参数
        extra_page_methods (Optional[List[Callable[[Page], Awaitable]]]):
            默认为 None，用于 https://playwright.dev/python/docs/api/class-page 中提到的部分方法，
            如 `page.route(...)` 等
    """
    html_code: str = Template(template).render(**render_parms)
    return (
        html_code
        if return_html
        else await html2img(
            html_code,
            page_parms=page_parms,
            screenshot_parms=screenshot_parms,
            extra_page_methods=extra_page_methods,
        )
    )


@overload
async def text2img(
    text: str,
    *,
    disable_default_css: bool = False,
    extra_css: str = "",
    return_html: Literal[False] = False,
    page_parms: Optional[PageParms] = None,
    screenshot_parms: Optional[ScreenshotParms] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> bytes:
    ...


@overload
async def text2img(
    text: str,
    *,
    disable_default_css: bool = False,
    extra_css: str = "",
    return_html: Literal[True] = True,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> str:
    ...


async def text2img(
    text: str,
    *,
    disable_default_css: bool = False,
    extra_css: str = "",
    return_html: bool = False,
    page_parms: Optional[PageParms] = None,
    screenshot_parms: Optional[ScreenshotParms] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> Union[str, bytes]:
    """纯文本转图片

    若使用 HTML 代码请在一行写完，换行会直接分段

    Args:
        text (str): 要转换为图片的文本
        disable_default_css (bool): 是否禁止使用内置 CSS
        extra_css (str): 除了内置 CSS 外需要在生成的页面中使用的 CSS
        return_html (bool): 返回生成的 HTML 代码而不是图片生成结果的 bytes
        page_parms (PageParms, optional): Playwright 浏览器 new_page 方法的参数
        screenshot_parms (ScreenshotParms, optional): Playwright 浏览器页面截图方法的参数
        extra_page_methods (Optional[List[Callable[[Page], Awaitable]]]):
            默认为 None，用于 https://playwright.dev/python/docs/api/class-page 中提到的部分方法，
            如 `page.route(...)` 等
    """
    html_code = (
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<style>{extra_css}{index_css if disable_default_css else ""}</style>'
        f'<div class="container">{text2html(text)}</div>'
    )
    return (
        html_code
        if return_html
        else await html2img(
            html_code,
            page_parms=page_parms,
            screenshot_parms=screenshot_parms,
            extra_page_methods=extra_page_methods,
        )
    )


@overload
async def md2img(
    content: str,
    *,
    md: MarkdownIt = markdown_it,
    disable_default_css: bool = False,
    extra_css: str = "",
    return_html: Literal[False] = False,
    disable_onedark_css: bool = False,
    page_parms: Optional[PageParms] = None,
    screenshot_parms: Optional[ScreenshotParms] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> bytes:
    ...


@overload
async def md2img(
    content: str,
    *,
    md: MarkdownIt = markdown_it,
    disable_default_css: bool = False,
    extra_css: str = "",
    return_html: Literal[True] = True,
    disable_onedark_css: bool = False,
) -> str:
    ...


async def md2img(
    content: str,
    *,
    md: MarkdownIt = markdown_it,
    disable_default_css: bool = False,
    extra_css: str = "",
    return_html: bool = False,
    disable_onedark_css: bool = False,
    page_parms: Optional[PageParms] = None,
    screenshot_parms: Optional[ScreenshotParms] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
):
    """Markdown 文本转图片

    Args:
        content (str): 要转换为图片的 Markdown 文本
        disable_default_css (bool): 是否禁止使用内置 CSS
        extra_css (str): 除了内置 CSS 外需要在生成的页面中使用的 CSS
        return_html (bool): 返回生成的 HTML 代码而不是图片生成结果的 bytes
        disable_onedark_css (bool): 是否禁用内置的用于代码块高亮的 OneDark 主题，
            可通过 extra_css 参数传入其他适用于 pygments 生成结果的 CSS
        page_parms (PageParms, optional): Playwright 浏览器 new_page 方法的参数
        screenshot_parms (ScreenshotParms, optional): Playwright 浏览器页面截图方法的参数
        extra_page_methods (Optional[List[Callable[[Page], Awaitable]]]):
            默认为 None，用于 https://playwright.dev/python/docs/api/class-page 中提到的部分方法，
            如 `page.route(...)` 等
    """
    if disable_default_css:
        github_css = ""
        onedark_css = ""
    else:
        github_css = Path(Path(__file__).parent / "css" / "github.css").read_text()
        onedark_css = "" if disable_onedark_css else Path(Path(__file__).parent / "css" / "one-dark.css").read_text()

    html_code = (
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<style>{onedark_css}{github_css}{extra_css}{"" if disable_default_css else index_css}</style>'
        f'<div class="markdown-body">{md.render(content)}</div>'
    )

    return (
        html_code
        if return_html
        else await html2img(
            html_code,
            page_parms=page_parms,
            screenshot_parms=screenshot_parms,
            extra_page_methods=extra_page_methods,
        )
    )
