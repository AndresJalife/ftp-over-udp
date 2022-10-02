FTP_TYPE_DOWNLOAD = 0
FTP_TYPE_UPLOAD = 1
FTP_TYPE_LIST = 2
NAME_MAX_LENGTH = 20

class FTP_message:
    def __init__(self, type, payload, error):
        self.type = type
        self.payload = payload
        self.error = error

    def encode(self):
        return self.type.encode('ASCII') + self.payload.encode('ASCII') + self.error.encode('ASCII')


class FTP_file_message(FTP_message):
    def __init__(self, file_name, type, payload, error):
        FTP_message.__init__(self, type, payload, error)
        self.file_name = file_name

    def encode(self):
        name = self.file_name
        for i in range(0, NAME_MAX_LENGTH - len(self.file_name)):
            name = name + "0"
        return self.type.encode('utf-8') + name.encode('utf-8') + self.payload
