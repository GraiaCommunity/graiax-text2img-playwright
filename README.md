<div align="center">

# (WIP) Graiax Text2img Playwright

*(WIP) 基于 Playwright 的适用于 Graia 的文转图工具*

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![License](https://img.shields.io/github/license/GraiaCommunity/graiax-text2img-playwright)](https://github.com/GraiaCommunity/graiax-text2img-playwright/blob/master/LICENSE)
[![pdm-managed](https://img.shields.io/badge/pdm-managed-blueviolet)](https://pdm.fming.dev)
[![PyPI](https://img.shields.io/pypi/v/graiax-text2img-playwright)](https://img.shields.io/pypi/v/graiax-text2img-playwright)

</div>

Graiax Text2img Playwright 是一个基于 [Graiax Playwright](https://github.com/GraiaCommunity/graiax-playwright) 的文转图工具，
其可以将纯文本、Markdown 或 JinJa2 的模板通过 Playwright 转换为图片。

## 安装

`pdm add graiax-text2img-playwright` 或 `poetry add graiax-text2img-playwright`。

> 我们强烈建议使用包管理器或虚拟环境

## 开始使用

以下示例以 Ariadne 为例。

### 配合 Graia Saya 使用

```python
from graiax.text2img_playwright import md2img

md = '''\
<div align="center">

# (WIP) Graiax Text2img Playwright

*(WIP) 基于 Playwright 的适用于 Graia 的文转图工具*

</div>

Graiax Text2img Playwright 是一个基于 [Graiax Playwright](https://github.com/GraiaCommunity/graiax-playwright) 的文转图工具，
其可以将纯文本、Markdown 或 JinJa2 的模板通过 Playwright 转换为图片。

## 安装

`pdm add graiax-text2img-playwright` 或 `poetry add graiax-text2img-playwright`。

> 我们强烈建议使用包管理器或虚拟环境
'''

@listen(FriendMessage)
async def function(app: Ariadne, friend: Friend):
    image_bytes = md2img(md, highlight=True)
    app.sendMessage(friend, MessageChain(Image(data_bytes=image_bytes)))
```
