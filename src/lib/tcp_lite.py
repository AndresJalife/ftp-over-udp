import socket

class Packet:

    def __init__(self, sync=False, data=bytes(), sequence_number=0, ack_number=0):
        self.sync = sync
        self.data = data
        self.sequence_number = sequence_number
        self.ack_number = ack_number

    def __bytes__(self):
        arr = bytearray()
        arr.append(bytes(self.sync))
        arr.append(self.data)
        return arr

    @staticmethod
    def from_bytes(bytes):
        return Packet(

        )


class TcpLiteSocket:

    CONNECT_RETIRES = 5
    ACK_RETRIES = 5
    ACK_TIMEOUT = 0.25
    DATA_PACKET_SIZE = 4096 - len(bytes(Packet()))
    STOP_AND_WAIT = 0
    GO_BACK_N = 1

    def __init__(self, addr, ack_type=STOP_AND_WAIT):
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(TcpLiteSocket.ACK_TIMEOUT)
        self.is_connected = False
        self.connected_to = None
        self.ack_type = ack_type

    def connect(self):a
        for i in range(TcpLiteSocket.CONNECT_RETIRES):
            self.send(bytes(Packet(sync=True)))
            recv_bytes, addr = self.receive()

            if not recv_bytes:
                continue

            packet = Packet.from_bytes(recv_bytes)
            if packet.ack_number == 1 and packet.sync:
                self.is_connected = True
                self.connected_to = addr
                print(f"Established connection to '{self.connected_to}'")
                return True

        print(f"Failed to connect to '{self.addr}'")
        return False

    def listen(self):
        self.socket.bind(('', 12000))

    def send(self, bytes):
        if self.ack_type == TcpLiteSocket.STOP_AND_WAIT:
            return self._send_stop_and_wait(bytes)
        else:
            raise not NotImplementedError('Go back N has not been implemented yet.')

    def _send_stop_and_wait(self, bytes_to_send):
        print(f'Sending {len(bytes_to_send)} bytes')
        for i in range(0, len(bytes_to_send), TcpLiteSocket.DATA_PACKET_SIZE):
            packet_to_send = Packet(
                data=bytes_to_send[i:TcpLiteSocket.DATA_PACKET_SIZE],
                sequence_number=i
            )
            print(f"Sending packet {i // TcpLiteSocket.DATA_PACKET_SIZE} of size {TcpLiteSocket.DATA_PACKET_SIZE}")

            for j in range(TcpLiteSocket.ACK_RETRIES):
                self.socket.sendto(bytes(packet_to_send), self.addr)
                recv_bytes, _ = self.receive()
                if recv_bytes and Packet.from_bytes(recv_bytes).ack_number == packet_to_send.sequence_number:
                    break

            print('STOP_AND_WAIT: Failed to receive ACK, shutting down.')
            self.shutdown()



    def receive(self):
        try:
            return self.socket.recvfrom(TcpLiteSocket.DATA_PACKET_SIZE, self.addr)
        except TimeoutError:
            return None, None


    def shutdown(self):
        self.socket.shutdown(socket.SHUT_RDWR)



socket = TcpLiteSocket('127.0.0.1', 123)
socket.connect()


socket.send(x.)
x.split(':')
