import socket
import rpyc
import threading
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Connect to the RPyC server
conn = rpyc.connect('localhost', 18812)

# Define the client-side implementation of the RPyC service
class GameClient(rpyc.Service):
    def exposed_receive_message(self, message):
        app.display_message(message)

    def exposed_update_game_state(self, game_state):
        app.update_game_state(game_state)

# Start the RPyC client service
client_service = rpyc.ThreadedServer(GameClient, port=0)
threading.Thread(target=client_service.start).start()

# Connect to the socket server
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 9999))

def send_message(message):
    client_socket.send(message.encode('utf-8'))

class ChatApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiplayer Game Chat and Tic-Tac-Toe")
        
        self.username_label = tk.Label(root, text="Username:")
        self.username_label.pack()
        
        self.username_entry = tk.Entry(root)
        self.username_entry.pack()
        
        self.password_label = tk.Label(root, text="Password:")
        self.password_label.pack()
        
        self.password_entry = tk.Entry(root, show="*")
        self.password_entry.pack()
        
        self.login_button = tk.Button(root, text="Login", command=self.login)
        self.login_button.pack()
        
        self.chat_area = scrolledtext.ScrolledText(root, state='disabled')
        self.chat_area.pack()
        
        self.message_entry = tk.Entry(root)
        self.message_entry.pack()
        
        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack()
        
        self.game_buttons = [tk.Button(root, text=" ", font=("Arial", 20), width=5, height=2, command=lambda i=i: self.make_move(i)) for i in range(9)]
        for i in range(3):
            for j in range(3):
                self.game_buttons[i * 3 + j].grid(row=i, column=j)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if conn.root.login(username, password):
            messagebox.showinfo("Login", "Login successful")
            self.username = username
            self.username_entry.config(state='disabled')
            self.password_entry.config(state='disabled')
            self.login_button.config(state='disabled')
            self.update_game_state(conn.root.get_game_state())
        else:
            messagebox.showerror("Login", "Login failed")
    
    def send_message(self):
        message = self.message_entry.get()
        if message:
            send_message(message)
            conn.root.broadcast(self.username, message)
            self.message_entry.delete(0, tk.END)
    
    def display_message(self, message):
        self.chat_area.config(state='normal')
        self.chat_area.insert(tk.END, message + '\n')
        self.chat_area.config(state='disabled')
    
    def make_move(self, position):
        if conn.root.make_move(self.username, position):
            pass
        else:
            messagebox.showwarning("Invalid Move", "This move is not allowed!")

    def update_game_state(self, game_state):
        for i in range(9):
            self.game_buttons[i].config(text=game_state[i])

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()
