from __future__ import annotations

import importlib.resources
from enum import Enum
from pathlib import Path
from typing import Awaitable, Callable, Literal, Sequence

from graiax.playwright import PlaywrightBrowser
from graiax.playwright.interface import Parameters as PageOption
from launart import Launart
from playwright.async_api import Page
from playwright.async_api._generated import Locator
from typing_extensions import TypedDict


class FloatRect(TypedDict):
    x: float
    y: float
    width: float
    height: float


class ScreenshotOption(TypedDict, total=False):
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
    mask: list["Locator"] | None


_CSS_MOD = "graiax.text2img.playwright.css"


class BuiltinCSS(Enum):
    value: str

    container = importlib.resources.read_text(_CSS_MOD, "container.css")
    one_dark = importlib.resources.read_text(_CSS_MOD, "one-dark.css")
    github = importlib.resources.read_text(_CSS_MOD, "github.css")
    reset = importlib.resources.read_text(_CSS_MOD, "reset.css")


class HTMLRenderer:
    def __init__(
        self,
        page_option: PageOption | None = None,
        screenshot_option: ScreenshotOption | None = None,
        css: Sequence[BuiltinCSS | str] = (
            BuiltinCSS.github,
            BuiltinCSS.one_dark,
            BuiltinCSS.container,
            BuiltinCSS.reset,
        ),
    ):
        if isinstance(css, str):
            css = [css]
        page_option = page_option or {}
        screenshot_option = screenshot_option or {}
        screenshot_option = {"full_page": True, "type": "jpeg", **screenshot_option}

        self.page_option: PageOption = page_option
        self.screenshot_option: ScreenshotOption = screenshot_option
        self.style: str = "\n".join(i.value if isinstance(i, BuiltinCSS) else i for i in css)

    async def render(
        self,
        content: str,
        *,
        extra_screenshot_option: ScreenshotOption | None = None,
        extra_page_option: PageOption | None = None,
        page_modifiers: Sequence[Callable[[Page], Awaitable]] = (),
    ) -> bytes:
        browser = Launart.current().get_interface(PlaywrightBrowser)

        page_option: PageOption = {**self.page_option, **(extra_page_option or {})}
        screenshot_option: ScreenshotOption = {**self.screenshot_option, **(extra_screenshot_option or {})}

        async with browser.page(**page_option or {}) as page:
            for modifier in page_modifiers:
                await modifier(page)
            await page.set_content(
                '<meta name="viewport" content="width=device-width,initial-scale=1.0">\n'
                f"<style>{self.style}</style>\n"
                f"{content}"
            )
            return await page.screenshot(**screenshot_option or {})
