import pygame
import queue
import socket
import struct
from time import time
from config import ACTION_FIND_ME, MULTICAST_IP, MULTICAST_PORT, STATE_PREPARING
from threading import Lock, Thread


class Network:

    def __init__(self, our_team, first_move_number):
        self.first_move_number = first_move_number
        self.game_state = STATE_PREPARING
        self.message_counter = 100
        self.messages_to_send = queue.Queue()
        self.unacked_last_attempt = None
        self.unacked_message = None
        self.send_lock = Lock()
        self.shutdown_signal = False
        self.team_name = our_team

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, struct.pack('b', 1))

        # Local Testing
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_LOOP, 1)

    def get_messages_to_send(self):
        return self.messages_to_send

    def shutdown(self):
        self.shutdown_signal = True

    def update_game_state(self, state):
        self.game_state = state

    def start(self):
        self.last_beacon_time = time()
        membership = socket.inet_aton(MULTICAST_IP) + socket.inet_aton('0.0.0.0')
        self.sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, membership)
        self.sock.bind(('0.0.0.0', MULTICAST_PORT))
        print(f"Listening on port [{self.sock.getsockname()[1]}]...")
        thread = Thread(target=self.network_loop)
        thread.start()
        return thread

    def network_loop(self):
        while not self.shutdown_signal:
            self.network_receive()
            self.exhaust_send_queue()

    def network_receive(self):
        self.sock.settimeout(1.5)
        try:
            received, address = self.sock.recvfrom(1024)
            message_parts = received.decode("utf-8").split('|')
            if received.startswith(b'ACK-') and message_parts[2] == self.team_name:
                self.process_acknowledgement(message_parts)
            elif not message_parts[1] == self.team_name:
                if len(message_parts) > 4:
                    print("Received: [%s] from [%s]" % (received, address))

                    if received.find(ACTION_FIND_ME.encode('utf-8')) < 0:
                        self.acknowledge(received)

                    event = pygame.event.Event(pygame.USEREVENT, dict(
                        team=message_parts[1], action=message_parts[2],
                        row=int(message_parts[3]), col=int(message_parts[4])))
                    pygame.event.post(event)
        except socket.timeout:
            pass
        finally:
            self.sock.settimeout(None)

    def exhaust_send_queue(self):
        if self.game_state == STATE_PREPARING and int(time() - self.last_beacon_time) > 3:
            self.messages_to_send.put('%s|%s|%d|0' % (self.team_name, ACTION_FIND_ME, self.first_move_number))
            self.last_beacon_time = time()

        ready_to_send_next_message = False
        with self.send_lock:
            if self.unacked_message is None:
                ready_to_send_next_message = True
            else:
                if time() - self.unacked_last_attempt > 6:
                    print('Retrying: %s' % self.unacked_message)
                    self.unacked_last_attempt = time()
                    self.sock.sendto(str.encode(self.unacked_message), (MULTICAST_IP, MULTICAST_PORT))

        if ready_to_send_next_message:
            try:
                while True:
                    outbound_message = self.messages_to_send.get(timeout=0.5)
                    self.message_counter += 1
                    message = "%d|%s" % (self.message_counter, outbound_message)

                    with self.send_lock:
                        if message.find(ACTION_FIND_ME) < 0:
                            # No need to acknowledge presence beacons.
                            self.unacked_message = message
                            self.unacked_last_attempt = time()
                        self.sock.sendto(str.encode(message), (MULTICAST_IP, MULTICAST_PORT))

                    print("Sent: [%s]" % message)
                    self.messages_to_send.task_done()
            except queue.Empty:
                pass

    def acknowledge(self, message):
        message_parts = message.decode("utf-8").split('|')
        message_number = message_parts[0]
        from_team = message_parts[1]
        message = "ACK-%s|%s|%s" % (message_number, self.team_name, from_team)
        with self.send_lock:
            self.sock.sendto(str.encode(message), (MULTICAST_IP, MULTICAST_PORT))
        print("Acknowledged: [%s]" % message)

    def process_acknowledgement(self, message_parts):
        with self.send_lock:
            unacked_message_number = self.unacked_message[:str(self.unacked_message).index('|')]
            if self.unacked_message \
                    and message_parts[0] == ('ACK-%s' % unacked_message_number) \
                    and message_parts[2] == self.team_name:
                print('Received acknowledgement from %s for message #%s.' % (message_parts[1], unacked_message_number))
                self.unacked_message = None

