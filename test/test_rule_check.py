from mcpcontest.rule_check import rule_check


def test_rule_check():
    hosts_lines = [
        "127.0.0.1 localhost",
        "10.0.0.1 test.example.com",
        "1.1.1.1 cloudflare.com",  # not match
        "192.168.1.1 console.local.com",
        "# Just a comment",
    ]
    no_proxy_lines = [
        "localhost",
        "*.example.com",
        "192.168.1.0/24",
        "cloud.flare.com",
    ]

    res = rule_check(hosts_lines, no_proxy_lines)
    assert res == 1


if __name__ == "__main__":
    test_rule_check()
    print("All tests passed.")
