from typing import Any, Callable, Generic, Protocol, runtime_checkable

from markdown_it import MarkdownIt
from typing_extensions import Concatenate, ParamSpec

P = ParamSpec("P")


@runtime_checkable
class MdPluginBase(Protocol):
    def apply(self, md: MarkdownIt) -> Any:
        ...


class MdPlugin(Generic[P]):
    def __init__(self, plugin: Callable[Concatenate[MarkdownIt, P], Any], *args: P.args, **kwargs: P.kwargs) -> None:
        self.func = plugin
        self.args = args
        self.kwargs = kwargs

    def apply(self, md: MarkdownIt):
        self.func(md, *self.args, **self.kwargs)
