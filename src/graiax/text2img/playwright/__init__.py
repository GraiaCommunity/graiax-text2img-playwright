from .renderer import HTMLRenderer as HTMLRenderer
from .converter import convert_text as convert_text, MarkdownConverter as MarkdownConverter
from .plugins.container import Container as Container, ContainerColor as ContainerColor
from .utils import MdPlugin as MdPlugin
from .renderer import PageOption as PageOption
from .renderer import ScreenshotOption as ScreenshotOption

_GLOBAL_MD_CONVERTER = MarkdownConverter()


def convert_md(content: str) -> str:
    return _GLOBAL_MD_CONVERTER.convert(content)
