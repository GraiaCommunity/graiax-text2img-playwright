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
    """转换 Markdown 文本至 HTML 代码

    Args:
        content (str): 要被转换为 HTML 的 Markdown 文本

    Returns:
        str: 生成的 HTML 代码
    """
    return _GLOBAL_MD_CONVERTER.convert(content)
