import pygame
import queue
import socket
import struct
from config import *
from time import time
from threading import Lock, Thread


class Network:

    def __init__(self, game_number, our_team_id):
        self.our_team_id = our_team_id
        self.our_game_state = STATE_PREPARING
        self.message_counter = 100
        self.messages_to_send = queue.Queue()
        self.unacked_last_attempt = None
        self.unacked_message = None
        self.send_lock = Lock()
        self.shutdown_signal = False
        self.game_number = game_number

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if hasattr(socket, "SO_REUSEPORT"):
            self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        # Local Testing
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    def get_messages_to_send(self):
        return self.messages_to_send

    def shutdown(self):
        self.shutdown_signal = True

    def update_game_state(self, state):
        self.our_game_state = state

    def start(self):
        self.last_beacon_time = time()
        membership = socket.inet_aton(MULTICAST_IP) + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.sock.bind(('0.0.0.0', MULTICAST_PORT + self.game_number))
        print(f"          Listening for multicasts on port [{self.sock.getsockname()[1]}]...")
        thread = Thread(target=self.network_loop)
        thread.start()
        return thread

    def network_loop(self):
        while not self.shutdown_signal:
            self.network_receive()
            self.exhaust_send_queue()

    def network_receive(self):
        self.sock.settimeout(0.5)
        try:
            received, address = self.sock.recvfrom(1024)
            message = received.decode("utf-8")
            message_parts = message.split('|')
            if message.startswith('ACK-') and message_parts[2] == str(self.our_team_id):
                self.process_acknowledgement(message_parts)
            elif not self.is_message_from_myself(message_parts):
                if len(message_parts) > 4:
                    print(f"Received: [ {message} ] from {address}")
                    if self.should_acknowledge(received):
                        self.acknowledge(received)
                    event = pygame.event.Event(pygame.USEREVENT, dict(
                        team_id=int(message_parts[1]), action=message_parts[2],
                        row=int(message_parts[3]), col=int(message_parts[4])))
                    pygame.event.post(event)
        except socket.timeout:
            pass
        finally:
            self.sock.settimeout(None)

    def is_message_from_myself(self, message_parts) -> bool:
        return message_parts[1] == str(self.our_team_id)

    def exhaust_send_queue(self):
        if self.our_game_state == STATE_PREPARING and int(time() - self.last_beacon_time) > 3:
            self.messages_to_send.put(f"{self.our_team_id}|{ACTION_FIND_ME}|{self.our_team_id}|0")
            self.last_beacon_time = time()

        ready_to_send_next_message = False
        with self.send_lock:
            if self.unacked_message is None:
                ready_to_send_next_message = True
            else:
                if time() - self.unacked_last_attempt > 6:
                    print(f"Retrying: [ {self.unacked_message} ]")
                    self.unacked_last_attempt = time()
                    self.sock.sendto(str.encode(self.unacked_message), (MULTICAST_IP, MULTICAST_PORT + self.game_number))

        if ready_to_send_next_message:
            try:
                while True:
                    outbound_message = self.messages_to_send.get(timeout=0.5)
                    self.message_counter += 1
                    message = f"{self.message_counter}|{outbound_message}"

                    with self.send_lock:
                        # No need to acknowledge FIND_ME beacons.
                        if message.find(ACTION_FIND_ME) < 0:
                            self.unacked_message = message
                            self.unacked_last_attempt = time()
                        self.sock.sendto(str.encode(message), (MULTICAST_IP, MULTICAST_PORT + self.game_number))

                    print(f"Sent:     [ {message} ]")
                    self.messages_to_send.task_done()
            except queue.Empty:
                pass

    def should_acknowledge(self, received) -> bool:
        # We don't acknowledge FIND_ME beacons.
        return received.find(ACTION_FIND_ME.encode('utf-8')) < 0

    def acknowledge(self, message):
        message_parts = message.decode("utf-8").split('|')
        message_number = message_parts[0]
        from_team_id = message_parts[1]
        message = f"ACK-{message_number}|{self.our_team_id}|{from_team_id}"
        with self.send_lock:
            self.sock.sendto(str.encode(message), (MULTICAST_IP, MULTICAST_PORT + self.game_number))
        print(f"Ack'd:    [ {message} ]")

    def process_acknowledgement(self, message_parts):
        with self.send_lock:
            unacked_message_number = self.unacked_message[:str(self.unacked_message).index('|')]
            if self.unacked_message \
                    and message_parts[0] == (f"ACK-{unacked_message_number}") \
                    and message_parts[2] == str(self.our_team_id):
                self.unacked_message = None

