# - - - - - - - Imports - - - - - - -#
import json
import time
import types

from Maxs_Modules.files import UserData
from Maxs_Modules.tools import install_package
from Maxs_Modules.debug import debug_message, error
from Maxs_Modules.renderer import render_text

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

    def to_bytes(self) -> bytes:
        """
        Creates a JSON object from the attributes of this object and encodes it in utf-8
        @return: The message as bytes (JSON encoded in utf-8)
        """
        obj = {
            "message": self.message,
            "sender": self.sender,
            "recipient": self.recipient,
            "message_type": self.message_type
        }
        debug_message(f"Encoding message: {obj}", "Network")
        return json.dumps(obj, ensure_ascii=False).encode("utf-8")

    def from_bytes(self, data: bytes) -> object:
        """
        Update this objects attributes from the bytes (JSON encoded in utf-8)
        @param data: The data to decode
        @return: This object
        """
        decoded = data.decode("utf-8")
        debug_message(f"Decoded message: {decoded}", "Network")

        obj = json.loads(decoded)
        self.message = obj.get("message")
        self.sender = obj.get("sender")
        self.recipient = obj.get("recipient")
        self.message_type = obj.get("message_type")
        return self


class QuizServer:
    """
    A class to represent a server for the quiz game
    """

    def __init__(self, host: str, port: int):
        """
        Initialise the server, setups a selector and a server socket to listen for connections
        @param host: The host to listen on
        @param port: The port to listen on
        """
        self.host = host
        self.port = port

        self.selector = selectors.DefaultSelector()
        self.clients = []
        self.client_names = []

        self.server = setup_tcp_server(self.port)

        self.selector.register(self.server, selectors.EVENT_READ, data=None)

    def run(self) -> None:
        """
        Loop forever and accept connections or service connections when they are ready
        """
        while True:
            events = self.selector.select(timeout=None)
            for key, mask in events:
                if key.data is None:
                    self.accept_connection(key.fileobj)
                else:
                    self.service_connection(key, mask)

    def accept_connection(self, sock: socket) -> None:
        """
        Accept a connection from a client, saves the client and registers it with the selector. The data (sometimes
        called key_data) is a namespace with the address of the client and the data to send and receive.

        @param sock: The socket to accept the connection from
        """
        # Accept the connection
        connection, address = sock.accept()

        # Print the address
        debug_message(f"Accepted connection from {address}", "network_server")

        # Don't block the process as we want to be able to accept multiple connections
        connection.setblocking(False)

        # Create the data object
        data = types.SimpleNamespace(socket_adress=address, recieved_bytes=b"", send_bytes=b"")

        # Create the events. They are now read and write so set those bits
        events = selectors.EVENT_READ | selectors.EVENT_WRITE

        # Register the connection with the selector
        self.selector.register(connection, events, data=data)

        # Add the connection to the list of clients
        self.clients.append(connection)
        self.client_names.append(address)

    def close_connection(self, sock: socket) -> None:
        """
        Close a connection from a client by removing it from the selector and the list of clients

        @param sock: The socket to close the connection on.
        """

        debug_message(f"Closing connection on {sock}", "network_server")

        # Unregister the socket from the selector
        self.selector.unregister(sock)

        # Close the socket
        sock.close()

        # Remove the socket from the list of clients
        for sock_index in range(len(self.clients)):
            if self.clients[sock_index] == sock:
                # Remove the client and name
                self.clients.pop(sock_index)
                self.client_names.pop(sock_index)
                break

    def service_connection(self, key: object, mask: object) -> None:
        """
        Service a connection from a client. This is called when the client has data to send or is ready to receive
        data. Data is read in 4096 byte chunks so messages shouldnt be sent directly one after another or will cause
        issues on the recving end. Data is then sent to the handle_data_received function. If there is data to send
        then it is sent to the handle_data_send function.

        @param key: The key to the client
        @param mask: The mask to the client
        """

        try:
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
                    debug_message(f"Closing connection on {data.socket_adress}", "network_server")

                    # Close the connection
                    self.close_connection(sock)

            # If the socket has its write bit set
            if mask & selectors.EVENT_WRITE:

                # If there is data to send
                if data.send_bytes:
                    self.handle_data_send(sock, data, data.send_bytes)

        except Exception as e:
            self.handle_error(sock, data, e)

    def handle_data_received(self, sock: socket, key_data: object, recv_data: bytes) -> None:
        """
        Handle data received from a client. This needs to be overridden by a subclass to handle for its use case.

        @param sock:  The socket the data came from.
        @param key_data: The data from the key, contains the address of
        the client, the data to send and the data to receive
        @param recv_data: The data received, can be also gotten from key_data.send_bytes but is passed for convenience
        """

    def handle_data_send(self, sock: socket, key_data: object, send_data: bytes) -> None:
        """
        Handle data sent to a client

        @param key_data: The data from the key
        @param sock: The socket to send the data on
        @param send_data: The data sent
        """

    def send_message(self, sock: socket, message: str, message_type: str) -> None:
        """
        Send a message to the socket specified. The message is wrapped in a QuizMessage object and then sent.

        @param message_type: The type of message to send
        @param sock: The socket to send the message on
        @param message: The message to send
        """
        message = QuizMessage(message, get_ip(), self.host, message_type)
        debug_message(f"Sending...")
        sock.sendall(message.to_bytes())
        debug_message(f"Sent {message}", "network_server")

    def send_message_to_all(self, message: str, message_type: str) -> None:
        """
        Send a message to all clients using the send_message function and  looping through the clients

        @param message_type: The type of message to send
        @param message: The message to send
        """
        for client in self.clients:
            self.send_message(client, message, message_type)

    def kill(self) -> None:
        """
        Kill the server, closing all connections in the clients list and then finally closing the server
        """
        # Close the clients
        for client in self.clients:
            self.close_connection(client)

        # Close the server
        self.close_connection(self.server)

    def handle_error(self, sock: socket, key_data: object, error_response: Exception) -> None:
        """
        Handle an error from the server. This is called when an error occurs in the server. The connection is closed
        on the socket and the error is printed. If the error is a user disconnecting then it is printed as a debug
        message, otherwise it is printed as an error this is because disconnection shouldn't be displayed.

        @param sock: The socket the error occurred on
        @param key_data: The data from the key
        @param error_response: The string representation of the error
        """
        self.close_connection(sock)

        # Check if this is caused by a user disconnecting
        if "An existing connection was forcibly closed by the remote host" in str(error_response):
            debug_message(f"Client disconnected: {key_data.socket_adress}", "network_server")
        else:
            error(f"Error in server: {error_response}")


