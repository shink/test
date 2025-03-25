import argparse
import os

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import yaml

from github import Auth, Github

from github.Issue import Issue as gh_issue
from github.PaginatedList import PaginatedList as gh_paginated_list
from github.PullRequest import PullRequest as gh_pr
from github.Repository import Repository as gh_repo


SH_ZONE = ZoneInfo("Asia/Shanghai")


@dataclass
class Issue:
    repo: str
    title: str
    labels: list[str]
    related: list[str]


@dataclass
class Employee:
    id: str
    name: str


@dataclass
class Config:
    repo: str
    employees: list[Employee]
    issue: Issue
    body_footer: str

    def __post_init__(self):
        self.employees = [
            Employee(**emp) if isinstance(emp, dict) else emp for emp in self.employees
        ]
        if isinstance(self.issue, dict):
            self.issue = Issue(**self.issue)


def _load_config(path: str) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return Config(**data)


def _get_week_period() -> tuple[datetime, datetime]:
    """
    Returns the start and end of the current week in Shanghai timezone.
    """

    today = datetime.now(tz=SH_ZONE).replace(hour=0, minute=0, second=0, microsecond=0)
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6, hours=23, minutes=59, seconds=59)
    return start_of_week, end_of_week


def _in_period(dt: datetime, start: datetime, end: datetime) -> bool:
    return start <= dt and dt <= end


def _get_pr_stats(
    repo: gh_repo, *, config: Config, start: datetime, end: datetime
) -> str:
    def _is_created_at_period(pr: gh_pr):
        created_at = pr.created_at.replace(tzinfo=SH_ZONE)
        return _in_period(created_at, start, end)

    def _is_merged_at_period(pr: gh_pr):
        if not pr.merged_at:
            return False
        merged_at = pr.merged_at.replace(tzinfo=SH_ZONE)
        return _in_period(merged_at, start, end)

    def _is_merged(pr: gh_pr):
        if pr.merged:
            return True
        if pr.state == "closed":
            labels = [label.name for label in pr.labels]
            return "Merged" in labels
        return False

    all_prs: gh_paginated_list[gh_pr] = repo.get_pulls(
        state="all", sort="created", direction="desc", base="main"
    )

    print(f"Generating PR stats from {start} to {end}")
    prs: list[gh_pr] = []
    for pr in all_prs:
        if _is_created_at_period(pr) or _is_merged_at_period(pr):
            prs.append(pr)

    print(f"Found {len(prs)} PRs in the period")
    report = ""
    for employee in config.employees:
        emp_prs: list[gh_pr] = []
        for pr in prs:
            if pr.user and pr.user.login.lower() == employee.id.lower():
                emp_prs.append(pr)

        open_prs: list[gh_pr] = []
        merged_prs: list[gh_pr] = []
        for pr in emp_prs:
            if pr.state == "open" or pr.state == "draft":
                open_prs.append(pr)
            elif _is_merged(pr):
                merged_prs.append(pr)

        print(
            f"Found PRs for {employee.id}: "
            f"{len(open_prs)} open, {len(merged_prs)} merged"
        )

        report = f"## PRs by @{employee.id}\n"
        if open_prs:
            report += "#### Openning PRs: \n"
            for pr in open_prs:
                report += f"- {pr.html_url}\n"

        if merged_prs:
            report += "#### Merged PRs: \n"
            for pr in merged_prs:
                report += f"- {pr.html_url}\n"

    if report:
        report += f"\n{config.body_footer}\n"
    return report


def _create_issue(repo: gh_repo, *, title: str, body: str, labels: list[str], **kwargs):
    if "dry_run" in kwargs and kwargs["dry_run"]:
        print(
            f"Creating issue: \n"
            f"Title: {title}\n"
            f"Body: {body}\n"
            f"Labels: {labels}\n"
        )
    else:
        repo.create_issue(
            title=title,
            body=body,
            labels=labels,
        )


def _update_issue_body(issue: gh_issue, *, body: str, **kwargs):
    if "dry_run" in kwargs and kwargs["dry_run"]:
        msg = f"Updating issue: {issue.html_url}\n"
        msg += f"Body: \n{body}\n"
        print(msg)
    else:
        issue.edit(body=body)


def _close_issue(issue: gh_issue, **kwargs):
    if "dry_run" in kwargs and kwargs["dry_run"]:
        print(f"Closing issue: {issue.html_url}\n")
    else:
        issue.edit(state="closed")


def _get_last_issue(repo: gh_repo, config: Config):
    issues = repo.get_issues(state="open", labels=config.issue.labels)
    for issue in issues:
        if config.issue.title in issue.title:
            print(f"Found last issue: {issue.html_url}")
            return issue

    print("No last issue found")
    return None


def main():
    # 解析 --path 参数
    parser = argparse.ArgumentParser(description="Generate weekly PR stats report")
    parser.add_argument(
        "--path",
        type=str,
        required=True,
        help="Path to the config YAML file",
    )
    parser.add_argument(
        "--dry-run",
        store=True,
        help="If set, only print the actions without actually doing them",
    )
    args = parser.parse_args()

    # 加载参数
    config = _load_config(args.path)
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required")

    # 授权
    auth = Auth.Token(token=token)
    with Github(auth=auth) as gh:
        repo = gh.get_repo(config.repo)
        issue_repo = gh.get_repo(config.issue.repo)

        # 0. 计算本周起止时间
        start, end = _get_week_period()

        # 1. 查询 PR 统计信息
        report = _get_pr_stats(repo, config, start=start, end=end)
        if not report:
            print("No stats found")
            return

        # 2. 查询上一个 Issue
        last_issue = _get_last_issue(issue_repo, config)

        if last_issue and _in_period(last_issue.created_at, start, end):
            # 3.更新本周 Issue
            _update_issue_body(last_issue, body=report, dry_run=args.dry_run)
        else:
            if last_issue:
                # 3. 关闭上周 Issue
                _close_issue(last_issue, dry_run=args.dry_run)

            # 4. 创建 Issue
            start_str = start.strftime("%m/%d")
            end_str = end.strftime("%m/%d")
            title = f"{config.issue.title} ({start_str} - {end_str})"
            _create_issue(
                issue_repo,
                title=title,
                body=report,
                labels=config.issue.labels,
                dry_run=args.dry_run,
            )


if __name__ == "__main__":
    main()
