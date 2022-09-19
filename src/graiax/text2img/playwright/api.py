from typing import Optional

from graiax.playwright import PlaywrightBrowser
from launart import Launart

from .types import NewPageParms, ScreenshotParms


async def html2img(
    html: str,
    new_page_args: Optional[NewPageParms] = None,
    screenshot_args: Optional[ScreenshotParms] = None,
) -> bytes:
    if new_page_args is None:
        new_page_args = {}
    if screenshot_args is None:
        screenshot_args = {}

    if "full_page" not in screenshot_args:
        screenshot_args["full_page"] = True
    if "type" not in screenshot_args:
        screenshot_args["type"] = "jpeg"

    launart = Launart.current()
    browser = launart.get_interface(PlaywrightBrowser)

    page = await browser.new_page(**new_page_args)

    try:
        await page.set_content(html)
        return await page.screenshot(**screenshot_args)
    finally:
        await page.close()
