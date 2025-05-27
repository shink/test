from typing import List

from fastmcp import FastMCP


value_count_mcp = FastMCP(name="ValueCountService")


@value_count_mcp.tool()
def value_count(data: List[str]) -> str:
    """
    输入 csv 文件内容，为每行字符串内容的列表

    Args:
        data (List[str]): csv 文件内容

    Returns:
        str: 统计结果，正常温度的平均值，异常值占整体数量的比例
    """

    header = data[0].strip().split(",")
    total = len(data) - 1

    # TODO
    temp_idx = 1

    abnormal_count = 0
    normal_count = 0
    total_temp = 0.0
    for line in data[1:]:
        values = line.strip().split(",")
        temp = float(values[temp_idx])
        if temp < -200 or temp >= 80:
            abnormal_count += 1
        else:
            normal_count += 1
            total_temp += temp

    avg_temp = total_temp / normal_count if normal_count > 0 else 0.0
    abnormal_ratio = abnormal_count / total if total > 0 else 0.0

    return f"{avg_temp},{abnormal_ratio}"


if __name__ == "__main__":
    value_count_mcp.run()
