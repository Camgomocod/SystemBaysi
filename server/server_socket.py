import socket
import threading
from data.data_base import DataBase

class ServerSocket:
    def __init__(self, host="0.0.0.0", port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.command = None
        self.running = True
        self.shared_data = DataBase()
        self.command_callbacks = {}
        self.connection_established = False

        # Iniciar el servidor en un thread separado
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def start_server(self):
        """Iniciar el servidor para escuchar conexiones."""
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor escuchando en el puerto {self.port}")

        while self.running:
            self.client_socket, addr = self.server_socket.accept()
            self.connection_established = True
            print(f"Conexión aceptada de {addr}")
            threading.Thread(
                target=self.handle_client,
                args=(self.client_socket,)
            ).start()

    def handle_client(self, client_socket):
        """Manejar mensajes recibidos del cliente."""
        while self.running:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"Mensaje recibido: {message}")
                    self.command = message
                    self.process_command(message)
                    client_socket.send(f"Comando recibido: {message}".encode())
                else:
                    print("El cliente cerró la conexión.")
                    break
            except Exception as e:
                print(f"Error: {e}")
                break
        client_socket.close()
        self.connection_established = False

    def register_callback(self, command: str, callback):
        """Registrar una función callback para un comando específico."""
        self.command_callbacks[command] = callback

    def process_command(self, message: str):
        """Procesar los comandos recibidos y ejecutar callbacks."""
        if message in self.command_callbacks:
            self.command_callbacks[message]()

    def get_command(self):
        """Obtener el último comando recibido."""
        return self.command

    def stop(self):
        """Detener el servidor."""
        self.running = False
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
