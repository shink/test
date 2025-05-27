import ipaddress

from typing import List

from fastmcp import FastMCP

ip_check_mcp = FastMCP(name="IpCheckService")


def is_valid_ip(ip_str):
    try:
        ipaddress.ip_address(ip_str)
        return True
    except ValueError:
        return False


@ip_check_mcp.tool()
def ip_check(files: List[str]) -> int:
    """
    读取指定的文件列表，检查每行是否是有效的 IP 地址

    Args:
        files (List[str]): 文件路径列表

    Returns:
        int: 无效 IP 地址的数量
    """

    invalid_count = 0
    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line == "":
                    continue
                if not is_valid_ip(line):
                    invalid_count += 1
    return invalid_count


if __name__ == "__main__":
    ip_check_mcp.run()
