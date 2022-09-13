def text2html(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n").strip()
    return "".join(f"<p>{_}</p>" for _ in text.split("\n"))
