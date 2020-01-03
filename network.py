import pygame
import queue
import socket
import struct
from threading import Thread

multicast_addr = '239.0.0.1'
bind_addr = '0.0.0.0'
port = 10000
membership = socket.inet_aton(multicast_addr) + socket.inet_aton(bind_addr)


class Network:

    def __init__(self, q):
        self.q = q
        self.shutdown_signal = False

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        # Local Testing
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

    def shutdown(self):
        self.shutdown_signal = True

    def start_receiving(self):
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.sock.bind(('0.0.0.0', port))
        print("Listening on port [%d]..." % self.sock.getsockname()[1])
        thread = Thread(target=self.network_receiver)
        thread.start()
        return thread

    def start_sending(self):
        thread = Thread(target=self.network_sender)
        thread.start()
        return thread

    def network_receiver(self):
        while not self.shutdown_signal:
            self.sock.settimeout(1.0)
            try:
                received, address = self.sock.recvfrom(1024)
                print("Received: [%s] from [%s]" % (received, address))
                message_parts = received.decode("utf-8").split('|')
                event = pygame.event.Event(pygame.USEREVENT, dict(team=message_parts[0], action=message_parts[1],
                                                                  row=int(message_parts[2]), col=int(message_parts[3])))
                pygame.event.post(event)
            except socket.timeout:
                pass
            finally:
                self.sock.settimeout(None)

    def network_sender(self):
        while not self.shutdown_signal:
            try:
                outbound_message = self.q.get(timeout=1)
                print("Transmitting [%s] ..." % outbound_message)
                self.sock.sendto(str.encode(outbound_message), (multicast_addr, port))
                self.q.task_done()
            except queue.Empty:
                pass

