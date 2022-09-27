from typing import List, MutableMapping

from markdown_it.token import Token
from markdown_it.utils import OptionsDict


class CreateContainer:
    klass: str
    default_title: str

    def __init__(self, klass: str, default_title: str):
        self.klass = klass
        self.default_title = default_title

    def create(self, tokens: List[Token], idx: int, options: OptionsDict, env: MutableMapping):
        token: Token = tokens[idx]
        info = token.info.strip()[len(self.klass) :].strip()

        if token.nesting == 1:
            return f'<div class="{self.klass} custom-block"><p class="custom-block-title">{info or self.default_title}</p>\n'
        else:
            return "</div>\n"

    def validate(self, marker: str, _):
        return True if marker.startswith(self.klass) else False
