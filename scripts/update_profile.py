#!/usr/bin/env python3
"""Generate profile metrics and update the dynamic README section.

Uses only GitHub's public repository data and the workflow-provided GITHUB_TOKEN.
"""

from __future__ import annotations

import html
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

USERNAME = "faveroo"
PROFILE_REPO = "faveroo"
README = Path("README.md")
METRICS = Path("assets/generated/metrics.svg")
START = "<!-- RECENT-WORK:START -->"
END = "<!-- RECENT-WORK:END -->"


def github_json(url: str):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": f"{USERNAME}-profile-workflow",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = Request(url, headers=headers)
    with urlopen(request, timeout=20) as response:
        return json.load(response)


def public_repositories() -> list[dict]:
    repos = github_json(
        f"https://api.github.com/users/{USERNAME}/repos"
        "?per_page=100&type=owner&sort=updated"
    )
    return [repo for repo in repos if not repo.get("private", False)]


def meaningful_repositories(repos: list[dict]) -> list[dict]:
    return [
        repo
        for repo in repos
        if repo["name"] != PROFILE_REPO
        and not repo.get("fork", False)
        and not repo.get("archived", False)
    ]


def recent_work_markdown(repos: list[dict]) -> str:
    selected = meaningful_repositories(repos)[:3]
    if not selected:
        return "_No recent public repository activity available._"

    lines = []
    for repo in selected:
        description = (repo.get("description") or "Public repository").strip()
        language = repo.get("language") or "Code"
        lines.append(
            f"- **[{repo['name']}]({repo['html_url']})** — {description} "
            f"`{language}`"
        )
    return "\n".join(lines)


def update_readme(recent_markdown: str) -> None:
    content = README.read_text(encoding="utf-8")
    if START not in content or END not in content:
        raise RuntimeError("README dynamic markers were not found")

    before, remainder = content.split(START, 1)
    _, after = remainder.split(END, 1)
    updated = f"{before}{START}\n{recent_markdown}\n{END}{after}"
    README.write_text(updated, encoding="utf-8")


def generate_metrics_svg(repos: list[dict]) -> None:
    meaningful = meaningful_repositories(repos)
    stars = sum(repo.get("stargazers_count", 0) for repo in meaningful)
    forks = sum(repo.get("forks_count", 0) for repo in meaningful)
    languages = Counter(
        repo["language"] for repo in meaningful if repo.get("language")
    )
    top_languages = " · ".join(language for language, _ in languages.most_common(4))
    top_languages = top_languages or "Public repositories"
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    values = [
        ("PUBLIC REPOS", str(len(repos))),
        ("OWN PROJECTS", str(len(meaningful))),
        ("STARS", str(stars)),
        ("FORKS", str(forks)),
    ]

    cards = []
    for index, (label, value) in enumerate(values):
        x = 28 + index * 190
        cards.append(
            f'<rect x="{x}" y="30" width="170" height="82" rx="12" '
            'fill="#161b22" stroke="#30363d"/>'
            f'<text x="{x + 16}" y="58" fill="#8b949e" font-size="12" '
            'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">'
            f'{html.escape(label)}</text>'
            f'<text x="{x + 16}" y="91" fill="#f0f6fc" font-size="28" '
            'font-family="-apple-system,BlinkMacSystemFont,Segoe UI,sans-serif" '
            f'font-weight="700">{html.escape(value)}</text>'
        )

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="800" height="165" viewBox="0 0 800 165" role="img" aria-labelledby="title desc">
  <title id="title">Gabriel Favero GitHub metrics</title>
  <desc id="desc">Public repository metrics generated from the GitHub API.</desc>
  <rect width="800" height="165" rx="16" fill="#0d1117" stroke="#30363d"/>
  {''.join(cards)}
  <text x="28" y="142" fill="#8b949e" font-size="13" font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace">{html.escape(top_languages)} · updated {generated}</text>
</svg>'''

    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(svg, encoding="utf-8")


def main() -> None:
    repos = public_repositories()
    generate_metrics_svg(repos)
    update_readme(recent_work_markdown(repos))


if __name__ == "__main__":
    main()
