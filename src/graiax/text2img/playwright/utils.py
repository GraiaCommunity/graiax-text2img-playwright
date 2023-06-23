from inspect import isawaitable
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


async def run_always_await(callable, *args, **kwargs):
    """Run a callable or awaitable function

    - source: https://github.com/GraiaProject/BroadcastControl/blob/19ca73543bc6d8453a5b3233e814b41107e35423/src/graia/broadcast/utilles.py#L31
    - license: MIT

    Args:
        callable (Callable[[Any], Union[Awaitable[Any], Any]):
            Function that need to be run.
        *args:
            Variable length argument list.
        **kwargs:
            Arbitrary keyword arguments.
    Returns:
        Return value of the function being run.
    """
    obj = callable(*args, **kwargs)
    while isawaitable(obj):
        obj = await obj
    return obj
