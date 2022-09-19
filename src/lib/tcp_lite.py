import socket
import struct
import math
import time
import collections
from threading import Thread


class Packet:
    """TcpLite Protocol packet"""
    HEADER_FORMAT = '??IIIII'

    def __init__(self, sync=False, data=bytes(), sequence_number=0, index_number=0, ack_number=0, total_packets=0, dead=False):
        self.sync = sync
        self.data = data
        self.sequence_number = sequence_number
        self.index_number = index_number
        self.ack_number = ack_number
        self.total_packets = total_packets
        self.dead = dead

    def is_ack(self):
        """Return if the pack is an ACK packet"""
        return self.ack_number != 0

    def __bytes__(self):
        """Convert this packet to a bytearray"""
        return struct.pack(
            Packet.HEADER_FORMAT,
            self.sync,
            self.dead,
            self.sequence_number,
            self.index_number,
            self.ack_number,
            self.total_packets,
            len(self.data)
        ) + self.data

    @staticmethod
    def from_bytes(packet_bytes):
        """Create a new packet object from a serialized set of bytes"""
        header_size = struct.calcsize(Packet.HEADER_FORMAT)
        header = struct.unpack(Packet.HEADER_FORMAT, packet_bytes[:header_size])
        return Packet(
            sync=header[0],
            dead=header[1],
            sequence_number=header[2],
            index_number=header[3],
            ack_number=header[4],
            total_packets=header[5],
            data=packet_bytes[header_size:header_size + header[6]],
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
        self.ack_type = ack_type
        self.verbosity_level = 0
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.settimeout(None)
        self.address_book = collections.defaultdict(collections.deque)
        self.ack_book = collections.defaultdict(collections.deque)
        self.connection_queue = collections.deque()
        self.send_queue = collections.deque()
        self.sending_thread = Thread(target=self._send_loop, daemon=True)
        self.receive_thread = Thread(target=self._receive_loop, daemon=True)
        self.should_die = False
        self.is_ready = False
        self.sending_thread.start()
        self.receive_thread.start()

    def _send_loop(self):
        """Send messages in the background"""
        methods = {
            TcpLiteSocket.STOP_AND_WAIT: self._send_stop_and_wait,
            # Add go-back-n
        }

        while not self.should_die:
            if not self.send_queue:
                continue
            packet_to_send, addr, wait_for_ack = self.send_queue.popleft()
            methods[self.ack_type](packet_to_send, addr, wait_for_ack)

    def _receive_loop(self):
        """Main loop that receives packets in the background"""
        while not self.should_die:
            if not self.is_ready:
                continue
            data, receive_addr = self.socket.recvfrom(TcpLiteSocket.PACKET_SIZE)
            packet = Packet.from_bytes(data)
            self._send_ack(packet, receive_addr)
            self._queue_packet(packet, receive_addr)

    def _get_packet_from_book(self, book, addr, timeout):
        """Gets a packet from an addr"""
        start = time.time()
        while start + timeout > time.time() or not timeout:
            queue = book[addr]
            if not queue:
                continue
            return queue.popleft()
        return None

    def _get_packet_from(self, addr, timeout=0):
        """Gets a packet from an addr"""
        return self._get_packet_from_book(self.address_book, addr, timeout)

    def _get_ack_packet_from(self, addr, timeout=0):
        """Gets an ACK packet from an addr"""
        return self._get_packet_from_book(self.ack_book, addr, timeout)

    def receive_from(self, addr):
        """Receives a piece of data from a set of packets. Blocks the current thread."""
        first = self._get_packet_from(addr)
        curr = 1
        total = first.total_packets
        buffer = [None] * first.total_packets
        buffer[first.index_number] = first.data
        while curr < total:
            packet = self._get_packet_from(addr)
            if buffer[packet.index_number]:
                # Duplicated packet, discard it
                continue
            buffer[packet.index_number] = packet.data
            curr += 1
        return b''.join(buffer)

    def _send_ack(self, packet, addr):
        """Sends an ACK to the currently connected peer"""
        if packet.is_ack():
            # We dont ack ack'ed packets
            return
        response = Packet(ack_number=packet.sequence_number)
        if packet.sync:
            response = Packet(ack_number=1, sync=True)
        self.socket.sendto(bytes(response), addr)

    def _queue_packet(self, packet, addr):
        """Queue a packet in the address book"""
        if packet.is_ack():
            self.ack_book[addr].append(packet)
            return

        if packet.sync:
            self.connection_queue.append((packet, addr))
            self._log(f'Received connection packet from client {addr}')
            return

        if addr not in self.address_book:
            self._log(f'Received packet from unknown client {addr}')
            return

        self.address_book[addr].append(packet)
        self._log(f'Received packet from client {addr}')

    def send_to(self, addr, bytes_to_send):
        """Sends a message using the specified ack algorithm"""

        self._log(f'Sending {len(bytes_to_send)} bytes "{bytes_to_send.decode("ASCII")}"')
        total_packets = int(math.ceil(len(bytes_to_send) / TcpLiteSocket.DATA_PAYLOAD_SIZE))
        for i in range(0, len(bytes_to_send), TcpLiteSocket.DATA_PAYLOAD_SIZE):
            payload = bytes_to_send[i:i + TcpLiteSocket.DATA_PAYLOAD_SIZE]
            curr = i // TcpLiteSocket.DATA_PAYLOAD_SIZE
            packet_to_send = Packet(
                data=payload,
                sequence_number=curr+56,
                index_number=curr,
                total_packets=total_packets
            )
            self._log(f'Queuing packet to send to {addr}')
            self.send_queue.append((packet_to_send, addr, True))

    def _send_stop_and_wait(self, packet_to_send, addr, wait_for_ack):
        """Sends a packet using the stop and wait algorithm"""
        packet_bytes = bytes(packet_to_send)
        self._log(f"Sending packet {packet_to_send.index_number + 1}/{packet_to_send.total_packets} of size {len(packet_bytes)} with payload {len(packet_to_send.data)} to {addr}")

        success = False
        for j in range(TcpLiteSocket.ACK_RETRIES):
            self.socket.sendto(packet_bytes, addr)
            self.is_ready = True
            if not wait_for_ack:
                success = True
                break
            ack_packet = self._get_ack_packet_from(addr, timeout=TcpLiteSocket.ACK_TIMEOUT)

            if not ack_packet:
                continue

            if ack_packet.ack_number == packet_to_send.sequence_number:
                success = True
                break
        if not success:
            self._log('STOP_AND_WAIT: Failed to receive ACK, shutting down.')
            #self._shutdown()
        else:
            self._log(f'Successfully sent packet {packet_to_send.sequence_number}/{packet_to_send.total_packets} and received ACK')

    def _shutdown(self):
        """Shuts down the socket"""
        self.should_die = True
        self.socket.shutdown(socket.SHUT_RDWR)

    def _log(self, *args):
        """Log the args to STDOUT"""
        if self.verbosity_level > 0:
            return print(*args)


class TcpLiteServer(TcpLiteSocket):
    """A server socket that listens for incoming connections"""

    def listen(self):
        """Listens on the specified address for incoming TcpLite connections"""
        self._log(f'Listening for new connections on {self.server_addr}')
        self.socket.bind(self.server_addr)
        self.is_ready = True
        while True:
            if not self.connection_queue:
                continue

            packet, addr = self.connection_queue.popleft()
            self._log(f'Received connection request from {addr}')
            lite_socket = TcpLiteConnection(parent=self, addr=addr)
            self._log(f'Client {addr} successfully connected')

            yield lite_socket

    def shutdown(self):
        """Shutdown the server and signal all clients"""
        for addr in self.address_book.keys():
            self.send_to(addr, bytes(Packet(dead=True)))
        self._shutdown()


class TcpLiteClient(TcpLiteSocket):
    """A client that can connect to server sockets"""

    def send(self, bytes_to_send):
        """Sends a packet to the server connected to"""
        return self.send_to(self.server_addr, bytes_to_send)

    def connect(self):
        """Connect to a TCPLite client in the specified address"""
        self.address_book[self.server_addr] = collections.deque([])
        for i in range(TcpLiteSocket.CONNECT_RETIRES):
            self.send_queue.append((Packet(sync=True), self.server_addr, False))
            packet = self._get_ack_packet_from(self.server_addr, timeout=TcpLiteSocket.ACK_TIMEOUT)

            if not packet:
                continue

            if packet.ack_number == 1 and packet.sync:
                self._log(f"Established connection to '{self.server_addr}'")
                return True

        self._log(f"Failed to connect to '{self.server_addr}'")
        return False

    def receive(self):
        """Blocks the current thread until it received a message from the stream"""
        return self.receive_from(self.server_addr)

    def shutdown(self):
        """Shutdowns the client and signals the server"""
        self.send_to(self.server_addr, bytes(Packet(dead=True)))
        self._shutdown()


class TcpLiteConnection:
    """Facade for a server child socket"""

    def __init__(self, parent, addr):
        self.parent = parent
        self.addr = addr

    def send(self, bytes_to_send):
        """Send a message to the connection"""
        self.parent.send_to(self.addr, bytes_to_send)

    def receive(self):
        """Receive data from the connection"""
        return self.parent.receive_from(self.addr)
