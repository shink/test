from fastmcp import FastMCP


excel_reader_mcp = FastMCP(name="ExcelReaderService")


@excel_reader_mcp.tool(
    name="ExcelReader",
    description="读取 Excel 文件，计算成绩为优（各科成绩均大于阈值）的学生人数",
)
def excel_reader(
    file_path: str,
    excellent_threshold: int = 80,
) -> int:
    """
    读取 Excel 文件，计算成绩为优（各科成绩均大于阈值）的学生人数。Excel 文件内容实例如下：

    姓名  语文  数学  英语
    Tom  55  75  73
    张三  97  86  89

    Args:
        file_path (str): Excel 文件路径
        excellent_threshold (int): 成绩为优的阈值，默认为 80

    Returns:
        int: 成绩为优的学生人数
    """
    import pandas as pd

    df = pd.read_excel(file_path)

    # 第一列是姓名，其他列是各科成绩
    score_cols = df.columns[1:]
    is_excellent = (df[score_cols] > excellent_threshold).all(axis=1)
    excellent_count = is_excellent.sum()
    return excellent_count


if __name__ == "__main__":
    excel_reader_mcp.run()
