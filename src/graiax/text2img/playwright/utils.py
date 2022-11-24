from typing import Any, Callable, Generic, Protocol, runtime_checkable

from markdown_it import MarkdownIt
from typing_extensions import Concatenate, ParamSpec

P = ParamSpec("P")


@runtime_checkable
class MdPluginBase(Protocol):
    """MdPlugin 协议

    MdPlugin 必须含有 apply 方法，该方法接受一个 MarkdownIt 实例并将自身应用于该实例上
    """

    def apply(self, md: MarkdownIt) -> Any:
        """将 MarkdownIt 插件应用到 MarkdownIt 实例

        Args:
            md (MarkdownIt): MarkdownIt 实例
        """
        ...


class MdPlugin(Generic[P]):
    """MdPlugin 基类

    定义一个可被 GraiaX TextToImage (Playwright) 识别并加载的 MdPlugin

    Args:
        plugin (Callable[Concatenate[MarkdownIt, P], Any]): 可将 MarkdownIt 插件应用到 MarkdownIt 实例的函数/方法或 MarkdownIt 插件本身
    """

    def __init__(self, plugin: Callable[Concatenate[MarkdownIt, P], Any], *args: P.args, **kwargs: P.kwargs) -> None:
        self.func = plugin
        self.args = args
        self.kwargs = kwargs

    def apply(self, md: MarkdownIt):
        """将 MarkdownIt 插件应用到 MarkdownIt 实例

        Args:
            md (MarkdownIt): MarkdownIt 实例
        """
        self.func(md, *self.args, **self.kwargs)
