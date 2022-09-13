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
