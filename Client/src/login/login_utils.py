import tkinter as tk
from tkinter import messagebox
import utils
import socket
from cryptography.fernet import Fernet
from game import Game


class Login:
    def __init__(self):
        self.root: tk.Tk = tk.Tk()
        self.root.title("OpenPongArena - Login")
        #  self.root.iconbitmap(r"..\..\assets\icon.ico")
        self.root.geometry("{}x{}".format(
            utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT))
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.connected: bool = False
        self.load_config()
        self.bind_socket()

        if self.connected:
            self.init_login_window()
            self.root.mainloop()
        else:
            messagebox.showerror(
                "Error", "Could not connect to server, please try again later.")
            self.root.destroy()

    def load_config(self):
        self.server_config = utils.open_environment()['Server']

    def bind_socket(self):
        self.connection_window = tk.Frame(self.root)
        self.connection_window.pack(fill=tk.BOTH, expand=True)
        MAX_TRIES: int = 5
        self.current_tries = 1
        while self.current_tries <= MAX_TRIES and not self.connected:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(utils.TIMEOUT)
            # delete previous connection label if it exists
            self.connection_label = tk.Label(
                self.connection_window, text="Connecting to server... ({}/{})".format(self.current_tries, MAX_TRIES))
            self.connection_label.pack(fill=tk.X, expand=True)
            try:
                self.sock.connect(
                    (self.server_config['IP'], self.server_config['PORT']))
                self.connected = True
            except ConnectionRefusedError:
                messagebox.showerror(
                    "Error", "Could not connect to server, please try again later.")
                break
            except TimeoutError:
                messagebox.showerror(
                    "Error", "Server timed out, trying to connect again in {} seconds.".format(utils.TIMEOUT))
            self.current_tries += 1
            self.connection_label.destroy()

    def init_login_window(self):
        self.login_window = tk.Frame(self.root)
        self.login_window.pack(fill=tk.BOTH, expand=True)

        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.insert(0, "Username")
        self.username_entry.bind('<FocusIn>', lambda event: self.username_entry.delete(
            0, tk.END) if self.username_entry.get() == "Username" else None)
        self.username_entry.bind('<FocusOut>', lambda event: self.username_entry.insert(
            0, "Username") if self.username_entry.get() == "" else None)
        # if enter is pressed, focus on pwd entry
        self.username_entry.bind(
            '<Return>', lambda event: self.password_entry.focus())
        self.username_entry.pack(fill=tk.X, expand=True)

        self.password_entry = tk.Entry(self.login_window)
        self.password_entry.insert(0, "Password")
        self.password_entry.bind('<FocusIn>', lambda event: self.password_entry.delete(
            0, tk.END) if self.password_entry.get() == "Password" else None)
        self.password_entry.bind('<FocusOut>', lambda event: self.password_entry.insert(
            0, "Password") if self.password_entry.get() == "" else None)
        # if enter is pressed, login
        self.password_entry.bind('<Return>', lambda event: self.login())
        self.password_entry.pack(fill=tk.X, expand=True)

        self.login_button = tk.Button(
            self.login_window, text="Login", command=self.login)
        self.login_button.pack(fill=tk.X, expand=True)

    def login(self):
        username: str = self.username_entry.get()
        password: str = self.password_entry.get()

        if username == "Username" and password == "Password":
            messagebox.showerror(
                "Error", "Please enter a valid username and password.")
        elif username == '' and password == '':
            messagebox.showerror(
                "Error", "Please enter a username and password.")
        else:
            # send username and password to server and wait for response
            f = Fernet(utils.get_fernet_key())
            # --login|<username>|<password>
            self.sock.send(
                f.encrypt(bytes("--login|{}|{}".format(username, password), "utf-8")))
            response = f.decrypt(self.sock.recv(1024)).decode("utf-8")
            if response == "--login_success":
                # start game
                self.root.destroy()
                Game(username=username, socket=self.sock)
            elif response == "--login_failure":
                messagebox.showerror("Error", "Invalid username or password.")
            else:
                messagebox.showerror("Error", "An unknown error occurred.")

    def quit(self):
        if self.connected:
            f = Fernet(utils.get_fernet_key())
            # --quit
            self.sock.send(f.encrypt(bytes("--quit"), "utf-8"))
            self.sock.send()
            self.sock.close()
        self.root.destroy()
