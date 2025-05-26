import email
import re
from email.header import decode_header
from email.utils import parsedate_to_datetime

from fastmcp import FastMCP

mail_parser_mcp = FastMCP(name="MailParserService")


def parse_eml(eml_path: str):
    """
    eml文件解析
    :params eml_fp: eml文件路径
    :params attr_dir: 附件保存目录
    """
    with open(eml_path, "r") as file:
        eml_content = file.read()

    msg = email.message_from_string(eml_content)

    # 邮件主题
    subject_bytes, subject_encode = decode_header(msg["Subject"])[0]
    if subject_encode:
        subject = subject_bytes.decode(subject_encode)
    else:
        subject = subject_bytes
    print("主题：", subject)

    # 邮件发件人
    from_ip = re.search("<(.*)>", msg["from"]).group(1)
    print("发件人邮箱：", from_ip)

    from_name = decode_header(msg["from"].split("<")[0].strip())
    if from_name:
        if from_name[0] and from_name[0][1]:
            from_n = from_name[0][0].decode(from_name[0][1])
        else:
            from_n = from_name[0][0]
    print("发件人名称：", from_n)

    # 邮件时间
    received_date = parsedate_to_datetime(msg["date"])
    print("接收时间：", received_date)

    # 邮件正文及附件
    for par in msg.walk():
        if not par.is_multipart():  # 判断是否为multipart，里面的数据不需要
            name = par.get_param("name")  # 获取附件的文件名
            if name:
                # 附件
                fname = decode_header(name)[0]
                if fname[1]:
                    attr_name = fname[0].decode(fname[1])
                else:
                    attr_name = fname[0]
                print("附件名:", attr_name)
            else:
                # 正文
                text_char = par.get_content_charset()
                if "text/plain" in par["content-type"]:  # 文本正文
                    body = par.get_payload(decode=True).decode(text_char)
                    print("邮件正文：", body)
                else:  # html格式正文
                    html_body = par.get_payload(decode=True).decode(text_char)
                    print("HTML正文：", html_body)


@mail_parser_mcp.tool(
    name="MailParser",
    description="读取 eml 文件",
)
def mail_parser(eml_path: str) -> str:
    """

    Args:
        hosts_lines (List[str]): hosts 文件内容
        no_proxy_lines (List[str]): no-proxy.cnf 文件内容

    Returns:
        int: hosts 中未匹配 no-proxy.cnf 规则的 IP 数量
    """
    pass


if __name__ == "__main__":
    mail_parser_mcp.run()