class QuizClient:
    """
    A class to represent a client for the quiz game
    """

    def __init__(self, host: str, port: int):
        """
        Initialise the client and connect to the server. The selector set and then is used to listen for data from
        the server

        @param host: The host ip to connect to
        @param port: The port to listen on
        """
        self.host = host
        self.port = port

        self.selector = selectors.DefaultSelector()

        self.client = connect_to_server(self.host, self.port)

        self.selector.register(self.client, selectors.EVENT_READ, data=None)

    def run(self) -> None:
        """
        Run the client, listening for data from the server refreshing every second. If there is data then it is read
        at 4096 bytes per chunk and then checked to see if it is a valid json string. If it is then it is sent to the
        handle_data_received function. If there is no data then the connection has been closed and the client is closed.
        """
        try:

            while True:

                events = self.selector.select(timeout=1)

                for key, mask in events:

                    try:
                        sock = key.fileobj
                        data = key.data

                        # If the socket has its read bit set
                        if mask & selectors.EVENT_READ:

                            # Store all the data parts in a list
                            fragments = []
                            recv_data = b''

                            # While there is data to read
                            while True:
                                data = sock.recv(4096)
                                fragments.append(data)
                                recv_data = b''.join(fragments)

                                try:
                                    decoded = recv_data.decode()
                                    json.loads(decoded)
                                    break
                                except ValueError:
                                    # TODO: This is not the best way of doing this as a malicious server could send
                                    #  broken JSON and cause the client to loop forever
                                    continue

                            # If there is no data then the connection has been closed
                            if recv_data:
                                self.handle_data_received(sock, data, recv_data)

                        # If the socket has its write bit set
                        if mask & selectors.EVENT_WRITE:

                            # If there is data to send
                            if data.send_bytes:
                                self.handle_request(sock, data, data.send_bytes)

                    except Exception as e:
                        self.handle_error(sock, data, e)

        # OSErrors thrown here are caused when the socket is being deleted, so can ignore them
        except OSError:
            pass

    def close_connection(self, sock: socket) -> None:
        """
        Close a connection on a socket and unregisters it from the selector, mostly used to close the connection on 
        the server

        @param sock: The socket to close the connection on.
        """
        # Unregister the socket from the selector
        self.selector.unregister(sock)

        # Close the socket
        sock.close()

    def handle_data_received(self, sock: socket, key_data: object, recv_data: bytes) -> None:
        """
        Handle data received from the server. This is called when data is received from the server. Functionality needs
        to be written by the subclass

        @param sock: The socket the data was received on
        @param key_data: The data from the key
        @param recv_data: The data received from the server, same as key_data.receive_bytes but kept for convenience
        """
        pass

    def handle_request(self, sock: socket, key_data: object, send_data: bytes) -> None:
        """
        Handle a request to send data to the server. This is called when data is sent to the server. Functionality needs
        to be written by the subclass

        @param sock: The socket to send the data on
        @param key_data: The data from the key
        @param send_data: The data to send to the server, same as key_data.send_bytes but kept for convenience
        """
        pass

    def handle_error(self, sock: socket, key_data: object, error_response: Exception) -> None:
        """
        Handle an error from the client. This is called when an error occurs in the client. The connection is closed
        and then the exception is printed using the error function

        @param sock: The socket the error occurred on
        @param key_data: The data from the selector key
        @param error_response: The string representation of the error
        """
        self.close_connection(sock)
        error(f"Error in client: {error_response}")

    def send_message(self, sock: object, message: str, message_type: str) -> None:
        """
        Send a message to the server enclosed in a QuizMessage object

        @param message_type: The type of message to send
        @param sock: The socket to send the message on
        @param message: The message to send
        """
        message = QuizMessage(message, get_ip(), self.host, message_type)
        debug_message(f"Sending {message}", "network_client")
        sock.sendall(message.to_bytes())


