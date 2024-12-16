import socket
import threading


# Clase del servidor (sin cambios)
class ServerSocket:
    def __init__(self, host="0.0.0.0", port=9999):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_socket = None
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        self.command = None  # Variable para almacenar el comando recibido

    def start_server(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Servidor escuchando en el puerto {self.port}")

        while True:
            self.client_socket, addr = self.server_socket.accept()
            print(f"Conexión aceptada de {addr}")
            threading.Thread(
                target=self.handle_client, args=(self.client_socket,)
            ).start()

    def handle_client(self, client_socket):
        while True:
            try:
                message = client_socket.recv(1024).decode()  # Recibir mensajes
                if message:
                    print(f"Mensaje recibido: {message}")
                    self.command = message  # Almacenar el comando recibido
                    client_socket.send(
                        f"Comando recibido: {message}".encode()
                    )  # Enviar respuesta
                else:
                    print("El cliente cerró la conexión.")
                    break  # Si no hay mensaje, se cierra la conexión
            except Exception as e:
                print(f"Error: {e}")
                break

    def get_command(self):
        return self.command
