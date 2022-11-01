import asyncio

from graiax.playwright import PlaywrightBrowser, PlaywrightService
from launart import Launart, Launchable

from graiax.text2img.playwright.builtin import *
from graiax.text2img.playwright.types import *


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
            with open("src/test/test.txt", encoding="utf8") as fp:
                await MarkdownToImg().render(
                    fp.read(),
                    page_params=PageParams(viewport={"width": 840, "height": 10}, device_scale_factor=2),
                    screenshot_params=ScreenshotParams(type="jpeg", path="test.jpg", quality=80, scale="device"),
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
