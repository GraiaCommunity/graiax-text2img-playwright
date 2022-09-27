"""
移植自 https://github.com/vuepress/vuepress-next/blob/main/packages/markdown/src/plugins/codePlugin/languages.ts
"""

import re

languages_map = {
    "Bash": {"ext": "sh", "aliases": ("bash", "sh", "zsh", "shell")},
    "Batchfile": {"ext": "bat", "aliases": ("batch", "bat", "cmd")},
    "C": {"ext": "c", "aliases": ("c",)},
    "C#": {"ext": "cs", "aliases": ("csharp", "c#", "cs")},
    "C++": {"ext": "cpp", "aliases": ("cpp", "c++")},
    "CSS": {"ext": "css", "aliases": ("css",)},
    "Diff": {"ext": "diff", "aliases": ("diff",)},
    "Docker": {"ext": "docker", "aliases": ("docker", "dockerfile")},
    "Fish": {"ext": "fish", "aliases": ("fish", "fishshell")},
    "Go": {"ext": "go", "aliases": ("go", "golang")},
    "HTML": {"ext": "html", "aliases": ("html",)},
    "Java": {"ext": "java", "aliases": ("java",)},
    "JavaScript": {"ext": "js", "aliases": ("javascript", "js")},
    "JSON": {"ext": "json", "aliases": ("json",)},
    "Kotlin": {"ext": "kt", "aliases": ("kotlin", "kt")},
    "Lua": {"ext": "lua", "aliases": ("lua",)},
    "Makefile": {"ext": "Makefile", "aliases": ("make", "makefile")},
    "Markdown": {"ext": "md", "aliases": ("markdown", "md")},
    "PHP": {"ext": "php", "aliases": ("php",)},
    "PowerShell": {"ext": "pwsh", "aliases": ("powershell", "pwsh", "posh", "ps1")},
    "Python": {"ext": "py", "aliases": ("python", "py")},
    "Python Traceback": {"ext": "py", "aliases": ("pytb", "py3tb")},
    "Ruby": {"ext": "ruby", "aliases": ("ruby", "rb")},
    "Rust": {"ext": "rust", "aliases": ("rust", "rs")},
    "Sass": {"ext": "sass", "aliases": ("sass",)},
    "SCSS": {"ext": "scss", "aliases": ("scss",)},
    "TOML": {"ext": "toml", "aliases": ("toml",)},
    "TypeScript": {"ext": "ts", "aliases": ("typescript", "ts")},
    "XML": {"ext": "xml", "aliases": ("xml",)},
    "YAML": {"ext": "yaml", "aliases": ("yaml", "yml")},
}

result = {}

for lang, data in languages_map.items():
    for alias in data["aliases"]:
        result[alias] = {"name": lang, "ext": data["ext"]}

languages_map = result.copy()
del result


def resolve_language(info: str):
    if alias := re.match(r"^([^ :[{]+)", info):
        return languages_map[alias.group()] if alias.group() in languages_map else {"name": "text", "ext": ""}
    else:
        return {"name": "text", "ext": ""}
