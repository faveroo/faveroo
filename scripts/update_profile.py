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
FULL_NAME = "Gabriel Favero Hoffmann"
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
    repos = []
    page = 1
    while True:
        batch = github_json(
            f"https://api.github.com/users/{USERNAME}/repos"
            f"?per_page=100&type=owner&sort=pushed&page={page}"
        )
        repos.extend(repo for repo in batch if not repo.get("private", False))
        if len(batch) < 100:
            return repos
        page += 1



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
    languages = Counter(repo["language"] for repo in meaningful if repo.get("language"))
    generated = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    values = [("PUBLIC REPOS", len(repos)), ("ORIGINAL PROJECTS", len(meaningful)),
              ("STARS EARNED", stars), ("PROJECT FORKS", forks)]
    parts = []
    for i, (label, value) in enumerate(values):
        x = 28 + i * 207
        parts.append(f'''<rect x="{x}" y="65" width="193" height="94" rx="10" fill="#1b1c23"/>
        <text x="{x+16}" y="91" fill="#b7b7c2" font-size="11" letter-spacing="1">{label}</text>
        <text x="{x+16}" y="139" fill="#f5f5f7" font-size="36" font-weight="700">{value}</text>''')
    total = sum(languages.values())
    for i, (language, count) in enumerate(languages.most_common(4)):
        x = 28 + (i % 2) * 424
        y = 215 + (i // 2) * 50
        parts.append(f'''<text x="{x}" y="{y}" fill="#e7e7eb" font-size="13">{html.escape(language)}</text>
        <text x="{x+392}" y="{y}" text-anchor="end" fill="#b7b7c2" font-size="12">{count} repos</text>
        <rect x="{x}" y="{y+10}" width="392" height="5" rx="2" fill="#303038"/>
        <rect x="{x}" y="{y+10}" width="{392*count/total:.1f}" height="5" rx="2" fill="#ff626f"/>''')
    if not total:
        parts.append('<text x="28" y="220" fill="#b7b7c2" font-size="13">No public repository language data available.</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="880" height="326" viewBox="0 0 880 326" role="img" aria-labelledby="title desc">
    <title id="title">{html.escape(FULL_NAME)} — GitHub in numbers</title>
    <desc id="desc">Public repositories: {len(repos)}. Original non-archived projects excluding this profile: {len(meaningful)}. Stars: {stars}. Forks: {forks}. Primary languages by repository count. Updated {generated}.</desc>
    <rect x="1" y="1" width="878" height="324" rx="16" fill="#101115" stroke="#303038"/>
    <g font-family="Arial,Helvetica,sans-serif">
    <text x="28" y="36" fill="#ff7b84" font-size="12" letter-spacing="2">PUBLIC WORK / GITHUB</text>
    <text x="850" y="36" text-anchor="end" fill="#b7b7c2" font-size="12">Updated {generated}</text>
    {''.join(parts)}
    <text x="28" y="187" fill="#b7b7c2" font-size="11" letter-spacing="1">PRIMARY LANGUAGES / ORIGINAL PROJECTS</text>
    <text x="28" y="307" fill="#b7b7c2" font-size="11">Source: GitHub API · Public repository data · Refreshed with GitHub Actions</text>
    </g></svg>'''
    METRICS.parent.mkdir(parents=True, exist_ok=True)
    METRICS.write_text(svg, encoding="utf-8")


def main() -> None:
    repos = public_repositories()
    generate_metrics_svg(repos)
    update_readme(recent_work_markdown(repos))


if __name__ == "__main__":
    main()
