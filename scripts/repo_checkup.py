"""Repo 体检能力模块：GitHub 仓库六维体检（数据源 GitHub 公开 API）。"""

import json
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone

GH_API = "https://api.github.com"
UA = "repo-checkup-pay-skill/1.0"

MANIFESTS = ["package.json", "requirements.txt", "pyproject.toml",
             "go.mod", "Cargo.toml", "pom.xml", "Gemfile", "composer.json"]
CI_DIRS = [".github", "workflows"]


def gh_get(path: str):
    req = urllib.request.Request(
        f"{GH_API}{path}",
        headers={"User-Agent": UA, "Accept": "application/vnd.github+json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read().decode("utf-8", "replace")), dict(r.headers)
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode("utf-8", "replace"))
        except Exception:
            body = {}
        return e.code, body, dict(e.headers)
    except Exception as e:  # noqa: BLE001
        return 0, {"message": f"{type(e).__name__}: {e}"}, {}


def days_since(iso):
    if not iso:
        return None
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return max(0, (datetime.now(timezone.utc) - dt).days)
    except Exception:
        return None


def count_commits(owner, repo, default_branch):
    code, _, headers = gh_get(f"/repos/{owner}/{repo}/commits?per_page=1&sha={default_branch}")
    if code != 200:
        return None
    link = headers.get("Link") or headers.get("link") or ""
    if 'rel="last"' in link:
        try:
            return int(link.split("page=")[-1].split(">")[0])
        except Exception:
            pass
    return 1


def compute(params: dict) -> dict:
    raw = (params.get("q", [""])[0] or "").strip()
    raw = raw.removeprefix("https://github.com/").removeprefix("http://github.com/").strip("/")
    if "/" not in raw:
        return {"error": "invalid_repo", "hint": "请传 owner/repo，如 octocat/Hello-World"}
    owner, repo = raw.split("/", 1)
    repo = repo.removesuffix(".git")
    report = {"repo": f"{owner}/{repo}", "generated_at": int(time.time())}

    code, data, headers = gh_get(f"/repos/{owner}/{repo}")
    if code == 404:
        return {"error": "not_found", "repo": report["repo"]}
    if code in (403, 429):
        return {"error": "rate_limited",
                "hint": "GitHub 未认证限流 60 次/小时/IP，请稍后再试",
                "remaining": headers.get("X-RateLimit-Remaining")}
    if code != 200:
        return {"error": "upstream_error", "status": code, "detail": str(data)[:200]}

    lic = (data.get("license") or {}).get("spdx_id")
    license_risk = "unknown" if not lic or lic == "NOASSERTION" else (
        "copyleft" if lic.startswith(("GPL", "AGPL", "LGPL")) else "permissive")

    report["basic"] = {
        "description": data.get("description"),
        "language": data.get("language"),
        "stars": data.get("stargazers_count", 0),
        "forks": data.get("forks_count", 0),
        "open_issues": data.get("open_issues_count", 0),
        "archived": data.get("archived", False),
        "license": lic,
        "created_days_ago": days_since(data.get("created_at")),
        "last_push_days_ago": days_since(data.get("pushed_at")),
    }

    code, langs, _ = gh_get(f"/repos/{owner}/{repo}/languages")
    total = sum(langs.values()) if isinstance(langs, dict) and langs else 0
    report["languages"] = ([{"name": k, "percent": round(v * 100 / total, 1)}
                            for k, v in sorted(langs.items(), key=lambda x: -x[1])] if total else [])

    branch = data.get("default_branch") or "main"
    commits = count_commits(owner, repo, branch)

    code, root, _ = gh_get(f"/repos/{owner}/{repo}/contents/")
    names = [f["name"] for f in root if isinstance(f, dict)] if code == 200 and isinstance(root, list) else []
    has_readme = any(n.lower().startswith("readme") for n in names)
    has_license = any(n.lower().startswith("license") or n.lower() == "copying" for n in names)
    has_tests = any(n.lower() in ("tests", "test") or n.lower().startswith("test_") for n in names)
    has_ci = any(n in names for n in CI_DIRS)
    manifests = [n for n in names if n in MANIFESTS]

    dep_count = None
    if "package.json" in manifests:
        c, body, _ = gh_get(f"/repos/{owner}/{repo}/contents/package.json")
        if c == 200 and isinstance(body, dict):
            try:
                pkg = json.loads(base64.b64decode(body.get("content", "")).decode("utf-8", "replace"))
                dep_count = len(pkg.get("dependencies", {})) + len(pkg.get("devDependencies", {}))
            except Exception:
                pass

    open_issues = data.get("open_issues_count", 0)
    issue_health = "unknown"
    if commits:
        ratio = open_issues / max(commits, 1)
        issue_health = "healthy" if ratio < 5 else ("warning" if ratio < 20 else "backlogged")

    last_push = report["basic"]["last_push_days_ago"] or 999
    scores = {
        "activity": 25 if last_push < 30 else (15 if last_push < 180 else 5),
        "community": min(25, 5 + (2 if report["basic"]["stars"] >= 10 else 0)
                         + (3 if report["basic"]["stars"] >= 100 else 0)
                         + (5 if report["basic"]["stars"] >= 1000 else 0)
                         + (10 if report["basic"]["forks"] >= 10 else 0)),
        "docs": 10 * (int(has_readme) + int(has_license)),
        "engineering": 10 * (int(has_tests) + int(has_ci)),
        "issue_health": {"healthy": 10, "warning": 6, "backlogged": 2}.get(issue_health, 4),
    }
    # 各维度上限之和 = 25+25+20+20+10 = 100，总分天然封顶
    total_score = min(100, sum(scores.values()))
    grade = "A" if total_score >= 80 else ("B" if total_score >= 60 else ("C" if total_score >= 40 else "D"))

    report["deep"] = {
        "total_commits": commits,
        "has_readme": has_readme, "has_license_file": has_license,
        "has_tests": has_tests, "has_ci": has_ci,
        "manifests": manifests, "dependency_count": dep_count,
        "license_risk": license_risk, "issue_health": issue_health,
    }
    report["score"] = {"total": total_score, "grade": grade, "breakdown": scores, "max": 100}
    report["notes"] = [
        "issue_health 为粗略口径（open_issues 含 PR）",
        f"license_risk={license_risk}" + ("，商用包装前注意 GPL 传染性" if license_risk == "copyleft" else ""),
    ]
    return report


