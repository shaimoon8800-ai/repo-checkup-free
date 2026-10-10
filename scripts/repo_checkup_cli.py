#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Repo 体检 CLI：python3 repo_checkup_cli.py <owner/repo 或完整 URL> [--json]"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from repo_checkup import compute  # noqa: E402


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if not args:
        print("用法: repo_checkup_cli.py <owner/repo 或 https://github.com/owner/repo>")
        return 2
    report = compute({"q": [args[0]]})
    if "--json" in sys.argv or "-j" in sys.argv:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        if "error" in report:
            print(f"体检失败: {report['error']}  {report.get('repo', '')}")
            print(report.get("hint", ""))
            return 1
        data = report
        b = data.get("basic", {})
        s = data.get("score", {})
        d = data.get("deep", {})
        print(f"仓库: {data.get('repo')}")
        print(f"评分: {s.get('total')}/{s.get('max')}  等级 {s.get('grade')}")
        print(f"分项: {s.get('breakdown')}")
        print(f"star: {b.get('stars')}  fork: {b.get('forks')}  "
              f"license: {b.get('license')}  语言: {b.get('language')}")
        print(f"提交数: {d.get('total_commits')}  测试: {d.get('has_tests')}  "
              f"CI: {d.get('has_ci')}  许可证风险: {d.get('license_risk')}  "
              f"Issue 健康: {d.get('issue_health')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
