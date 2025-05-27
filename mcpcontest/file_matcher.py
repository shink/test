import os

from typing import List

from fastmcp import FastMCP

file_matcher_mcp = FastMCP(name="FileMatcherService")


@file_matcher_mcp.tool()
def file_matcher(dir_path: str, file_type: str = "txt") -> List[str]:
    """
    遍历指定目录下的所有文件，返回匹配指定类型的文件路径列表

    Args:
        dir_path (str): 文件目录路径
        file_type (str, optional): 文件类型后缀名，不带点。默认是 "txt"

    Returns:
        List[str]: 匹配的文件路径列表
    """

    file_paths = []
    for dirpath, _, filenames in os.walk(dir_path):
        for filename in filenames:
            if filename.endswith(f".{file_type}"):
                file_paths.append(os.path.join(dirpath, filename))
    return file_paths


if __name__ == "__main__":
    file_matcher_mcp.run()
