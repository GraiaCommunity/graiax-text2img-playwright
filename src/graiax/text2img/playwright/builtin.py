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
from playwright.async_api import Page

from .api import html2img
from .types import PageParams, ScreenshotParams
from .utils import text2html

reset_css = Path(Path(__file__).parent / "css" / "reset.css").read_text()


@overload
async def template2img(
    template: str,
    render_params: Dict[str, str],
    *,
    return_html: Literal[False] = False,
    page_params: Optional[PageParams] = None,
    screenshot_params: Optional[ScreenshotParams] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> bytes:
    ...


@overload
async def template2img(
    template: str,
    render_params: Dict[str, str],
    *,
    return_html: Literal[True] = True,
) -> str:
    ...


async def template2img(
    template: str,
    render_params: Dict[str, str],
    *,
    return_html: bool = False,
    page_params: Optional[PageParams] = None,
    screenshot_params: Optional[ScreenshotParams] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> Union[str, bytes]:
    """Jinja2 模板转图片

    Args:
        template (str): Jinja2 模板
        render_params (Dict[str, str]): Jinja2.Template.render 的参数
        return_html (bool): 返回生成的 HTML 代码而不是图片生成结果的 bytes
        page_params (PageParams, optional): Playwright 浏览器 new_page 方法的参数
        screenshot_params (ScreenshotParams, optional): Playwright 浏览器页面截图方法的参数
        extra_page_methods (Optional[List[Callable[[Page], Awaitable]]]):
            默认为 None，用于 https://playwright.dev/python/docs/api/class-page 中提到的部分方法，
            如 `page.route(...)` 等
    """
    html_code: str = Template(template).render(**render_params)
    return (
        html_code
        if return_html
        else await html2img(
            html_code,
            page_params=page_params,
            screenshot_params=screenshot_params,
            extra_page_methods=extra_page_methods,
        )
    )


@overload
async def text2img(
    text: str,
    *,
    disable_reset_css: bool = False,
    extra_css: str = "",
    return_html: Literal[False] = False,
    page_params: Optional[PageParams] = None,
    screenshot_params: Optional[ScreenshotParams] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> bytes:
    ...


@overload
async def text2img(
    text: str,
    *,
    disable_reset_css: bool = False,
    extra_css: str = "",
    return_html: Literal[True] = True,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> str:
    ...


async def text2img(
    text: str,
    *,
    disable_reset_css: bool = False,
    extra_css: str = "",
    return_html: bool = False,
    page_params: Optional[PageParams] = None,
    screenshot_params: Optional[ScreenshotParams] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> Union[str, bytes]:
    """纯文本转图片

    若使用 HTML 代码请在一行写完，换行会直接分段

    Args:
        text (str): 要转换为图片的文本
        disable_reset_css (bool): 是否禁用 Reset CSS
        extra_css (str): 除了内置 CSS 外需要使用的 CSS
        return_html (bool): 返回生成的 HTML 代码而不是图片生成结果的 bytes
        page_params (PageParams, optional): Playwright 浏览器 new_page 方法的参数
        screenshot_params (ScreenshotParams, optional): Playwright 浏览器页面截图方法的参数
        extra_page_methods (Optional[List[Callable[[Page], Awaitable]]]):
            默认为 None，用于 https://playwright.dev/python/docs/api/class-page 中提到的部分方法，
            如 `page.route(...)` 等
    """
    html_code = (
        '<meta name="viewport" content="width=device-width,initial-scale=1.0">'
        f'<style>{extra_css}{"" if disable_reset_css else reset_css}</style>'
        f'<div class="container">{text2html(text)}</div>'
    )
    return (
        html_code
        if return_html
        else await html2img(
            html_code,
            page_params=page_params,
            screenshot_params=screenshot_params,
            extra_page_methods=extra_page_methods,
        )
    )


class MarkdownToImg:
    def __init__(self, md: Optional[MarkdownIt] = None, css: str = ""):
        """Markdown 转图片

        Args:
            md (Optional[MarkdownIt]): MarkdownIt 实例，若不指定 MarkdownIt 实例，则有额外的无法禁用的内置 CSS
            css (str): 额外的全局 CSS
        """

        if md:
            self.md = md
            self.builtin_css = css
        else:
            from mdit_py_emoji import emoji_plugin
            from mdit_py_plugins.anchors.index import anchors_plugin
            from mdit_py_plugins.container.index import container_plugin
            from mdit_py_plugins.footnote.index import footnote_plugin
            from mdit_py_plugins.front_matter.index import front_matter_plugin
            from mdit_py_plugins.tasklists import tasklists_plugin

            from .plugins.code import code_plugin
            from .plugins.code.highlight_code import Highlight
            from .plugins.custom_container import CreateContainer

            tip_container = CreateContainer("tip", "提示")
            warnning_container = CreateContainer("warnning", "注意")
            danger_container = CreateContainer("danger", "警告")

            onedark_css = Path(Path(__file__).parent / "css" / "one-dark.css").read_text()
            container_css = Path(Path(__file__).parent / "css" / "container.css").read_text()
            github_css = Path(Path(__file__).parent / "css" / "github.css").read_text()

            self.builtin_css = css + github_css + onedark_css + container_css

            self.md = (
                MarkdownIt("gfm-like", {"highlight": Highlight().render})
                .use(anchors_plugin)
                .use(container_plugin, name="tip", validate=tip_container.validate, render=tip_container.create)
                .use(
                    container_plugin,
                    name="warnning",
                    validate=warnning_container.validate,
                    render=warnning_container.create,
                )
                .use(
                    container_plugin, name="danger", validate=danger_container.validate, render=danger_container.create
                )
                .use(footnote_plugin)
                .use(tasklists_plugin)
                .use(front_matter_plugin)
                .use(code_plugin)
                .use(emoji_plugin)
                .enable("table")
            )

    @overload
    async def render(
        self,
        content: str,
        *,
        disable_reset_css: bool = False,
        extra_css: str = "",
        return_html: Literal[False] = False,
        page_params: Optional[PageParams] = None,
        screenshot_params: Optional[ScreenshotParams] = None,
        extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
    ) -> bytes:
        ...

    @overload
    async def render(
        self,
        content: str,
        *,
        disable_reset_css: bool = False,
        extra_css: str = "",
        return_html: Literal[True] = True,
    ) -> str:
        ...

    async def render(
        self,
        content: str,
        *,
        disable_reset_css: bool = False,
        extra_css: str = "",
        return_html: bool = False,
        page_params: Optional[PageParams] = None,
        screenshot_params: Optional[ScreenshotParams] = None,
        extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
    ):
        """渲染 Markdown

        Args:
            content (str): 要转换为图片的 Markdown 文本
            disable_reset_css (bool): 是否禁用 Reset CSS
            extra_css (str): 除了内置 CSS 外需要使用的 CSS
            return_html (bool): 返回生成的 HTML 代码而不是图片生成结果的 bytes
            page_params (PageParams, optional): Playwright 浏览器 new_page 方法的参数
            screenshot_params (ScreenshotParams, optional): Playwright 浏览器页面截图方法的参数
            extra_page_methods (Optional[List[Callable[[Page], Awaitable]]]):
                默认为 None，用于 https://playwright.dev/python/docs/api/class-page 中提到的部分方法，
                如 `page.route(...)` 等
        """

        html_code = (
            '<meta name="viewport" content="width=device-width,initial-scale=1.0"/>'
            f'<style>{self.builtin_css}{extra_css}{"" if disable_reset_css else reset_css}</style>'
            f'<div class="markdown-body">{self.md.render(content)}</div>'
        )

        return (
            html_code
            if return_html
            else await html2img(
                html_code,
                page_params=page_params,
                screenshot_params=screenshot_params,
                extra_page_methods=extra_page_methods,
            )
        )
