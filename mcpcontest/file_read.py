from typing import List

from fastmcp import FastMCP


file_read = FastMCP(name="FileReadService")


@file_read.tool(
    name="FileRead",
    description="读取文件内容，返回按行分割的列表",
)
def rule_check(file_path: str) -> List[str]:
    """
    读取文件内容，返回按行分割的列表

    Args:
        file_path (str): 文件路径

    Returns:
        List[str]: 文件内容按行分割的列表
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
        return lines


if __name__ == "__main__":
    file_read.run()
