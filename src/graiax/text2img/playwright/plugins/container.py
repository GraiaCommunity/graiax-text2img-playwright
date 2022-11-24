from __future__ import annotations

from dataclasses import dataclass
from typing import MutableMapping

from markdown_it import MarkdownIt
from markdown_it.token import Token
from markdown_it.utils import OptionsDict
from mdit_py_plugins.container.index import container_plugin

from ..utils import MdPluginBase


@dataclass
class ContainerColor:
    color: str
    border_color: str
    background_color: str

    def to_style(self) -> str:
        return ";".join(
            (
                f"color:{self.color}",
                f"border-color:{self.border_color}",
                f"background-color:{self.background_color}",
            )
        )


class Container(MdPluginBase):
    def __init__(self, style: ContainerColor | str, name: str, title: str | None = None) -> None:
        self.name = name
        self.title = title or name
        self.style = style.to_style() if isinstance(style, ContainerColor) else style

    def render(self, tokens: list[Token], idx: int, options: OptionsDict, env: MutableMapping):
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
        container_plugin(md, self.name, validate=self.validate, render=self.render)


WARNING = Container(ContainerColor("#ad850e", "rgba(255, 197, 23, .5)", "rgba(255, 197, 23, .05)"), "warning", "注意")
TIP = Container(ContainerColor("#155f3e", "rgba(66, 184, 131, .5)", "rgba(66, 184, 131, .05)"), "tip", "提示")
DANGER = Container(ContainerColor("#ab2131", "rgba(237, 60, 80, .5)", "rgba(237, 60, 80, .05)"), "danger", "警告")
