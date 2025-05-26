import re
from typing import List

from fastmcp import FastMCP


rule_check_mcp = FastMCP(name="RuleCheckService")


def wildcard_to_regex(pattern: str) -> re.Pattern:
    # 将通配符 * 转换为正则表达式 .*，同时转义其他特殊字符
    pattern = re.escape(pattern)
    pattern = pattern.replace(r"\*", ".*")
    return re.compile(f"^{pattern}$")


@rule_check_mcp.tool(
    name="RuleCheck",
    description="读取 Excel 文件，计算成绩为优（各科成绩均大于阈值）的学生人数",
)
def rule_check(
    hosts_lines: List[str],
    no_proxy_lines: List[str],
) -> int:
    """
    根据 hosts 文件和 no-proxy.cnf 文件中的内容，计算 hosts 中未匹配 no-proxy.cnf 规则的 IP 数量。

    hosts 内容示例如下，'#'表示注释：
    127.0.0.1 localhost
    10.0.0.1 test.example.com
    # Just a comment

    no-proxy.cnf 内容示例如下，'*'表示通配符：
    localhost
    *.example.com
    10.0.0.*
    192.168.1.1

    Args:
        hosts_lines (List[str]): hosts 文件内容
        no_proxy_lines (List[str]): no-proxy.cnf 文件内容

    Returns:
        int: hosts 中未匹配 no-proxy.cnf 规则的 IP 数量
    """
    # 编译 no-proxy.cnf 中的通配符规则为正则表达式
    patterns = [
        wildcard_to_regex(line.strip())
        for line in no_proxy_lines
        if line.strip() and not line.strip().startswith("#")
    ]

    unmatched_count = 0

    for line in hosts_lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if not parts:
            continue

        ip = parts[0]
        hostname = parts[1]

        # 检查是否匹配任意 no-proxy 规则
        matched = any(p.fullmatch(ip) or p.fullmatch(hostname) for p in patterns)

        if not matched:
            unmatched_count += 1

    return unmatched_count


if __name__ == "__main__":
    rule_check_mcp.run()
