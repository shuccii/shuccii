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
                        orderBy: {field: PUSHED_AT, direction: DESC}) {
      nodes {
        name
        stargazerCount
        pushedAt
        primaryLanguage { name }
        defaultBranchRef {
          name
          target { ... on Commit { history(first: 100) { nodes { messageHeadline committedDate oid } } } }
        }
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          totalSize
          edges { size node { name color } }
        }
      }
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
    days: list[int] = field(default_factory=list)       # daily totals, most recent last
    weekday: list[int] = field(default_factory=list)    # Sun..Sat totals over the year
    hours: list[int] = field(default_factory=list)      # commits per hour, JST
    day_dates: list[str] = field(default_factory=list)
    created: str = ""
    repos_detail: list[dict] = field(default_factory=list)
    commits_log: list[tuple[str, str, str]] = field(default_factory=list)  # (time, repo, headline)
    lang_bytes: list[tuple[str, int, str]] = field(default_factory=list)   # (name, bytes, colour)
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

    @property
    def years_on_github(self) -> int:
        if not self.created:
            return 0
        delta = datetime.now(timezone.utc) - datetime.fromisoformat(self.created.replace("Z", "+00:00"))
        return max(0, int(delta.days / 365.25))

    @property
    def peak_hour(self) -> int:
        return self.hours.index(max(self.hours)) if self.hours else 0


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
    t.days = [d["contributionCount"] for w in cal["weeks"] for d in w["contributionDays"]]
    t.day_dates = [d["date"] for w in cal["weeks"] for d in w["contributionDays"]]
    t.created = user["createdAt"]

    by_weekday = [0] * 7
    for w in cal["weeks"]:
        for d in w["contributionDays"]:
            # %w: Sunday == 0, matching the order GitHub lays the calendar out in
            by_weekday[int(datetime.fromisoformat(d["date"]).strftime("%w"))] += d["contributionCount"]
    t.weekday = by_weekday

    sizes: dict[str, int] = {}
    colours: dict[str, str] = {}
    for node in nodes:
        for edge in (node.get("languages") or {}).get("edges", []):
            name = edge["node"]["name"]
            sizes[name] = sizes.get(name, 0) + edge["size"]
            colours.setdefault(name, edge["node"].get("color") or "#7d8590")
    t.lang_bytes = sorted(((k, v, colours[k]) for k, v in sizes.items()),
                          key=lambda kv: -kv[1])

    log: list[tuple[str, str, str]] = []
    for node in nodes:
        branch = node.get("defaultBranchRef") or {}
        target = branch.get("target") or {}
        for c in (target.get("history") or {}).get("nodes", []):
            log.append((c["committedDate"], node["name"], c["messageHeadline"]))
    log.sort(reverse=True)
    t.commits_log = [(d[11:16], r, m) for d, r, m in log[:9]]

    # committedDate is UTC; the profile reads in JST
    by_hour = [0] * 24
    for iso, _, _ in log:
        by_hour[(int(iso[11:13]) + 9) % 24] += 1
    t.hours = by_hour

    t.repos_detail = [
        {"name": n["name"], "stars": n["stargazerCount"],
         "lang": (n.get("primaryLanguage") or {}).get("name") or "—",
         "pushed": (n.get("pushedAt") or "")[:10]}
        for n in nodes[:6]
    ]
    t.live = True
    return t
