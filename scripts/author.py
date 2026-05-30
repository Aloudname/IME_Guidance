#!/usr/bin/env python3
"""
`git push` 时触发的功能函数
GitHub Actions 将 `@author(...)` 替换为 HTML
"""

import re, sys
from pathlib import Path
from typing import Optional


def badge(username: str, desc: "Optional[str]" = None) -> str:
    """内容定义"""
    parts = [
        f'<img src="https://github.com/{username}.png?size=40"'
        f' width="22" style="border-radius:50%;vertical-align:middle"'
        f' alt="{username}"/>',
        f' **[<span style="color:inherit;">{username}</span>](https://github.com/{username})**',
    ]
    if desc:
        parts.append(f" · *{desc.strip()}*")
    return " ".join(parts)


def render_author_block(match: re.Match) -> str:
    """渲染函数"""
    raw = match.group(1).strip()

    # Split by | to get individual author specs
    specs = [s.strip() for s in raw.split("|")]

    badges: list[str] = []
    for spec in specs:
        if "," in spec:
            username, desc = spec.split(",", 1)
            badges.append(badge(username.strip(), desc.strip()))
        else:
            badges.append(badge(spec.strip()))

    if len(badges) == 1:
        return f"> {badges[0]}"
    else:
        return "> " + " &nbsp;|&nbsp; ".join(badges)


# 遍历项目文件夹
AUTHOR_RE = re.compile(r"@author\((.+?)\)")

SKIP_DIRS = {".git", ".claude", ".github", "scripts", "node_modules", "__pycache__"}


def process_file(path: Path) -> bool:
    """单文件函数，查找替换 @author"""
    original = path.read_text(encoding="utf-8")
    if "@author(" not in original:
        return False

    replaced = AUTHOR_RE.sub(render_author_block, original)
    if replaced != original:
        path.write_text(replaced, encoding="utf-8")
        return True
    return False


def process_repo(root: Path) -> int:
    """仓库函数"""
    count = 0
    for md_file in root.rglob("*.md"):
        # Skip files inside ignored directories
        if any(p in SKIP_DIRS for p in md_file.parts):
            continue
        if process_file(md_file):
            print(f"  ✓ {md_file.relative_to(root)}")
            count += 1
    return count


def main() -> None:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    changed = process_repo(root)


if __name__ == "__main__":
    main()