class QuizGameServer(QuizServer):
    game = None
    running = False
    error = None

    def handle_data_received(self, sock: socket, key_data: object, recv_data: bytes) -> None:
        """
        Handle data received from a client. This function can handle the client_join message type and the sync_player
        message. Both of these actions involve updating the game's users array with the new user data if the request
        was handled without error. Upon handling the messages the server will send a error response to the socket if
        the game is full or has already started or if the username is already taken.  If the game has already started
        then the server will only allow the client to join if they have a name that is already in the game's users
        but not connected, which is treated as a reconnect.

        @param sock: The socket to handle the data from
        @param key_data: The data from the selector key
        @param recv_data: The data received from the client (same as key_data.receive_bytes but kept for convenience)
        """

        # Convert the data to a message
        message = QuizMessage(None, None, None, None)
        message.from_bytes(recv_data)

        # Handle the message
        match message.message_type:
            case "client_join":
                # Check if the game has started
                if self.game.game_started:
                    self.send_message(sock, "Game has already started", "server_error")
                    return

                # Check if the game is full
                if len(self.game.users) >= self.game.max_players:
                    self.send_message(sock, "Game is full", "server_error")
                    return

                # Convert the user to an object
                self.game.users.append(message.message)
                temp_index = len(self.game.users) - 1
                self.game.convert_users()

                is_new_player = True

                # Check if the username is taken
                for user_index in range(len(self.game.users) - 1):

                    # If the username is taken
                    user = self.game.users[user_index]
                    if user.name == self.game.users[temp_index].name:
                        # If the user is taken and connected then the name is taken so send an error
                        if user.is_connected:
                            self.send_message(sock, "Username is taken", "server_error")
                            # Remove the user from the list
                            self.game.users.pop(temp_index)
                            return

                        debug_message(f"Removing index {temp_index}", "network_server")

                        # Remove the user from the list as will use the old one
                        self.game.users.pop(temp_index)
                        temp_index = user_index

                        # This means the server is continuing a game so send the user their progress
                        is_new_player = False
                        self.sync_game()
                        time.sleep(0.5)

                        break

                # If this server is continuing a game then don't allow new players to join
                if is_new_player and self.game.game_loaded:
                    self.send_message(sock,
                                      "Server is continuing game, must rejoin using same name. New players arent allowed",
                                      "server_error")
                    # Remove the user from the list
                    self.game.users.pop(temp_index)
                    return

                self.game.convert_users()

                # Set the sockets name to the user's name
                self.client_names[self.clients.index(sock)] = self.game.users[temp_index].name

                # User is now connected
                self.game.users[temp_index].is_connected = True
                debug_message(f"Player {message.message['name']} has joined the game", "network_server")

            case "sync_player":
                user = message.message

                index = 0

                # Find the user to update
                for user_index in range(len(self.game.users)):
                    if self.game.users[user_index].name == user["name"]:
                        self.game.users[user_index] = user
                        self.game.users[user_index]["is_connected"] = True
                        index = user_index
                        break

                # Convert the users to objects
                self.game.convert_users()
                debug_message(f"Player: {self.game.users[index].name} has synced", "network_server")

            case _:
                debug_message(f"Unhandled message: {message.message}", "network_server")

    def sync_game(self) -> None:
        """
        Sync the game data to all clients. This will send all the game data, so it is best practice to save any
        variables that need to be saved before handling this. As games can be quite large (30kb with 50 questions,
        50 players) this function should be used sparingly, instead send the data that needs to be updated,
        i.e use sync_players when showing the scoreboard.
        """
        # Ensure users have been converted, as timings can be off when networked
        self.game.convert_users()

        # Get the game data
        self.game.prepare_save_data()
        game_data = self.game.save_data

        debug_message(f"Syncing game data: {game_data}", "network_server")

        # Send the game data to all clients
        self.send_message_to_all(game_data, "sync_game")

        # Convert everything back
        self.game.convert_all_from_save_data()

    def sync_players(self) -> None:
        """
        Sync the player data to all clients. This will send all the player data, so it is best practice to save the
        position of the local player before handling this. 
        """
        # Ensure users have been converted, as timings can be off when networked
        self.game.convert_users()

        # Get the game data
        self.game.prepare_save_data()
        players = self.game.save_data["users"]

        debug_message(f"Syncing player data: {players}", "network_server")

        # Send the game data to all clients
        self.send_message_to_all(players, "sync_players")

        # Convert everything back
        self.game.convert_all_from_save_data()

    def sync_bots(self) -> None:
        """
        Sync the bot data to all clients.
        """
        # Ensure bots have been converted, as timings can be off when networked
        self.game.convert_bots()

        # Get the game data
        self.game.prepare_save_data()
        bots = self.game.save_data["bots"]

        debug_message(f"Syncing bot data: {bots}", "network_server")

        # Send the game data to all clients
        self.send_message_to_all(bots, "sync_bots")

        # Convert everything back
        self.game.convert_all_from_save_data()

    def handle_error(self, sock: socket, key_data: object, error_response: Exception) -> None:
        """
        Handle an error from a client and then close the client. Uses the super class to handle the error and then sets
        the running variable to false

        @param sock: The socket that the error occurred on
        @param key_data: The key data for the socket
        @param error_response: The exception that was raised that caused the error
        """
        super().handle_error(sock, key_data, error_response)
        self.running = False

    def close_connection(self, sock: socket) -> None:
        """
        Close a connection from a client by removing it from the selector and the list of clients. The user is also
        removed from the games list of players.

        @param sock: The socket to close the connection on.
        """

        debug_message(f"Closing connection on {sock}", "network_server")

        # Unregister the socket from the selector
        self.selector.unregister(sock)

        # Close the socket
        sock.close()

        # Remove the socket from the list of clients
        # Remove the player from the game
        for sock_index in range(len(self.clients)):
            if self.clients[sock_index] == sock:
                for user_index in range(len(self.game.users)):
                    if self.game.users[user_index].name == self.client_names[sock_index]:
                        self.game.users.pop(user_index)
                        break

                # Remove the client and name
                self.clients.pop(sock_index)
                self.client_names.pop(sock_index)
                break


