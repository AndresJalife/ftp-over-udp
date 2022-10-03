from lib.tcp_lite import TcpLiteSocket


class DefaultConfiguration:
    def __init__(self):
        config_file = open("src/config.txt", "r")
        lines = config_file.readlines()
        for line in lines:
            split_line = line.split("=")
            if split_line[0] == "port":
                self.port = int(split_line[1])
            elif split_line[0] == "host":
                self.host = split_line[1].rstrip()
            elif split_line[0] == "storage":
                self.storage = split_line[1].rstrip()
            elif split_line[0] == "verbosity":
                self.verbosity = int(split_line[1])
            elif split_line[0] == "send_type":
                send_type = split_line[1].rstrip()
                if send_type == 'gbn':
                    self.send_type = TcpLiteSocket.GO_BACK_N
                else:
                    self.send_type = TcpLiteSocket.STOP_AND_WAIT
        config_file.close()
