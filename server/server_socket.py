import socket
import threading
from data.data_base import DataBase

class ServerSocket:
    """Class to handle server socket communication."""

    def __init__(self, host="0.0.0.0", port=9999):
        """Initialize the server socket.

        Args:
            host (str): The host IP address. Defaults to "0.0.0.0".
            port (int): The port number. Defaults to 9999.
        """
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.command = None
        self.running = True
        self.shared_data = DataBase()
        self.command_callbacks = {}
        self.connection_established = False

        # Start the server in a separate thread
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def start_server(self):
        """Start the server to listen for connections."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server listening on port {self.port}")

        while self.running:
            self.client_socket, addr = self.server_socket.accept()
            self.connection_established = True
            print(f"Connection accepted from {addr}")
            threading.Thread(
                target=self.handle_client,
                args=(self.client_socket,)
            ).start()

    def handle_client(self, client_socket):
        """Handle messages received from the client.

        Args:
            client_socket (socket.socket): The client socket.
        """
        while self.running:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"Message received: {message}")
                    self.command = message
                    self.process_command(message)
                    client_socket.send(f"Command received: {message}".encode())
                else:
                    print("Client closed the connection.")
                    break
            except Exception as e:
                print(f"Error: {e}")
                break
        client_socket.close()
        self.connection_established = False

    def register_callback(self, command: str, callback):
        """Register a callback function for a specific command.

        Args:
            command (str): The command to register the callback for.
            callback (function): The callback function to register.
        """
        self.command_callbacks[command] = callback

    def process_command(self, message: str):
        """Process received commands and execute callbacks.

        Args:
            message (str): The command message to process.
        """
        if message in self.command_callbacks:
            self.command_callbacks[message]()

    def get_command(self):
        """Get the last received command.

        Returns:
            str: The last received command.
        """
        return self.command

    def stop(self):
        """Stop the server."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
