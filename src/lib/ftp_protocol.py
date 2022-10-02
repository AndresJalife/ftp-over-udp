import struct

class FTP_file_message():
    HEADER_FORMAT = 'I?II'
    FTP_TYPE_DOWNLOAD = 0
    FTP_TYPE_UPLOAD = 1
    FTP_TYPE_LIST = 2

    def __init__(self, file_name, type, payload, error):
        self.file_name = file_name
        self.type = type
        self.payload = payload
        self.error = error


    def encode(self):
        # name = self.file_name
        # for i in range(0, NAME_MAX_LENGTH - len(self.file_name)):
        #     name = name + "0"
        # return self.type.encode('utf-8') + name.encode('utf-8') + self.payload
        """Convert this packet to a bytearray"""

        return struct.pack(
            self.HEADER_FORMAT,
            self.type,
            self.error,
            len(self.file_name),
            len(self.payload)
        ) + self.file_name.encode("ASCII") + self.payload

    @staticmethod
    def decode(bytes):
        """Create a new packet object from a serialized set of bytes"""
        header_size = struct.calcsize(FTP_file_message.HEADER_FORMAT)
        header = struct.unpack(FTP_file_message.HEADER_FORMAT, bytes[:header_size])
        return FTP_file_message(
            type=header[0],
            error=header[1],
            file_name=bytes[header_size:header_size + header[2]].decode("ASCII"),
            payload= bytes[header_size + header[2]:header_size + header[2] + header[3]]
        )

    # def decode(self, bytes):


        # name = ""
        # for i in range(1, NAME_MAX_LENGTH + 1):
        #     name = name + chr(bytes[i])
        # for i in range(len(name) - 1, -1, -1):
        #     if name[i] != "0":
        #         break
        #     name = name[:len(name) - 1]

        # self.type = FTP_TYPE_UPLOAD
        # self.file_name = name
        # self.payload = bytes[NAME_MAX_LENGTH + 1:]