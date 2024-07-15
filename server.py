import socket
import threading
import rpyc
from rpyc.utils.server import ThreadedServer

# Define the RPyC service
class GameService(rpyc.Service):
    clients = {}
    credentials = {"user1": "password1", "user2": "password2"}  # Simple username/password store
    game_state = [' ' for _ in range(9)]
    current_turn = 'X'

    def on_connect(self, conn):
        print(f"Client connected: {conn}")

    def on_disconnect(self, conn):
        for user, client_conn in self.clients.items():
            if client_conn == conn:
                del self.clients[user]
                break
        print(f"Client disconnected: {conn}")

    def exposed_login(self, username, password):
        if username in self.credentials and self.credentials[username] == password:
            self.clients[username] = self._conn
            return True
        return False

    def exposed_broadcast(self, username, message):
        if username in self.clients:
            for client_conn in self.clients.values():
                client_conn.root.receive_message(f"{username}: {message}")

    def exposed_get_game_state(self):
        return self.game_state

    def exposed_make_move(self, username, position):
        if username in self.clients:
            if self.game_state[position] == ' ' and self.current_turn == 'X':
                self.game_state[position] = 'X'
                self.current_turn = 'O'
                self.notify_all_clients()
                return True
            elif self.game_state[position] == ' ' and self.current_turn == 'O':
                self.game_state[position] = 'O'
                self.current_turn = 'X'
                self.notify_all_clients()
                return True
        return False

    def notify_all_clients(self):
        for client_conn in self.clients.values():
            client_conn.root.update_game_state(self.game_state)

# Run the RPyC server in a separate thread
def start_rpyc_server():
    server = ThreadedServer(GameService, port=18812)
    server.start()

# Socket server to handle connections
def start_socket_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 9999))
    server_socket.listen(5)
    print("Socket server started on port 9999")

    while True:
        client_socket, addr = server_socket.accept()
        print(f"Connection from {addr}")
        threading.Thread(target=handle_client, args=(client_socket,)).start()

def handle_client(client_socket):
    while True:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break
            print(f"Received: {message}")
            # Handle message or forward to other clients if needed
        except:
            break
    client_socket.close()

if __name__ == "__main__":
    threading.Thread(target=start_rpyc_server).start()
    start_socket_server()
