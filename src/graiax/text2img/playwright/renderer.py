from __future__ import annotations

import importlib.resources
from collections.abc import Awaitable, Callable, Sequence
from enum import Enum
from pathlib import Path
from typing import Literal, overload

from graiax.playwright import PlaywrightService
from graiax.playwright.utils import Parameters as PageOption
from launart import Launart
from playwright.async_api import Browser, BrowserContext, Page
from playwright.async_api._generated import Locator
from typing_extensions import TypedDict

from .utils import run_always_await


class FloatRect(TypedDict):
    x: float
    y: float
    width: float
    height: float


class ScreenshotOption(TypedDict, total=False):
    """Playwright 截图参数

    详见：https://playwright.dev/python/docs/api/class-page#page-screenshot

    Args:
        timeout (float, optional): 截图超时时间.
        type (Literal["jpeg", "png"], optional): 截图图片类型.
        path (Union[str, Path]], optional): 截图保存路径，如不需要则留空.
        quality (int, optional): 截图质量，仅适用于 JPEG 格式图片.
        omit_background (bool, optional): 是否允许隐藏默认的白色背景，这样就可以截透明图了，仅适用于 PNG 格式.
        full_page (bool, optional): 是否截整个页面而不是仅设置的视口大小，默认为 True.
        clip (FloatRect, optional): 截图后裁切的区域，xy为起点.
        animations: (Literal["allow", "disabled"], optional): 是否允许播放 CSS 动画.
        caret: (Literal["hide", "initial"], optional): 当设置为 `hide` 时，截图时将隐藏文本插入符号，默认为 `hide`.
        scale: (Literal["css", "device"], optional): 页面缩放设置.
            当设置为 `css` 时，则将设备分辨率与 CSS 中的像素一一对应，在高分屏上会使得截图变小.
            当设置为 `device` 时，则根据设备的屏幕缩放设置或当前 Playwright 的 Page/Context 中的
            device_scale_factor 参数来缩放.
        mask (List["Locator"]], optional): 指定截图时的遮罩的 Locator。元素将被一颜色为 #FF00FF 的框覆盖.
    """

    timeout: float | None
    type: Literal["jpeg", "png", None]
    path: str | Path | None
    quality: int | None
    omit_background: bool | None
    full_page: bool | None
    clip: FloatRect | None
    animations: Literal["allow", "disabled", None]
    caret: Literal["hide", "initial", None]
    scale: Literal["css", "device", None]
    mask: list[Locator] | None


_CSS_MOD = "graiax.text2img.playwright.css"


class BuiltinCSS(Enum):
    """内置 CSS"""

    value: str

    reset = importlib.resources.read_text(_CSS_MOD, "reset.css")
    github = importlib.resources.read_text(_CSS_MOD, "github.css")
    one_dark = importlib.resources.read_text(_CSS_MOD, "one-dark.css")
    container = importlib.resources.read_text(_CSS_MOD, "container.css")


