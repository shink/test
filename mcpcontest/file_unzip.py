import os
import zipfile

from fastmcp import FastMCP

file_unzip_mcp = FastMCP(name="FileUnzipService")


@file_unzip_mcp.tool()
def file_unzip(zip_path: str) -> str:
    """
    解压 zip 文件，返回解压后的文件路径

    Args:
        zip_path (str): zip 文件路径

    Returns:
        str: 解压后的文件路径
    """

    # 将 xxx/data.zip 解压到 xxx/extracted 目录下
    extract_to = os.path.join(os.path.dirname(zip_path), "extracted")
    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_to)
    return extract_to


if __name__ == "__main__":
    file_unzip_mcp.run()
