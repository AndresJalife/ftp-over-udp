FTP_TYPE_UPLOAD = 0
FTP_TYPE_DOWNLOAD = 1
FTP_TYPE_LIST = 2

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
