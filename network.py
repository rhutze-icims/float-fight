import pygame
import queue
import socket
import struct
from time import time
from config import MULTICAST_IP, MULTICAST_PORT, STATE_PREPARING
from threading import Thread


class Network:

    def __init__(self, our_team, first_move_number):
        self.first_move_number = first_move_number
        self.game_state = STATE_PREPARING
        self.messages_to_send = queue.Queue()
        self.shutdown_signal = False
        self.team_name = our_team

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        # Local Testing
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 0)

    def get_messages_to_send(self):
        return self.messages_to_send

    def shutdown(self):
        self.shutdown_signal = True

    def start_receiving(self):
        membership = socket.inet_aton(MULTICAST_IP) + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.sock.bind(('0.0.0.0', MULTICAST_PORT))
        print("Listening on port [%d]..." % self.sock.getsockname()[1])
        thread = Thread(target=self.network_receiver)
        thread.start()
        return thread

    def start_sending(self):
        thread = Thread(target=self.network_sender)
        thread.start()
        return thread

    def update_game_state(self, state):
        self.game_state = state

    def network_receiver(self):
        while not self.shutdown_signal:
            self.sock.settimeout(1.0)
            try:
                received, address = self.sock.recvfrom(1024)
                message_parts = received.decode("utf-8").split('|')
                if len(message_parts) > 3 and not message_parts[0] == self.team_name:
                    print("Received: [%s] from [%s]" % (received, address))
                    event = pygame.event.Event(pygame.USEREVENT, dict(
                        team=message_parts[0], action=message_parts[1],
                        row=int(message_parts[2]), col=int(message_parts[3])))
                    pygame.event.post(event)
            except socket.timeout:
                pass
            finally:
                self.sock.settimeout(None)

    def network_sender(self):
        last_beacon_time = time()

        while not self.shutdown_signal:
            if self.game_state == STATE_PREPARING and int(time() - last_beacon_time) > 3:
                self.messages_to_send.put('%s|FIND_ME|%d|0' % (self.team_name, self.first_move_number))
                last_beacon_time = time()

            try:
                outbound_message = self.messages_to_send.get(timeout=1)
                print("Sending [%s] ..." % outbound_message)
                self.sock.sendto(str.encode(outbound_message), (MULTICAST_IP, MULTICAST_PORT))
                self.messages_to_send.task_done()
            except queue.Empty:
                pass

