import ipaddress
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
    description="根据 hosts 文件和 no-proxy.cnf 文件中的内容，"
    "计算 hosts 中未匹配 no-proxy.cnf 规则的 IP 数量",
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
    wildcard_patterns = []
    cidr_networks = []
    exact_set = set()

    # 解析 no_proxy_lines
    for line in no_proxy_lines:
        line = line.strip()
        # 注释
        if not line or line.startswith("#"):
            continue

        # CIDR 格式
        if "/" in line:
            try:
                cidr_networks.append(ipaddress.ip_network(line, strict=False))
            except ValueError:
                pass  # 忽略非法 CIDR
        # 通配符格式
        elif "*" in line:
            wildcard_patterns.append(wildcard_to_regex(line))
        else:
            exact_set.add(line)

    unmatched_count = 0

    for line in hosts_lines:
        line = line.strip()
        # 注释
        if not line or line.startswith("#"):
            continue

        parts = line.split()
        if not parts:
            continue

        ip = parts[0]
        hostname = parts[1] if len(parts) > 1 else ""

        matched = False

        # 1. 精确匹配
        if ip in exact_set or hostname in exact_set:
            matched = True

        # 2. 通配符匹配
        if not matched:
            matched = any(
                pattern.fullmatch(ip) or pattern.fullmatch(hostname)
                for pattern in wildcard_patterns
            )

        # 3. CIDR 网段匹配（仅限 IP）
        if not matched:
            try:
                ip_obj = ipaddress.ip_address(ip)
                matched = any(ip_obj in net for net in cidr_networks)
            except ValueError:
                pass  # 无效 IP

        if not matched:
            unmatched_count += 1

    return unmatched_count


if __name__ == "__main__":
    rule_check_mcp.run()
