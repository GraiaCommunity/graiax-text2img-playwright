import asyncio
from os import remove

from graiax.playwright import PlaywrightBrowser, PlaywrightService
from launart import Launart, Launchable

from graiax.text2img_playwright import *


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
            with open("src/test/test.txt", encoding="utf8") as fp:
                await md2img(fp.read())
            with open("graiax-text2img-playwright_test.jpg", 'wb') as f:
                with open("src/test/test.txt", encoding="utf8") as fp:
                    f.write(await md2img(fp.read(), hightlight=True))
            await asyncio.sleep(10)
            remove("graiax-text2img-playwright_test.jpg")


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
