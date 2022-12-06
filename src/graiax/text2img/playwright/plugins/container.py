from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Union

from markdown_it import MarkdownIt
from markdown_it.token import Token
from mdit_py_plugins.container.index import container_plugin

from ..utils import MdPluginBase


@dataclass
class ContainerColor:
    """自定义容器的颜色

    Returns:
        color (str): 文本颜色
        border_color (str): 边框颜色
        background_color (str): 背景颜色
    """

    color: str
    border_color: str
    background_color: str

    def to_style(self) -> str:
        """生成对应的 CSS"""
        return ";".join(
            (
                f"color:{self.color}",
                f"border-color:{self.border_color}",
                f"background-color:{self.background_color}",
            )
        )


class Container(MdPluginBase):
    """自定义容器

    该容器使用与 VitePress 的 Container 相同的样式

    用法:
        ```markdown
        # Container 测试

        :::tip
        我是 tip
        :::
        ```

    Args:
        style (Union[ContainerColor, str]): 容器的颜色设置或自定义 CSS.
        name (str): 容器的名字，在 Markdown 文本中使用.
        title (Optional[str], optional): 容器的默认标题.
    """

    name: str
    title: str
    style: str

    def __init__(self, style: Union[ContainerColor, str], name: str, title: Optional[str] = None) -> None:
        self.name = name
        self.title = title or name
        self.style = style.to_style() if isinstance(style, ContainerColor) else style

    def render_impl(self, tokens: List[Token], idx: int):
        token: Token = tokens[idx]
        info = token.info.strip()[len(self.name) :].strip()

        if token.nesting == 1:
            return (
                f'<div style="{self.style}" class="{self.name} container-block">'
                f'<p class="container-block-title">{info or self.title}</p>\n'
            )
        else:
            return "</div>\n"

    def validate(self, marker: str, _):
        return bool(marker.startswith(self.name))

    def apply(self, md: MarkdownIt):
        def render(_, tokens, idx, *__):
            return self.render_impl(tokens, idx)

        container_plugin(md, self.name, validate=self.validate, render=render)


WARNING = Container(ContainerColor("#ad850e", "rgba(255, 197, 23, .5)", "rgba(255, 197, 23, .05)"), "warning", "注意")
TIP = Container(ContainerColor("#155f3e", "rgba(66, 184, 131, .5)", "rgba(66, 184, 131, .05)"), "tip", "提示")
DANGER = Container(ContainerColor("#ab2131", "rgba(237, 60, 80, .5)", "rgba(237, 60, 80, .05)"), "danger", "警告")
