from typing import Awaitable, Callable, List, Optional

from graiax.playwright import PlaywrightBrowser
from launart import Launart
from playwright.async_api import Page

from .types import PageParms, ScreenshotParms


async def html2img(
    html_code: str,
    *,
    page_parms: Optional[PageParms] = None,
    screenshot_parms: Optional[ScreenshotParms] = None,
    extra_page_methods: Optional[List[Callable[[Page], Awaitable]]] = None,
) -> bytes:
    """纯 HTML 代码转图片

    Args:
        html_code (str): HTML 代码
        page_parms (Optional[PageParms]): 默认为 None，用于新建 Playwright 页面的参数
        screenshot_parms (Optional[ScreenshotParms]): 默认为 None，用于 Playwright 截图的参数
        extra_page_methods (Optional[List[Callable[[Page], Awaitable]]]):
            默认为 None，用于 https://playwright.dev/python/docs/api/class-page 中提到的部分方法，
            如 `page.route(...)` 等
    """

    if page_parms is None:
        page_parms = {}
    if screenshot_parms is None:
        screenshot_parms = {}

    if "full_page" not in screenshot_parms:
        screenshot_parms["full_page"] = True
    if "type" not in screenshot_parms:
        screenshot_parms["type"] = "jpeg"

    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    page = await browser.new_page(**page_parms)

    if extra_page_methods is not None:
        for method in extra_page_methods:
            await method(page)

    try:
        await page.set_content(html_code)
        return await page.screenshot(**screenshot_parms)
    finally:
        await page.close()
