from typing import List

from fastmcp import FastMCP


csv_reader_mcp = FastMCP(name="CsvReaderService")


@csv_reader_mcp.tool()
def csv_reader(csv_path: str, encoding="utf-8") -> List[str]:
    """
    读取 csv 文件内容，返回每行字符串内容的列表

    Args:
        csv_path (str): csv 文件路径
        encoding (str, optional): csv 文件编码。默认是 "utf-8"

    Returns:
        List[str]: csv 文件内容
    """

    with open(csv_path, "r", encoding="utf-8") as f:
        return f.readlines()


if __name__ == "__main__":
    csv_reader_mcp.run()
