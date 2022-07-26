import tkinter as tk
from tkinter import messagebox
import utils
import socket
from cryptography.fernet import Fernet
import os
import game.game as game


class Login:
    def __init__(self):
        self.root: tk.Tk = tk.Tk()
        self.root.title("OpenPongArena - Login")
        photoimage = tk.PhotoImage(file = os.path.join(os.path.dirname(
            __file__), "..", "..", "assets", "icon.png"))
        self.root.iconphoto(False, photoimage)
        self.root.geometry("{}x{}".format(
            utils.WINDOW_WIDTH, utils.WINDOW_HEIGHT))
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.quit)

        self.connected: bool = False
        self.load_config()
        self.bind_socket()

        if self.connected:
            self.check_version()
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
            # recreating the socket because the timeout doesn't allow us to immediately trying to connect again
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
                exit(0)
            except TimeoutError:
                messagebox.showerror(
                     "Error", "Server timed out, trying to connect again in {} seconds.".format(utils.TIMEOUT))
            self.current_tries += 1
            self.connection_label.destroy()

    def check_version(self):
        # send version to server and wait for response
        f = Fernet(utils.get_fernet_key())
        self.sock.send(
            f.encrypt(bytes("--version|{}".format(utils.get_version()), "utf-8")))
        response = f.decrypt(self.sock.recv(1024)).decode("utf-8")
        if response != "--version_OK":
            messagebox.showerror(
                "Error", "The client version is outdated, please update the client.")
            self.quit()

    def init_login_window(self):
        self.login_window = tk.Frame(self.root)
        self.login_window.pack(fill=tk.BOTH, expand=True)

        self.title = tk.Label(
            self.login_window, text="OpenPongArena", font=("Arial", 30))
        self.subtitle = tk.Label(
            self.login_window, text="Login", font=('Arial', 20))
        self.title.pack(fill=tk.X, expand=True, padx=5)
        self.subtitle.pack(fill=tk.BOTH, expand=True, padx=5)

        self.username_entry = tk.Entry(self.login_window)
        self.username_entry.insert(0, "Username")
        self.username_entry.bind('<FocusIn>', lambda event: self.username_entry.delete(
            0, tk.END) if self.username_entry.get() == "Username" else None)
        self.username_entry.bind('<FocusOut>', lambda event: self.username_entry.insert(
            0, "Username") if self.username_entry.get() == "" else None)
        # if enter is pressed, focus on pwd entry
        self.username_entry.bind(
            '<Return>', lambda event: self.password_entry.focus())
        self.username_entry.pack(
            fill=tk.X, expand=True, padx=int(utils.WINDOW_WIDTH / 4))

        self.password_entry = tk.Entry(self.login_window)
        self.password_entry.insert(0, "Password")
        self.password_entry.bind('<FocusIn>', lambda event: self.password_entry.delete(
            0, tk.END) if self.password_entry.get() == "Password" else None)
        self.password_entry.bind('<FocusOut>', lambda event: self.password_entry.insert(
            0, "Password") if self.password_entry.get() == "" else None)
        # if enter is pressed, login
        self.password_entry.bind('<Return>', lambda event: self.login())
        self.password_entry.pack(
            fill=tk.X, expand=True, padx=int(utils.WINDOW_WIDTH / 4))

        self.login_button = tk.Button(
            self.login_window, text="Login", command=self.login)
        self.login_button.pack(fill=tk.X, expand=True,
                               padx=int(utils.WINDOW_WIDTH / 3))

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
            try:
                response = f.decrypt(self.sock.recv(1024)).decode("utf-8")
                response = response.split('|')
                if response[0] == "--login_success":
                    # --login_success|<elo>
                    # start game
                    elo = float(response[1])
                    self.root.destroy()
                    game.Game(username=username, elo=elo, sock=self.sock)
                elif response[0] == "--login_failure":
                    messagebox.showerror(
                        "Error", "Invalid username or password.")
                else:
                    messagebox.showerror("Error", "An unknown error occurred.")
            except TimeoutError:
                messagebox.showerror(
                    "Error", "Server unexpectedly timed out, please try again later...")
                self.quit()

    def quit(self):
        if self.connected:
            f = Fernet(utils.get_fernet_key())
            # --quit
            self.sock.send(f.encrypt(bytes("--quit", "utf-8")))
            self.sock.close()
        self.root.destroy()
        exit(0)
