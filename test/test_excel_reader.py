import os

from mcpcontest.excel_reader import excel_reader


def test_excel_reader():
    file_path = os.path.join(os.path.dirname(__file__), "test_data")
    res = excel_reader(file_path)
    assert res == 1


if __name__ == "__main__":
    test_excel_reader()
    print("All tests passed.")
