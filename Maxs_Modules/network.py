# - - - - - - - Imports - - - - - - -#
import json
import threading
import types

from Maxs_Modules.setup import UserData
from Maxs_Modules.debug import debug_message, error

# Get the setup data
setup = UserData()
setup.get_packages(["requests"])

import requests
import socket
import selectors


# - - - - - - - Classes - - - - - - - -#

class QuizMessage:
    """
    A class to represent a message sent between the client and server
    """

    def __init__(self, message: str, sender: str, recipient: str, message_type: str):
        """
        @param message: The message
        @param sender: The sender of the message
        @param recipient: The recipient of the message
        @param message_type: The type of the message
        """
        self.message = message
        self.sender = sender
        self.recipient = recipient
        self.message_type = message_type

    def __str__(self):
        return f"Message: {self.message}, Sender: {self.sender}, Recipient: {self.recipient}, Type: {self.message_type}"

    def to_bytes(self):
        obj = {
            "message": self.message,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type
        }
        debug_message(f"Encoding message: {obj}", "Network")
        return json.dumps(obj, ensure_ascii=False).encode("utf-8")

    def from_bytes(self, data: bytes):
        decoded = data.decode("utf-8")
        debug_message(f"Decoded message: {decoded}", "Network")

        obj = json.loads(decoded)
        self.message = obj.get("message")
        self.sender = obj.get("sender")
        self.recipient = obj.get("recipient")
        self.message_type = obj.get("message_type")


class QuizServer:
    """
    A class to represent a server for the quiz game
    """

    def __init__(self, host: str, port: int):
        """
        @param host: The host to listen on
        @param port: The port to listen on
        """
        self.host = host
        self.port = port

        self.selector = selectors.DefaultSelector()
        self.clients = []

        self.server = setup_tcp_server(self.port)

        self.selector.register(self.server, selectors.EVENT_READ, data=None)

    def run(self):
        """
        Run the server
        """
        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_connection(key.fileobj)
                else:
                    self.service_connection(key, mask)

    def accept_connection(self, sock):
        """
        Accept a connection from a client

        @param sock: The socket to accept the connection from
        """
        # Accept the connection
        connection, address = sock.accept()

        # Print the address
        print(f"Accepted connection from {address}")

        # Dont block the process as we want to be able to accept multiple connections
        connection.setblocking(False)

        # Create the data object
        data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")

        # Create the events. They are now read and write so set those bits
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        # Register the connection with the selector
        self.selector.register(connection, events, data=data)

    def close_connection(self, sock):
        """
        Close a connection from a client

        @param sock: The socket to close the connection from
        """

        # Unregister the socket from the selector
        self.selector.unregister(sock)

        # Close the socket
        sock.close()

    def service_connection(self, key, mask):
        """
        Service a connection from a client

        @param key: The key to the client
        @param mask: The mask to the client
        """
        sock = key.fileobj
        data = key.data

        # If the socket has its read bit set
        if mask & selectors.EVENT_READ:

            # Get the data
            recv_data = sock.recv(4096)

            # If there is no data then the connection has been closed
            if recv_data:
                self.handle_data_received(sock, data, recv_data)

            else:
                # Print the address
                print(f"Closing connection on {data.addr}")

                # Close the connection
                self.close_connection(sock)

        # If the socket has its write bit set
        if mask & selectors.EVENT_WRITE:

            # If there is data to send
            if data.outb:
                self.handle_data_send(sock, data, data.outb)

    def handle_data_received(self, sock, key_data, recv_data: bytes):
        """
        Handle data received from a client

        @param sock:  T
        @param key_data: The data from the key
        @param recv_data: The data received
        """

    def handle_data_send(self, sock, key_data, send_data: bytes):
        """
        Handle data sent to a client

        @param send_data: The data sent
        """


class QuizClient:
    """
    A class to represent a client for the quiz game
    """

    message_queue = []

    def __init__(self, host: str, port: int):
        """
        @param host: The host ip to connect to
        @param port: The port to listen on
        """
        self.host = host
        self.port = port

        self.selector = selectors.DefaultSelector()

        self.client = connect_to_server(self.host, self.port)

        self.selector.register(self.client, selectors.EVENT_READ, data=None)

    def run(self):
        while True:

            if len(self.message_queue) > 0:
                self.send_message(self.client, self.message_queue[0][0], self.message_queue[0][1])
                self.message_queue.pop(0)

            events = self.selector.select(timeout=1)

            for key, mask in events:
                sock = key.fileobj
                data = key.data

                # Check if there is a message to send
                print(self.message_queue)

                # If the socket has its read bit set
                if mask & selectors.EVENT_READ:

                    # Get the data
                    recv_data = sock.recv(4096)

                    # If there is no data then the connection has been closed
                    if recv_data:
                        self.handle_response(sock, data, recv_data)

                # If the socket has its write bit set
                if mask & selectors.EVENT_WRITE:

                    # If there is data to send
                    if data.outb:
                        self.handle_request(sock, data, data.outb)

    def handle_response(self, sock, key_data, recv_data: bytes):
        pass

    def handle_request(self, sock, key_data, send_data: bytes):
        pass

    def send_message(self, sock,  message: str, message_type: str):
        """
        Send a message to the server

        @param message: The message to send
        """
        message = QuizMessage(message, get_ip(), self.host, message_type)
        debug_message(f"Sending {message}", "network_client")
        sock.sendall(message.to_bytes())

