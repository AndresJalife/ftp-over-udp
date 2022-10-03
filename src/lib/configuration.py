class DefaultConfiguration:
    def __init__(self):
        config_file = open("src/config.txt", "r")
        lines = config_file.readlines()
        for line in lines:
            split_line = line.split("=")
            if split_line[0] == "port":
                self.port = split_line[1].rstrip()
            elif split_line[0] == "host":
                self.host = int(split_line[1])
            elif split_line[0] == "storage":
                self.storage = split_line[1].rstrip()
            elif split_line[0] == "verbosity":
                self.verbosity = int(split_line[1])

        config_file.close()
