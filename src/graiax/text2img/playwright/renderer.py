from __future__ import annotations

import importlib.resources
from enum import Enum
from pathlib import Path
from typing import Awaitable, Callable, List, Literal, Optional, Sequence, Union, overload

from graiax.playwright import PlaywrightBrowser
from graiax.playwright.interface import Parameters as PageOption
from launart import Launart
from playwright.async_api import Page, BrowserContext, Browser
from playwright.async_api._generated import Locator
from typing_extensions import TypedDict


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
            当设置为 `device` 时，则根据设备的屏幕缩放设置或当前 Playwright 的 Page/Context 中的 device_scale_factor 参数缩放.
        mask (List["Locator"]], optional): 指定截图时的遮罩的 Locator。元素将被一颜色为 #FF00FF 的框覆盖.
    """

    timeout: Optional[float]
    type: Literal["jpeg", "png", None]
    path: Optional[Union[str, Path]]
    quality: Optional[int]
    omit_background: Optional[bool]
    full_page: Optional[bool]
    clip: Optional[FloatRect]
    animations: Literal["allow", "disabled", None]
    caret: Literal["hide", "initial", None]
    scale: Literal["css", "device", None]
    mask: Optional[List["Locator"]]


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
        page_modifiers (List[Callable[[Page], Awaitable]], optional): 接受 Page 实例的方法/函数.
            用于对 Page 本身进行额外的修改，如: 使用 page.route 重定向资源文件到本地文件.
    """

    page_option: PageOption
    screenshot_option: ScreenshotOption
    style: str
    page_modifiers: List[Callable[[Page], Awaitable]]

    def __init__(
        self,
        page_option: Optional[PageOption] = None,
        screenshot_option: Optional[ScreenshotOption] = None,
        *,
        css: Sequence[Union[BuiltinCSS, str]] = (
            BuiltinCSS.reset,
            BuiltinCSS.github,
            BuiltinCSS.one_dark,
            BuiltinCSS.container,
        ),
        page_modifiers: Optional[List[Callable[[Page], Awaitable]]] = None,
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
        extra_screenshot_option: Optional[ScreenshotOption] = None,
        extra_page_option: Optional[PageOption] = None,
        extra_page_modifiers: Optional[List[Callable[[Page], Awaitable]]] = None,
        browser: Optional[Browser] = None,
    ) -> bytes:
        ...

    @overload
    async def render(
        self,
        content: str,
        *,
        extra_screenshot_option: Optional[ScreenshotOption] = None,
        extra_page_modifiers: Optional[List[Callable[[Page], Awaitable]]] = None,
        context: BrowserContext,
    ) -> bytes:
        ...

    async def render(
        self,
        content: str,
        *,
        extra_screenshot_option: Optional[ScreenshotOption] = None,
        extra_page_option: Optional[PageOption] = None,
        extra_page_modifiers: Optional[List[Callable[[Page], Awaitable]]] = None,
        browser: Optional[Browser] = None,
        context: Optional[BrowserContext] = None,
    ) -> bytes:
        """渲染 HTML 代码为图片

        Args:
            content (str): 要渲染的 HTML 代码
            extra_screenshot_option (Optional[ScreenshotOption], optional): 额外的截图选项.
            extra_page_option (Optional[PageOption], optional): 额外的页面设置.
            extra_page_modifiers (List[Callable[[Page], Awaitable]], optional): 接受 `Page` 实例的方法/函数.
                用于对 Page 本身进行额外的修改，如: 使用 `page.route` 重定向资源文件到本地文件.
                仅本次截图使用.
            browser (Optional[Browser], optional): Playwright 异步浏览器实例，
                如果 `context` 和 `browser` 都不传入则会通过 `Launart` 获取.
            context (Optional[BrowserContext], optional): Playwright 浏览器上下文实例，
                和 `browser` 参数互斥，并且不能和 `extra_page_option` 一起传入.

        Returns:
            bytes: 渲染结果图的 bytes 数据
        """
        screenshot_option: ScreenshotOption = {**self.screenshot_option, **(extra_screenshot_option or {})}
        page_modifiers: List[Callable[[Page], Awaitable]] = self.page_modifiers + (extra_page_modifiers or [])

        if context is None:
            browser = browser or Launart.current().get_interface(PlaywrightBrowser)
            page_option: PageOption = {**self.page_option, **(extra_page_option or {})}
            page = await browser.new_page(**page_option)
        elif extra_page_option is not None:
            raise ValueError("`extra_page_option` conflicts with `context` argument.")
        else:
            page = await context.new_page()
        for modifier in page_modifiers:
            await modifier(page)
        await page.set_content(
            '<html><head><meta name="viewport" content="width=device-width,initial-scale=1.0">'
            f"<style>{self.style}</style></head><body>{content}<body></html>"
        )
        result = await page.screenshot(**screenshot_option)
        await page.close()
        return result
