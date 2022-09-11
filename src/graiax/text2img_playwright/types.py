from pathlib import Path
from typing import List, Literal, Optional, Union

from playwright._impl._api_structures import FloatRect
from playwright.async_api._generated import Locator
from typing_extensions import TypedDict


class ScreenshotParm(TypedDict, total=False):
    timeout: Optional[float]
    type: Optional[Literal["jpeg", "png"]]
    path: Optional[Union[str, Path]]
    quality: Optional[int]
    omit_background: Optional[bool]
    full_page: Optional[bool]
    clip: Optional[FloatRect]
    animations: Optional[Literal["allow", "disabled"]]
    caret: Optional[Literal["hide", "initial"]]
    scale: Optional[Literal["css", "device"]]
    mask: Optional[List["Locator"]]