class QuizGameClient(QuizClient):
    game = None
    running = False
    error = None
    server = None
    move_on = False

    def __init__(self, host: str, port: int):
        super().__init__(host, port)

    def handle_data_received(self, sock: socket, key_data: object, recv_data: bytes) -> None:
        """
        Handle data received from the server. The message is converted to a QuizMessage object and then handled,
        the types that can be handled are: server_error, move_on, sync_game, sync_players, sync_bots. Server error
        will cause the client to close, move on will exit the wait_for_move_on()'s loop, sync_game will sync the game
        data, sync_players will sync the player data and sync_bots will sync the bot data.

        @param sock: The socket to handle the data from
        @param key_data: The key data for the socket's selector
        @param recv_data: The data received from the server as bytes (the same as key_data.receive_bytes but kept for
        convenience)
        """
        self.server = sock

        # Convert the data to a message
        message = QuizMessage(None, None, None, None)
        message.from_bytes(recv_data)

        # Handle the message
        match message.message_type:
            case "server_error":
                self.error = f"Server error: {message.message}"
                self.close_connection(sock)
                self.running = False

            case "move_on":
                self.move_on = True

            case "sync_game":
                self.game.save_data = message.message
                # Load the save data into variables
                self.game.load_from_saved()

                # Set the default settings if the settings are none
                self.game.set_settings_default()

                # Convert everything back
                self.game.convert_all_from_save_data()

                # Ensure that the joined_game flag is not lost
                self.game.joined_game = True

                # Make sure the user playing is the local user and not the synced one
                for user_index in range(len(self.game.users)):
                    if self.game.users[user_index].name == self.game.current_user_playing_net_name:
                        self.game.current_user_playing = user_index

            case "sync_players":
                synced_users = message.message

                self.game.users = synced_users

                self.game.convert_users()
                for user in self.game.users:
                    debug_message(f"Player: {user.name} has synced with a score of {user.points}")

                # Make sure the user playing is the local user and not the synced one
                for user_index in range(len(self.game.users)):
                    if self.game.users[user_index].name == self.game.current_user_playing_net_name:
                        self.game.current_user_playing = user_index

            case "sync_bots":
                synced_bots = message.message
                for bot_index in range(len(synced_bots)):
                    self.game.bots[bot_index] = synced_bots[bot_index]
                self.game.convert_bots()

            case _:
                debug_message(f"Unhandled message: {message.message}", "network_client")

    def handle_error(self, sock: socket, key_data: object, error_response: Exception) -> None:
        """
        Handle an error from the server, close the connection and set the running variable to false. If the error
        message was that the connection was closed by the host then it is rephrased as "Server Closed" for readability.

        @param sock: The socket to handle the error from
        @param key_data: The key data for the socket
        @param error_response: The error response
        """
        self.close_connection(sock)

        error_response = str(error_response)

        # Make errors more readable
        if "An existing connection was forcibly closed by the remote host" in error_response:
            error_response = "Server Closed"

        self.error = error_response
        self.running = False

    def send_self(self):
        """
        Send the local user to the server
        """
        # Convert the users to a dict
        self.game.prepare_save_data()

        # Get the user data
        user_data = self.game.save_data["users"][self.game.current_user_playing]

        # Send the user data to the server
        self.send_message(self.server, user_data, "sync_player")

        # Convert everything back
        self.game.convert_all_from_save_data()

    def wait_for_move_on(self):
        """
        Wait for the move on flag to be set (this is set when receiving the move on message from the server)
        """
        self.move_on = False
        while not self.move_on and self.running:
            pass


