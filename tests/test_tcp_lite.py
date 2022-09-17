from src.lib.tcp_lite import TcpLiteSocket


def test_connect():
    server = TcpLiteSocket(('127.0.0.1', 10563))
