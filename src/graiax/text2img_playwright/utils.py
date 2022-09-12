from .types import ScreenshotParms


def text2html(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return "".join(f"<p>{_}</p>" for _ in text.split("\n"))


def update_screenshot_args(screenshot_args: ScreenshotParms) -> ScreenshotParms:
    if "full_page" not in screenshot_args:
        screenshot_args["full_page"] = True
    if "type" not in screenshot_args:
        screenshot_args["type"] = "jpeg"
    return screenshot_args