# - - - - - - - Functions - - - - - - -#


def api_get_questions(amount: int, category: int, difficulty: str, question_type: str) -> list:
    """
    Gets questions from the API at https://opentdb.com/api.php and returns them as a list of dictionaries

    @param amount: How many questions to get (Max 50)
    @param category: The category of the questions (index, offset by 9)
    @param difficulty: The difficulty of the questions
    @param question_type: The type of the questions
    @return: A list of dictionaries containing the questions
    """

    # Get the setup data

    try:
        import requests
    except ImportError:
        install_package("requests")
        import requests

    redo = True
    api_fix = 0

    user_data = UserData()

    while redo:

        # Create the URL
        url = f"https://opentdb.com/api.php?amount={amount}"

        # Ignore the options if they are "Any" (or none because 'convert_question_settings_to_api' already does this)
        # since the API gives any by default

        if question_type is not None and api_fix < 1:
            url += f"&type={question_type}"

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
                    render_text("Auto fixing API error...")
                    api_fix += 1
                    continue

            case 2:
                error("Invalid parameter")

        # Return the questions
        return response.json()["results"]


def connect_to_server(server_ip: str, port: int) -> socket.socket:
    """
    Connect to a server using a socket

    @param server_ip: The IP of the server (IPv4)
    @param port: The port of the server. Note: use any port higher than 1024 for un-privileged users
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
    Sets up a TCP server on the local machine.

    @param port: The port to listen on
    @return: The socket object
    """

    # Create the socket. AF_INET is ipv4 and SOCK_STREAM is TCP
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Get the IP address to bind to
    ip = get_ip()

    # Bind the socket to the port
    sock.bind((ip, port))
    debug_message(f"Bound to {ip}:{port}", "network_server")

    # Start listening
    sock.listen()

    # Don't block the process as we want to be able to accept multiple connections
    sock.setblocking(False)

    # Return the socket
    return sock


def get_ip() -> str:
    """
    Gets the IP of the computer using the socket library

    @return: The IP of the computer
    """
    return socket.gethostbyname(socket.gethostname())