class HTMLRenderer:
    """HTML 渲染器

    用于将 HTML 代码转换为图片

    Args:
        page_option (PageOption, optional): 截图时使用的页面设置.
            参数介绍详见：https://playwright.dev/python/docs/api/class-browser#browser-new-page
        screenshot_option (ScreenshotOption, optional): 截图设置.
        css (Sequence[Union[BuiltinCSS, str]], optional): 要加载的 CSS.
            默认包含 Reset CSS、GitHub Markdown 样式、One Dark 代码高亮主题、VitePress 样式的 container CSS.
            如有不需要或想覆盖这些默认 CSS，则传入一个包含 CSS 字符串的列表.
        page_modifiers (List[Callable[[Page], Union[Awaitable[None], None]]], optional): 接受 Page 实例的方法/函数.
            用于对 Page 本身进行额外的修改，如: 使用 page.route 重定向资源文件到本地文件.
    """

    page_option: PageOption
    screenshot_option: ScreenshotOption
    style: str
    page_modifiers: list[Callable[[Page], Awaitable[None] | None]]

    def __init__(
        self,
        page_option: PageOption | None = None,
        screenshot_option: ScreenshotOption | None = None,
        *,
        css: Sequence[BuiltinCSS | str] = (
            BuiltinCSS.reset,
            BuiltinCSS.github,
            BuiltinCSS.one_dark,
            BuiltinCSS.container,
        ),
        page_modifiers: list[Callable[[Page], Awaitable[None] | None]] | None = None,
    ):
        if isinstance(css, str):
            css = [css]
        page_option = page_option or {}
        screenshot_option = screenshot_option or {}
        screenshot_option = {"full_page": True, "type": "jpeg", **screenshot_option}

        self.page_option: PageOption = page_option
        self.screenshot_option: ScreenshotOption = screenshot_option
        self.style: str = "\n".join(i.value if isinstance(i, BuiltinCSS) else i for i in css)
        self.page_modifiers = page_modifiers or []

    @overload
    async def render(
        self,
        content: str,
        *,
        extra_screenshot_option: ScreenshotOption | None = None,
        extra_page_option: PageOption | None = None,
        extra_page_modifiers: list[Callable[[Page], Awaitable[None] | None]] | None = None,
        new_context: bool = False,
        use_global_context: bool = True,
    ) -> bytes:
        ...

    @overload
    async def render(
        self,
        content: str,
        *,
        browser: Browser,
        extra_screenshot_option: ScreenshotOption | None = None,
        extra_page_option: PageOption | None = None,
        extra_page_modifiers: list[Callable[[Page], Awaitable[None] | None]] | None = None,
        new_context: bool = False,
    ) -> bytes:
        ...

    @overload
    async def render(
        self,
        content: str,
        *,
        context: BrowserContext,
        extra_screenshot_option: ScreenshotOption | None = None,
        extra_page_modifiers: list[Callable[[Page], Awaitable[None] | None]] | None = None,
    ) -> bytes:
        ...

    async def render(
        self,
        content: str,
        *,
        browser: Browser | None = None,
        context: BrowserContext | None = None,
        extra_screenshot_option: ScreenshotOption | None = None,
        extra_page_option: PageOption | None = None,
        extra_page_modifiers: list[Callable[[Page], Awaitable[None] | None]] | None = None,
        new_context: bool = False,
        use_global_context: bool = True,
    ) -> bytes:
        """渲染 HTML 代码为图片

        Args:
            content (str): 要渲染的 HTML 代码
            browser (Optional[Browser], optional): Playwright 异步浏览器实例，
                如果 `context` 和 `browser` 都不传入则会通过 `Launart` 自动获取.
                当使用持久上下文（Persistence Context）模式启动 Playwright 时，
                不支持 `page_option` 和 `extra_page_option`.
            context (Optional[BrowserContext], optional): Playwright 浏览器上下文实例，
                如果 `context` 和 `browser` 都不传入则会通过 `Launart` 自动获取.
                与 `browser` 参数互斥，且不支持 `page_option` 和 `extra_page_option`.
            extra_screenshot_option (Optional[ScreenshotOption], optional): 额外的截图选项.
            extra_page_option (Optional[PageOption], optional): 额外的页面设置.
            extra_page_modifiers (List[Callable[[Page], Union[Awaitable[None], None]]], optional):
                接受 `Page` 实例的方法/函数.
                用于对 Page 本身进行额外的修改，如: 使用 `page.route` 重定向资源文件到本地文件.
                仅本次截图使用.
            new_content (bool, optional): 是否创建一个新上下文来渲染，可能可以避免一些
                cookie 之类的问题，默认为否.
            use_global_context (bool, optional): 是否使用全局的上下文来截图.
                当你使用持久上下文来启动 Playwright 时，必须使用全局上下文.
                当你使用了 `page_option` 参数时该参数会被忽略.

        Returns:
            bytes: 渲染结果图的 bytes 数据
        """
        screenshot_option: ScreenshotOption = {**self.screenshot_option, **(extra_screenshot_option or {})}
        page_modifiers: list[Callable[[Page], Awaitable[None] | None]] = self.page_modifiers + (
            extra_page_modifiers or []
        )

        launart = Launart.current()
        page_option: PageOption = {**self.page_option, **(extra_page_option or {})}

        if (browser is not None) and (context is not None):
            raise ValueError("Argument `browser` and `context` conflict with each other.")

        pw_service = launart.get_component(PlaywrightService)

        if page_option and pw_service.use_persistent_context:
            raise ValueError("`page_option` and `extra_page_option` conflicts with persistence context.")

        _context: BrowserContext | None = None

        if context is not None:
            page = await context.new_page()
            _bytes = await self._render(page, content, page_modifiers, screenshot_option)
            await page.close()
            return _bytes

        if browser is not None:
            _context = await browser.new_context()
            page = await _context.new_page()
            _bytes = await self._render(page, content, page_modifiers, screenshot_option)
            await page.close()
            await _context.close()
            return _bytes

        # if browser is None and context is None:
        async with pw_service.page(
            use_global_context=use_global_context, without_new_context=not new_context, **page_option
        ) as page:
            _bytes = await self._render(page, content, page_modifiers, screenshot_option)
            return _bytes

    async def _render(
        self,
        page: Page,
        content: str,
        page_modifiers: list[Callable[[Page], Awaitable[None] | None]],
        screenshot_option: ScreenshotOption,
    ) -> bytes:
        for modifier in page_modifiers:
            await run_always_await(modifier, page)

        await page.set_content(
            '<html><head><meta name="viewport" content="width=device-width,initial-scale=1.0">'
            f"<style>{self.style}</style></head><body>{content}<body></html>"
        )
        return await page.screenshot(**screenshot_option)
