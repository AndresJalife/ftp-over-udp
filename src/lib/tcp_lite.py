import socket
import struct


class Packet:
    STRUCT_FORMAT = '?IIs'

    def __init__(self, sync=False, data=bytes(), sequence_number=0, ack_number=0):
        self.sync = sync
        self.data = data
        self.sequence_number = sequence_number
        self.ack_number = ack_number

    def __bytes__(self):
        return struct.pack(Packet.STRUCT_FORMAT, self.sync, self.sequence_number, self.ack_number, self.data)

    @staticmethod
    def from_bytes(bytes):
        values = struct.unpack(Packet.STRUCT_FORMAT, bytes)
        return Packet(
            sync=values[0],
            sequence_number=values[1],
            ack_number=values[2],
            data=values[3],
        )


class TcpLiteSocket:

    CONNECT_RETIRES = 5
    ACK_RETRIES = 5
    ACK_TIMEOUT = 2
    DATA_PACKET_SIZE = 4096 - len(bytes(Packet()))
    STOP_AND_WAIT = 0
    GO_BACK_N = 1

    def __init__(self, addr, ack_type=STOP_AND_WAIT):
        self.addr = addr
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(TcpLiteSocket.ACK_TIMEOUT)
        self.is_connected = False
        self.ack_type = ack_type

    def connect(self):
        for i in range(TcpLiteSocket.CONNECT_RETIRES):
            self.socket.sendto(bytes(Packet(sync=True)), self.addr)
            recv_bytes, _ = self.try_receive()

            if not recv_bytes:
                continue

            packet = Packet.from_bytes(recv_bytes)
            if packet.ack_number == 1 and packet.sync:
                self.is_connected = True
                print(f"Established connection to '{self.addr}'")
                return True

        print(f"Failed to connect to '{self.addr}'")
        return False

    def listen(self):
        print(f'Listening for new connections on {self.addr}')
        self.socket.bind(self.addr)
        while True:
            recv_bytes, addr = self.try_receive()

            if not recv_bytes:
                continue

            print(f'Received connection request from {addr}')
            socket = TcpLiteSocket(addr=addr, ack_type=self.ack_type)
            socket.is_connected = True
            yield socket

    def send(self, bytes_to_send):
        if self.ack_type == TcpLiteSocket.STOP_AND_WAIT:
            return self._send_stop_and_wait(bytes_to_send)
        else:
            raise not NotImplementedError('Go back N has not been implemented yet.')

    def _send_stop_and_wait(self, bytes_to_send):
        print(f'Sending {len(bytes_to_send)} bytes')
        for i in range(0, len(bytes_to_send), TcpLiteSocket.DATA_PACKET_SIZE):
            packet_to_send = Packet(
                data=bytes_to_send[i:i+TcpLiteSocket.DATA_PACKET_SIZE],
                sequence_number=i
            )
            packet_bytes = bytes(packet_to_send)
            curr = i // TcpLiteSocket.DATA_PACKET_SIZE
            total = (len(bytes_to_send) // TcpLiteSocket.DATA_PACKET_SIZE) + 1
            print(f"Sending packet {curr}/{total} of size {len(packet_bytes)}")

            for j in range(TcpLiteSocket.ACK_RETRIES):
                self.socket.sendto(packet_bytes, self.addr)
                recv_bytes, _ = self.try_receive()
                print(recv_bytes)
                if recv_bytes and Packet.from_bytes(recv_bytes).ack_number == packet_to_send.sequence_number:
                    break

            print('STOP_AND_WAIT: Failed to receive ACK, shutting down.')
            self.shutdown()



    def try_receive(self):
        try:
            return self.socket.recvfrom(TcpLiteSocket.DATA_PACKET_SIZE)
        except socket.timeout:
            return None, None


    def shutdown(self):
        self.socket.shutdown(socket.SHUT_RDWR)

