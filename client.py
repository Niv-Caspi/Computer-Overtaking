# FINAL CLIENT CODE
import socket
from PIL import ImageGrab
from io import BytesIO

if __name__ == '__main__':
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ("192.168.14.108", 8080)
        print("Starting up on {} port {}".format(*server_address))
        sock.connect(server_address)

        while True:
            screenshot = ImageGrab.grab()
            screenshot_bytes = BytesIO()
            screenshot.save(screenshot_bytes, format="PNG")
            screenshot_bytes = screenshot_bytes.getvalue()  # Use getvalue() to get the bytes
            
            size = len(screenshot_bytes)
            sock.sendall(size.to_bytes(4, byteorder='big'))
            sock.sendall(screenshot_bytes)
    except ConnectionAbortedError:
        print("The established connection has been stopped by the server.")

    sock.close()
