"""将指定类型转换为 HTML.
"""

from __future__ import annotations

from enum import Enum
from typing import Sequence, overload

from markdown_it import MarkdownIt
from mdit_py_emoji import emoji_plugin
from mdit_py_plugins.anchors.index import anchors_plugin
from mdit_py_plugins.footnote.index import footnote_plugin
from mdit_py_plugins.front_matter.index import front_matter_plugin
from mdit_py_plugins.tasklists import tasklists_plugin

from .plugins import container
from .plugins.code import code_plugin
from .plugins.code.highlighter import Highlighter
from .utils import MdPlugin, MdPluginBase


def convert_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return "".join(('<div class="container">', "".join(f"<p>{s}</p>" for s in text.split("\n")), "</div>"))


class DefaultPlugin(Enum):
    value: MdPlugin

    emoji = MdPlugin(emoji_plugin)
    anchors = MdPlugin(anchors_plugin)
    footnote = MdPlugin(footnote_plugin)
    front_matter = MdPlugin(front_matter_plugin)
    task_lists = MdPlugin(tasklists_plugin)
    code = MdPlugin(code_plugin)


class MarkdownConverter:
    @overload
    def __init__(
        self,
        md: None = None,
        default_plugins: Sequence[DefaultPlugin] = ...,
        extra_plugins: Sequence[MdPluginBase] = ...,
        *,
        highlighter: Highlighter = Highlighter(),
    ):
        ...

    @overload
    def __init__(
        self,
        md: MarkdownIt,
        default_plugins: Sequence[DefaultPlugin] = ...,
        extra_plugins: Sequence[MdPluginBase] = ...,
    ):
        ...

    def __init__(
        self,
        md: MarkdownIt | None = None,
        default_plugins: Sequence[DefaultPlugin] = (
            DefaultPlugin.emoji,
            DefaultPlugin.anchors,
            DefaultPlugin.footnote,
            DefaultPlugin.front_matter,
            DefaultPlugin.task_lists,
            DefaultPlugin.code,
        ),
        extra_plugins: Sequence[MdPluginBase] = (
            container.TIP,
            container.WARNING,
            container.DANGER,
        ),
        *,
        highlighter: Highlighter = Highlighter(),
    ) -> None:
        self.md = md or MarkdownIt("gfm-like", {"highlight": highlighter}).enable("table")
        for d in default_plugins:
            d.value.apply(self.md)
        for p in extra_plugins:
            p.apply(self.md)

    def convert(
        self,
        content: str,
    ) -> str:
        return f'<div class="markdown-body">{self.md.render(content)}</div>'
