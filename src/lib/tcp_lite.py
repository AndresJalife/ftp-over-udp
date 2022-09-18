import socket
import struct
import math
import time
import collections


class Packet:
    HEADER_FORMAT = '?IIII'

    def __init__(self, sync=False, data=bytes(), sequence_number=0, ack_number=0, total_packets=0):
        self.sync = sync
        self.data = data
        self.sequence_number = sequence_number
        self.ack_number = ack_number
        self.total_packets = total_packets

    def __bytes__(self):
        return struct.pack(
            Packet.HEADER_FORMAT,
            self.sync,
            self.sequence_number,
            self.ack_number,
            self.total_packets,
            len(self.data)
        ) + self.data

    @staticmethod
    def from_bytes(bytes):
        header_size = struct.calcsize(Packet.HEADER_FORMAT)
        header = struct.unpack(Packet.HEADER_FORMAT, bytes[:header_size])
        return Packet(
            sync=header[0],
            sequence_number=header[1],
            ack_number=header[2],
            total_packets=header[3],
            data=bytes[header_size:header_size + header[4]],
        )


class TcpLiteSocket:
    CONNECT_RETIRES = 5
    ACK_RETRIES = 5
    ACK_TIMEOUT = 2
    PACKET_SIZE = 4096
    DATA_PAYLOAD_SIZE = PACKET_SIZE - len(bytes(Packet()))
    STOP_AND_WAIT = 0
    GO_BACK_N = 1

    def __init__(self, addr, ack_type=STOP_AND_WAIT):
        self.server_addr = addr
        self.is_client = False
        self.ack_type = ack_type
        self.socket = self._create_socket()
        self.address_book = {}

    def connect(self):
        for i in range(TcpLiteSocket.CONNECT_RETIRES):
            self.socket.sendto(bytes(Packet(sync=True)), self.server_addr)
            recv_bytes, _ = self._try_receive()

            if not recv_bytes:
                continue

            packet = Packet.from_bytes(recv_bytes)
            if packet.ack_number == 1 and packet.sync:
                self.is_client = True
                self.address_book[self.server_addr] = collections.deque([])
                print(f"Established connection to '{self.server_addr}'")
                return True

        print(f"Failed to connect to '{self.server_addr}'")
        return False

    @staticmethod
    def _create_socket():
        new_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        new_socket.settimeout(TcpLiteSocket.ACK_TIMEOUT)
        return new_socket

    def listen(self):
        print(f'Listening for new connections on {self.server_addr}')
        self.socket.bind(self.server_addr)
        while True:
            packet, addr = self._receive_packet(send_ack=False)

            if not packet.sync:
                self._queue_packet(packet, addr)
                continue
            print(f'Received connection request from {addr}')
            lite_socket = self._add_client(addr)
            print(f'Client {addr} successfully connected')

            yield lite_socket

    def _add_client(self, addr):
        self.address_book[addr] = collections.deque([])
        lite_socket = TcpLiteClient(parent=self, addr=addr)
        self._send_ack(ack_number=1, addr=addr, sync=True)
        return lite_socket

    def _queue_packet(self, packet, addr):
        if addr not in self.address_book:
            print(f'Received packet from unconnected client {addr}')
            return

        self.address_book[addr].append(packet)
        print(f'Received packet from client {addr}')

    def send(self, bytes_to_send):
        return self._send(self.server_addr, bytes_to_send)

    def send_to(self, addr, bytes_to_send):
        """Sends a message using the specified ack algorithm"""
        if self.ack_type == TcpLiteSocket.STOP_AND_WAIT:
            return self._send_stop_and_wait(addr, bytes_to_send)
        else:
            raise not NotImplementedError('Go back N has not been implemented yet.')

    def _send_stop_and_wait(self, addr, bytes_to_send):
        print(f'Sending {len(bytes_to_send)} bytes "{bytes_to_send.decode("ASCII")}"')
        total_packets = int(math.ceil(len(bytes_to_send) / TcpLiteSocket.DATA_PAYLOAD_SIZE))
        for i in range(0, len(bytes_to_send), TcpLiteSocket.DATA_PAYLOAD_SIZE):
            payload = bytes_to_send[i:i + TcpLiteSocket.DATA_PAYLOAD_SIZE]
            curr = i // TcpLiteSocket.DATA_PAYLOAD_SIZE
            packet_to_send = Packet(
                data=payload,
                sequence_number=curr,
                total_packets=total_packets
            )
            packet_bytes = bytes(packet_to_send)
            print(f"Sending packet {curr + 1}/{total_packets} of size {len(packet_bytes)} with payload {len(payload)}")

            success = False
            for j in range(TcpLiteSocket.ACK_RETRIES):
                self.socket.sendto(packet_bytes, addr)
                ack_packet = self._receive_packet_from(addr, timeout=TcpLiteSocket.ACK_TIMEOUT)
                if not ack_packet:
                    continue

                if ack_packet.ack_number == packet_to_send.sequence_number:
                    success = True
                    break
            if not success:
                print('STOP_AND_WAIT: Failed to receive ACK, shutting down.')
                self.shutdown()
            else:
                print(f'Successfully sent packet {curr + 1}/{total_packets}')

    def _try_receive(self):
        """Try to receive data from the socket"""
        try:
            return self.socket.recvfrom(TcpLiteSocket.PACKET_SIZE)
        except socket.timeout:
            return None, None

    def _send_ack(self, ack_number, addr, sync=False):
        """Sends an ACK to the currently connected peer"""
        self.socket.sendto(bytes(Packet(ack_number=ack_number, sync=sync)), addr)

    def _receive_packet(self, send_ack=True):
        """Receive a packet from the socket and return an ACK"""
        data, addr = self._try_receive()
        while (data, addr) == (None, None):
            data, addr = self._try_receive()
        packet = Packet.from_bytes(data)
        if send_ack:
            self._send_ack(packet.sequence_number, addr)
        return packet, addr

    def _receive_and_queue_packet(self):
        start = time.time()
        while not queue and (not timeout or start + timeout < time.time()):
            packet, addr = self._receive_packet()
            self._queue_packet(packet, addr)

    def _receive_packet_from(self, addr, timeout=0):
        if addr not in self.address_book:
            print('Address not in address book')
            return None

        queue = self.address_book[addr]
        self._receive_and_queue_packet(timeout)

        if queue:
            return queue.popleft()
        return None

    def receive_from(self, addr):
        first = self._receive_packet_from(addr)
        curr = 1
        total = first.total_packets
        buffer = [None] * first.total_packets
        buffer[first.sequence_number] = first.data
        while curr < total:
            packet = self._receive_packet_from(addr)
            if buffer[packet.sequence_number]:
                # Duplicated packet, discard it
                continue
            buffer[packet.sequence_number] = packet.data
            curr += 1
        return b''.join(buffer)

    def receive(self):
        """Blocks the current thread until it received a message from the stream"""
        return self.receive_from(self.server_addr)

    def shutdown(self):
        self.socket.shutdown(socket.SHUT_RDWR)


class TcpLiteClient:

    def __init__(self, parent, addr):
        self.parent = parent
        self.addr = addr

    def send(self, bytes_to_send):
        self.parent.send_to(self.addr, bytes_to_send)

    def receive(self):
        return self.parent.receive_from(self.addr)
