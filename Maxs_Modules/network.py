# - - - - - - - Imports - - - - - - -#
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

class Message:
    pass

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
    # USING EXAMPLE FORM https://realpython.com/python-sockets/

    # Create the socket
    sock = setup_tcp_server(5000)

    # Register the socket with the selector
    selector = selectors.DefaultSelector()
    selector.register(sock, selectors.EVENT_READ, data=None)

    try:
        while True:
            # Wait for an event
            events = selector.select(timeout=None)

            # For each event
            for key, mask in events:

                # If the data is None then it is a new connection
                if key.data is None:
                    # Accept the connection
                    connection, address = key.fileobj.accept()

                    # Print the address
                    print(f"Accepted connection from {address}")

                    # Dont block the process as we want to be able to accept multiple connections
                    connection.setblocking(False)

                    # Create the data object
                    data = types.SimpleNamespace(addr=address, inb=b"", outb=b"")

                    # Create the events. They are now read and write so set those bits
                    events = selectors.EVENT_READ | selectors.EVENT_WRITE

                    # Register the connection with the selector
                    selector.register(connection, events, data=data)

                else:
                    sock = key.fileobj
                    data = key.data

                    # If the socket has its read bit set
                    if mask & selectors.EVENT_READ:

                        # Get the data
                        recv_data = sock.recv(1024)

                        # If there is no data then the connection has been closed
                        if recv_data:
                            # Add the data to the output buffer
                            data.outb += recv_data
                        else:

                            # Print the address
                            print(f"Closing connection to {data.addr}")

                            # Unregister the socket from the selector
                            selector.unregister(sock)

                            # Close the socket
                            sock.close()

                    # If the socket has its write bit set
                    if mask & selectors.EVENT_WRITE:

                        # If there is data to send
                        if data.outb:

                            # Print the data
                            print(f"Echoing {data.outb} to {data.addr}")

                            # Send the data
                            sent = sock.send(data.outb)

                            # Remove the data that has been sent from the output buffer
                            data.outb = data.outb[sent:]
    finally:
        selector.close()
def test_echo_client():
    # USING EXAMPLE FORM https://realpython.com/python-sockets/

    # Get the IP
    ip = get_ip()

    # Port is 5000 for testing
    port = 5000

    # Create the socket
    sock = connect_to_server(ip, port)

    # Send the data
    sock.sendall(b"Hello, world")

    # Get the data
    data = sock.recv(1024)

    # Print the data
    print(f"Received {data!r}")

# Note to self: using https://realpython.com/python-sockets/
