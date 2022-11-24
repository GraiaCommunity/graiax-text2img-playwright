import asyncio

from graiax.playwright import PlaywrightBrowser, PlaywrightService
from launart import Launart, Launchable

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


class Test(Launchable):
    id = "test"

    @property
    def required(self):
        return {PlaywrightBrowser}

    @property
    def stages(self):
        return {"blocking"}

    async def launch(self, _: Launart):
        async with self.stage("blocking"):
            # with open("src/README.md", encoding="utf8") as fp:
            #     await md2img(
            #         fp.read(),
            #         page_params={"viewport": {"width": 840, "height": 10}, "device_scale_factor": 1.5},
            #         screenshot_args={"path": "test.jpg", "quality": 80, "scale": "device"},
            #     )
            with open("src/test/test.md", encoding="utf8") as fp:
                renderer = HTMLRenderer(
                    page_option=PageOption(viewport={"width": 840, "height": 1000}, device_scale_factor=2),
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
                    ).convert(fp.read()),
                    extra_screenshot_option=ScreenshotOption(path="md.jpg"),
                )
                await renderer.render(
                    convert_text("Testing message!"), extra_screenshot_option=ScreenshotOption(path="text.jpg")
                )


loop = asyncio.new_event_loop()
launart = Launart()

launart.add_service(PlaywrightService("chromium"))
launart.add_launchable(Test())

launart.launch_blocking()

launart.status.exiting = True
if launart.task_group is not None:
    launart.task_group.stop = True
    task = launart.task_group.blocking_task
    if task and not task.done():
        task.cancel()
