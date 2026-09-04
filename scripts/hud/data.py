"""Fetch the numbers the interface displays. Nothing here is invented:
every field comes from the GitHub GraphQL API or from `git` itself."""
from __future__ import annotations

import json
import subprocess
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

QUERY = """
query($login: String!) {
  user(login: $login) {
    login
    name
    createdAt
    followers { totalCount }
    publicRepos: repositories(privacy: PUBLIC, ownerAffiliations: OWNER) { totalCount }
    owned: repositories(first: 100, ownerAffiliations: OWNER, isFork: false,
                        orderBy: {field: STARGAZERS, direction: DESC}) {
      nodes { name stargazerCount primaryLanguage { name } }
    }
    contributionsCollection {
      totalCommitContributions
      totalPullRequestContributions
      totalIssueContributions
      totalRepositoriesWithContributedCommits
      contributionCalendar {
        totalContributions
        weeks { firstDay contributionDays { contributionCount date } }
      }
    }
  }
}
"""


@dataclass
class Telemetry:
    login: str = "shuccii"
    name: str = ""
    commits: int = 0
    contributions: int = 0
    prs: int = 0
    issues: int = 0
    repos: int = 0
    stars: int = 0
    followers: int = 0
    since: str = "—"
    top_language: str = "—"
    languages: list[tuple[str, int]] = field(default_factory=list)
    weeks: list[int] = field(default_factory=list)      # weekly contribution totals
    week_starts: list[str] = field(default_factory=list)
    sha: str = "—"
    branch: str = "main"
    synced: str = ""
    live: bool = False

    @property
    def peak_week(self) -> int:
        return max(self.weeks) if self.weeks else 0

    @property
    def active_weeks(self) -> int:
        return sum(1 for w in self.weeks if w)


def _git(*args: str) -> str:
    try:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                              text=True, check=True).stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""


def _graphql(login: str, token: str) -> dict:
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": login}}).encode(),
        headers={"Authorization": f"bearer {token}",
                 "Content-Type": "application/json",
                 "User-Agent": "shuccii-hud"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if payload.get("errors"):
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def collect(login: str, token: str | None) -> Telemetry:
    t = Telemetry(login=login)
    t.synced = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    t.sha = _git("rev-parse", "--short", "HEAD") or "—"
    t.branch = _git("rev-parse", "--abbrev-ref", "HEAD") or "main"
    t.name = login.upper()

    if not token:
        print("::warning::no GITHUB_TOKEN — drawing the interface without live telemetry")
        return t

    try:
        user = _graphql(login, token)
    except Exception as exc:                                   # noqa: BLE001
        print(f"::warning::telemetry query failed ({exc}) — keeping the previous render")
        return t

    cc = user["contributionsCollection"]
    cal = cc["contributionCalendar"]
    nodes = user["owned"]["nodes"]

    counts: dict[str, int] = {}
    for n in nodes:
        lang = (n.get("primaryLanguage") or {}).get("name")
        if lang:
            counts[lang] = counts.get(lang, 0) + 1

    t.name = (user.get("name") or login).upper()
    t.commits = cc["totalCommitContributions"]
    t.prs = cc["totalPullRequestContributions"]
    t.issues = cc["totalIssueContributions"]
    t.contributions = cal["totalContributions"]
    t.repos = user["publicRepos"]["totalCount"]
    t.stars = sum(n["stargazerCount"] for n in nodes)
    t.followers = user["followers"]["totalCount"]
    t.since = user["createdAt"][:4]
    t.languages = sorted(counts.items(), key=lambda kv: -kv[1])
    t.top_language = t.languages[0][0] if t.languages else "—"
    t.weeks = [sum(d["contributionCount"] for d in w["contributionDays"]) for w in cal["weeks"]]
    t.week_starts = [w["firstDay"] for w in cal["weeks"]]
    t.live = True
    return t
