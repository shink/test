import argparse
import os

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TYPE_CHECKING

import yaml

from github import Auth, Github

# if TYPE_CHECKING:
from github.Issue import Issue as gh_issue
from github.PaginatedList import PaginatedList as gh_paginated_list
from github.PullRequest import PullRequest as gh_pr
from github.Repository import Repository as gh_repo


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


def _load_config(path: str) -> Config:
    with open(path, "r") as f:
        data = yaml.safe_load(f)
        return Config(**data)


def _get_week_period() -> tuple[datetime, datetime]:
    today = datetime.now()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    return start_of_week, end_of_week


def _get_pr_stats(
    repo: gh_repo, *, employees: list[Employee], start: datetime, end: datetime
) -> str:
    all_prs: gh_paginated_list[gh_pr] = repo.get_pulls(
        state="all", sort="created", direction="desc"
    )

    report = ""
    for employee in employees:
        user_prs: list[gh_pr] = []
        for pr in all_prs:
            if (
                pr.user
                and pr.user.login.lower() == employee.id.lower()
                and pr.created_at >= start
                and pr.created_at <= end
            ):
                user_prs.append(pr)

        def _is_merged(pr: gh_pr):
            if pr.merged:
                return True
            if pr.state == "closed":
                labels = [label.name for label in pr.labels]
                return "Merged" in labels
            return False

        open_prs: list[gh_pr] = []
        merged_prs: list[gh_pr] = []
        for pr in user_prs:
            if pr.state == "open":
                open_prs.append(pr)
            elif _is_merged(pr):
                merged_prs.append(pr)

        report = f"## PRs by @{employee.id}\n"
        if open_prs:
            report += "#### Openning PRs: \n"
            for pr in open_prs:
                report += f"- {pr.html_url}\n"

        if merged_prs:
            report += "#### Merged PRs: \n"
            for pr in merged_prs:
                report += f"- {pr.html_url}\n"

    return report


def _create_issue(repo: gh_repo, *, title: str, body: str, labels: list[str]):
    repo.create_issue(
        title=title,
        body=body,
        labels=labels,
    )


def _update_issue_body(issue: gh_issue, *, body: str):
    issue.edit(body=body)


def _close_issue(issue: gh_issue):
    issue.edit(state="closed")


def _get_last_issue(repo: gh_repo, config: Config):
    issues = repo.get_issues(state="open", labels=config.issue.labels)
    if not issues:
        return None
    for issue in issues:
        if config.issue.title in issue.title:
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
    args = parser.parse_args()

    # 授权
    config = _load_config(args.path)
    token = os.getenv("GITHUB_TOKEN")
    if not token:
        raise ValueError("GITHUB_TOKEN is required")
    auth = Auth.Token(token=token)
    gh = Github(auth=auth)
    repo = gh.get_repo(config.repo)
    issue_repo = gh.get_repo(config.issue.repo)

    # 0. 计算本周起止时间
    start, end = _get_week_period()

    # 1. 查询 PR 统计信息
    report = _get_pr_stats(repo, employees=config.employees, start=start, end=end)

    # 2. 查询上周的 Issue
    last_issue = _get_last_issue(issue_repo, config)

    if last_issue:
        # 3. 更新 Issue
        _update_issue_body(last_issue, body=report)
        # 4. 关闭上周 Issue
        _close_issue(last_issue)
    else:
        # 3. 创建 Issue
        start_str = start.strftime("%m-%d")
        end_str = end.strftime("%m-%d")
        title = f"{config.issue.title} ({start_str} - {end_str})"
        _create_issue(issue_repo, title=title, body=report, labels=config.issue.labels)


if __name__ == "__main__":
    main()
