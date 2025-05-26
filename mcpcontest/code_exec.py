from typing import Tuple

from fastmcp import FastMCP


code_exec_mcp = FastMCP(name="CodeExecService")


@code_exec_mcp.tool(
    name="CodeExec",
    description="计算三维空间中两点之间的欧氏距离，保留指定位小数（默认8位）",
)
def code_exec(
    p1: Tuple[int, int, int],
    p2: Tuple[int, int, int],
    precision: int = 8,
) -> str:
    """
    计算三维空间中两点之间的欧氏距离，保留指定位小数（默认8位）

    Args:
        p1 (Tuple[int, int, int]): 第一个点的坐标，形如 (x1, y1, z1)
        p2 (Tuple[int, int, int]): 第二个点的坐标，形如 (x2, y2, z2)
        precision (int, optional): 保留的小数位数，默认为8

    Returns:
        str: 三维空间中两点之间的欧氏距离，保留指定位小数（默认8位）
    """
    import math

    distance = math.sqrt(
        (p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2 + (p1[2] - p2[2]) ** 2
    )
    distance = round(distance, precision)
    return f"{distance:.{precision}f}"


if __name__ == "__main__":
    code_exec_mcp.run()
