from .converter import MarkdownConverter, convert_text
from .plugins.container import Container, ContainerColor
from .renderer import HTMLRenderer, PageOption, ScreenshotOption
from .utils import MdPlugin

__all__ = [
    "convert_text",
    "convert_md",
    "MarkdownConverter",
    "Container",
    "ContainerColor",
    "HTMLRenderer",
    "PageOption",
    "ScreenshotOption",
    "MdPlugin",
]

_GLOBAL_MD_CONVERTER = MarkdownConverter()


def convert_md(content: str) -> str:
    return _GLOBAL_MD_CONVERTER.convert(content)
