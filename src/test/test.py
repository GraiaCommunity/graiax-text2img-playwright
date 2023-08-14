import asyncio
from pathlib import Path

from graiax.playwright import PlaywrightBrowser, PlaywrightService
from launart import Launart, Service

from graiax.text2img.playwright import (
    HTMLRenderer,
    MarkdownConverter,
    PageOption,
    ScreenshotOption,
    convert_text,
)
from graiax.text2img.playwright.plugins.container import (
    DANGER,
    TIP,
    WARNING,
    Container,
    ContainerColor,
)


class Test(Service):
    id = "test"

    @property
    def required(self):
        return {PlaywrightBrowser}

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, _: Launart):
        async with self.stage("blocking"):
            Path("test-result").mkdir(exist_ok=True)
            text = Path("src/test/test.md").read_text(encoding="utf8")
            renderer = HTMLRenderer(
                page_option=PageOption(viewport={"width": 840, "height": 1}, device_scale_factor=2),
                screenshot_option=ScreenshotOption(type="jpeg", quality=80, scale="device"),
            )
            await renderer.render(
                MarkdownConverter(
                    extra_plugins=[
                        TIP,
                        WARNING,
                        DANGER,
                        Container(ContainerColor("#1166ff", "#0033ee", "rgba(16, 25, 180, .05)"), "blue"),
                    ]
                ).convert(text),
                extra_screenshot_option=ScreenshotOption(path="test-result/md.jpg"),
            )
            await renderer.render(
                convert_text("# Test\n\nTesting message!"),
                extra_screenshot_option=ScreenshotOption(path="test-result/text.jpg"),
            )


loop = asyncio.new_event_loop()
launart = Launart()

launart.add_component(PlaywrightService("chromium", viewport={"width": 340, "height": 1}))
launart.add_component(Test())

launart.launch_blocking()

launart.status.exiting = True
if launart.task_group is not None:
    launart.task_group.stop = True
    task = launart.task_group.blocking_task
    if task and not task.done():
        task.cancel()