# - - - - - - - Functions - - - - - - -#


def api_get_questions(amount: int, category: int, difficulty: str, type: str) -> list:
    """
    Gets questions from the API at https://opentdb.com/api.php and returns them as a list of dictionaries

    @param amount: How many questions to get (Max 50)
    @param category: The category of the questions (index, offset by 9)
    @param difficulty: The difficulty of the questions
    @param type: The type of the questions
    @return: A list of dictionaries containing the questions
    """
    redo = True
    api_fix = 0

    user_data = UserData()

    while redo:

        # Create the URL
        url = f"https://opentdb.com/api.php?amount={amount}"

        # Ignore the options if they are "Any" (or none because 'convert_question_settings_to_api' already does this)
        # since the API gives any by default

        if type is not None and api_fix < 1:
            url += f"&type={type}"

        if difficulty != "Any" and api_fix < 2:
            url += f"&difficulty={difficulty.lower()}"

        if category is not None and api_fix < 3:
            url += f"&category={category}"

        debug_message(url, "API")

        # Get the questions from the API
        response = requests.get(url)

        # Check if the was any errors
        if response.status_code != 200:
            error("Failed to get questions from the API")
            return []

        # Debug
        debug_message(str(response.json()), "API")

        # Check for errors
        match response.json()["response_code"]:
            case 0:
                pass  # No errors, just good to have a defined case so that I don't forget it
            case 1:
                error("No results found")
                if user_data.auto_fix_api:
                    api_fix += 1
                    continue

            case 2:
                error("Invalid parameter")

        # Return the questions
        return response.json()["results"]


def connect_to_server(server_ip: str, port: int) -> socket.socket:
    """
    Connect to a server using a socket

    @param server_ip: The IP of the server (IPV4)
    @param port: The port of the server. Note: use any port higher than 1024 for privileged users
    @return: The socket object
    """

    # Create the socket. AF_INET is ipv4 and SOCK_STREAM is TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect to the server
    sock.connect((server_ip, port))

    # Return the socket
    return sock


def setup_tcp_server(port: int) -> socket.socket:
    """
    Sets up a TCP server

    @param port: The port to listen on
    @return: The socket object
    """

    # Create the socket. AF_INET is ipv4 and SOCK_STREAM is TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the IP adress to bind to
    ip = get_ip()

    # Bind the socket to the port
    sock.bind((ip, port))
    debug_message(f"Bound to {ip}:{port}", "network_server")

    # Start listening
    sock.listen()

    # Dont block the process as we want to be able to accept multiple connections
    sock.setblocking(False)

    # Return the socket
    return sock


def get_ip() -> str:
    """
    Gets the IP of the computer

    @return: The IP of the computer
    """
    return socket.gethostbyname(socket.gethostname())


def test_echo_server():
    class EchoServer(QuizServer):

        def handle_data_received(self, sock, key_data, recv_data: bytes):
            """
            Handle data received from a client

            @param key_data:
            @param recv_data: The data received
            """
            key_data.outb += recv_data

        def handle_data_send(self, sock, key_data, send_data: bytes):
            """
            Handle data sent to a client

            @param key_data:
            @param data: The data sent

            """
            # Get the message from the data
            message = QuizMessage(None, None, None, None)
            message.from_bytes(send_data)

            # Create a QuizMessage object
            message = QuizMessage(message.message, get_ip(), key_data.addr[0], "echo")

            # Send the data
            sent = sock.send(message.to_bytes())

            # Print the data
            print(f"Echoing {message.message} to {key_data.addr}")

            # Remove the data that has been sent from the output buffer
            key_data.outb = key_data.outb[sent:]

    try:
        server = EchoServer(get_ip(), 5000)
        server.run()

    except Exception as e:
        print(f"Error: {e}")


# debug server -echo-client
# debug server -echo-server

def test_echo_client():
    class EchoClient(QuizClient):

        def handle_response(self, sock, key_data, recv_data: bytes):
            """
            Handle a message received from the server

            """
            debug_message(f"Received {recv_data}", "network_client")

            # Convert the response into a message object
            message = QuizMessage(None, None, None, None)
            message.from_bytes(recv_data)

            print(f"Response: {message.message}")

    # Get the IP
    ip = get_ip()

    # Port is 5000 for testing
    port = 5000

    # Create the client
    client = EchoClient(ip, port)

    # Thread the client
    client_thread = threading.Thread(target=client.run)
    client_thread.start()

    client.send_message(client.client, "Hello world", "echo")

    # Loop until the user wants to quit
    while True:
        # Get the message
        message = input("Enter a message to send to the server: ")

        # Check if the user wants to quit
        if message == "quit":
            break

        client.message_queue.append([message, "echo"])


# Note to self: using https://realpython.com/python-sockets/
